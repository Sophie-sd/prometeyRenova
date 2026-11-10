"""Кабінет КП клієнта: жодного англійського рядка інтерфейсу, «Сайт» прихований,
під «Категорія» видно «+ Додати категорію»."""
import re
from html import unescape

from django.core.management import call_command
from django.test import Client, TestCase
from django.utils.translation import trans_real

from apps.democorp.services.provision import provision_demo_corp
from apps.democorp.tests.test_admin_ux import _proposal

# Англійські рядки Unfold/Django, які клієнт бачив у кабінеті 10.11.2026.
ENGLISH = (
    'Select value', 'Type to search', 'Select action', 'Select record', 'Run',
    'Search apps and models', 'Choose file to upload', 'Available shortcuts',
    'Global shortcuts', 'Toggle sidebar', 'Toggle filter', 'Create new record',
    'Open selection', 'Open command tool', 'Changelist shortcuts', 'Navigate',
    'Light', 'Dark', 'System', 'True', 'False', 'Slug', 'SEO title', 'SEO description',
)

PAGES = (
    '', 'democorp/corpblock/',
    'democorp/corpcategory/', 'democorp/corpcategory/add/',
    'democorp/corpproduct/', 'democorp/corpproduct/add/',
    'democorp/corpgalleryimage/', 'democorp/corpgalleryimage/add/',
    'democorp/corpproductionstep/', 'democorp/corpproductionstep/add/',
    'democorp/corptestimonial/', 'democorp/corptestimonial/add/',
    'democorp/corppartner/', 'democorp/corppartner/add/',
    'democorp/corplead/', 'password_change/',
)


def _ui_texts(html):
    """Видимий текст і підписи (placeholder/title/aria-label), без script/style."""
    body = re.sub(r'<(script|style|template)\b.*?</\1>', '', html, flags=re.S)
    texts = re.findall(r'>([^<>]+)<', body)
    texts += re.findall(r'(?:placeholder|title|aria-label)="([^"]+)"', body)
    return [unescape(t).strip() for t in texts if t.strip()]


class CorpAdminUkrainianTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command('compilemessages', locale=['uk'], ignore=['prometey_env', '.venv'], verbosity=0)
        # .mo щойно зібрано (як у build.sh) — перечитати каталоги перекладів.
        trans_real._translations = {}
        trans_real._default = None

    def setUp(self):
        self.site = provision_demo_corp(_proposal())
        self.client = Client(HTTP_ACCEPT_LANGUAGE='uk')
        self.client.force_login(self.site.owner_user)

    def _url(self, suffix):
        return self.site.get_console_path().rstrip('/') + '/' + suffix

    def test_no_english_ui_on_client_pages(self):
        found = {}
        for page in PAGES:
            response = self.client.get(self._url(page))
            self.assertEqual(response.status_code, 200, page)
            texts = _ui_texts(response.content.decode())
            # template-теги Unfold (гарячі клавіші, меню) теж мають бути українські
            texts += _ui_texts(re.sub(r'</?template\b[^>]*>', '', response.content.decode()))
            hits = sorted({w for w in ENGLISH for t in texts if t == w or t.startswith(w + ' ')
                           or t.startswith(w + '.')})
            if hits:
                found[page or 'home'] = hits
        self.maxDiff = None
        self.assertEqual(found, {})

    def test_product_form_hides_site_and_shows_add_category(self):
        html = self.client.get(self._url('democorp/corpproduct/add/')).content.decode()
        self.assertNotIn('name="tenant"', html)
        self.assertNotIn('<select name="tenant"', html)
        self.assertNotIn('for="id_tenant"', html)
        self.assertIn('data-dc-add-category="1"', html)
        self.assertIn('+ Додати категорію', html)
        self.assertIn('democorp/corpcategory/add/', html)
        self.assertIn('democorp/js/admin_category_add.js', html)

    def test_client_adds_product_without_choosing_site(self):
        category = self.site.categories.first()
        response = self.client.post(self._url('democorp/corpproduct/add/'), {
            'category': category.pk, 'name': 'Новий приклад',
            'slug': 'novyi-pryklad', 'order': 0, 'is_active': 'on',
            'images-TOTAL_FORMS': 0, 'images-INITIAL_FORMS': 0,
            'images-MIN_NUM_FORMS': 0, 'images-MAX_NUM_FORMS': 1000,
        })
        self.assertEqual(response.status_code, 302, response.content.decode()[:3000])
        self.assertTrue(self.site.products.filter(name='Новий приклад').exists())

    def test_duplicate_slug_in_own_site_is_form_error_not_crash(self):
        existing = self.site.products.first()
        response = self.client.post(self._url('democorp/corpproduct/add/'), {
            'category': existing.category_id, 'name': 'Дубль', 'slug': existing.slug, 'order': 0,
            'images-TOTAL_FORMS': 0, 'images-INITIAL_FORMS': 0,
            'images-MIN_NUM_FORMS': 0, 'images-MAX_NUM_FORMS': 1000,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.site.products.filter(name='Дубль').exists())
