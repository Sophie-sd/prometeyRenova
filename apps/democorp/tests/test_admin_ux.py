"""Кабінет КП: унікальні категорії у select і збереження фото/фону."""
import io
import tempfile
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from PIL import Image

from apps.core.proposal_models import Proposal
from apps.democorp.content_models import CorpBlock
from apps.democorp.services.provision import provision_demo_corp

TMP_MEDIA = Path(tempfile.mkdtemp(prefix='democorp-admin-ux-'))


def _png(color):
    buffer = io.BytesIO()
    Image.new('RGB', (8, 8), color).save(buffer, format='PNG')
    return buffer.getvalue()


def _proposal(**overrides):
    defaults = {
        'slug': 'corp-ux-a',
        'client_name': 'UX Client',
        'title': 'UX KP',
        'issued_on': date(2026, 11, 10),
        'is_published': True,
        'kind': Proposal.DemoKind.CORPORATE,
        'corp_catalog': True,
    }
    defaults.update(overrides)
    return Proposal.objects.create(**defaults)


class _SelectOptions(HTMLParser):
    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name
        self.in_target = False
        self.options = []
        self._opt = None

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag == 'select' and self.class_name in ad.get('class', '').split():
            self.in_target = True
            self.options = []
        elif self.in_target and tag == 'option':
            self._opt = {'value': ad.get('value', ''), 'text': ''}

    def handle_endtag(self, tag):
        if tag == 'option' and self._opt is not None:
            self.options.append(self._opt)
            self._opt = None
        elif tag == 'select':
            self.in_target = False

    def handle_data(self, data):
        if self._opt is not None:
            self._opt['text'] += data


class _FormFields(HTMLParser):
    def __init__(self):
        super().__init__()
        self.fields = {}
        self._ta = None
        self._buf = []
        self._sel = None
        self._sel_picked = False

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag == 'textarea':
            self._ta = ad.get('name')
            self._buf = []
            return
        if tag == 'select':
            self._sel = ad.get('name')
            self._sel_picked = False
            return
        if tag == 'option' and self._sel:
            picked = 'selected' in ad
            if picked or not self._sel_picked:
                self.fields[self._sel] = ad.get('value', '')
                if picked:
                    self._sel_picked = True
            return
        if tag != 'input':
            return
        name = ad.get('name')
        if not name or ad.get('type') in ('file', 'submit', 'button'):
            return
        if ad.get('type') == 'checkbox':
            if 'checked' in ad:
                self.fields[name] = ad.get('value', 'on')
            return
        self.fields[name] = ad.get('value', '')

    def handle_endtag(self, tag):
        if tag == 'textarea' and self._ta:
            self.fields[self._ta] = ''.join(self._buf)
            self._ta = None
        elif tag == 'select':
            self._sel = None
            self._sel_picked = False

    def handle_data(self, data):
        if self._ta:
            self._buf.append(data)


@override_settings(MEDIA_ROOT=str(TMP_MEDIA))
class CorpAdminUxTests(TestCase):
    def setUp(self):
        self.site = provision_demo_corp(_proposal())
        self.other = provision_demo_corp(_proposal(
            slug='corp-ux-b', client_name='Other UX',
        ))
        self.client = Client()
        self.client.force_login(self.site.owner_user)

    def _url(self, site, suffix):
        return site.get_console_path().rstrip('/') + '/' + suffix.lstrip('/')

    def test_category_filter_is_unique_dropdown_and_filters(self):
        response = self.client.get(self._url(self.site, 'democorp/corpproduct/'))
        self.assertEqual(response.status_code, 200)
        parser = _SelectOptions('dc-cat-filter__select')
        parser.feed(response.content.decode())
        labels = [item['text'].strip() for item in parser.options]
        values = [item['value'] for item in parser.options]
        self.assertIn('Всі', labels)
        self.assertEqual(len(labels), len(set(labels)))
        self.assertEqual(len(values), len(set(values)))
        self.assertEqual(labels.count('Компанії'), 1)
        self.assertEqual(labels.count('Послуги'), 1)
        self.assertEqual(labels.count('Виробництво'), 1)
        self.assertEqual(labels.count('Запис і освіта'), 1)
        other_pk = str(self.other.categories.get(name='Компанії').pk)
        self.assertFalse(any(f'category__id__exact={other_pk}' in value for value in values))

        services = self.site.categories.get(name='Послуги')
        in_cat = list(self.site.products.filter(category=services).values_list('name', flat=True))
        out_cat = list(self.site.products.exclude(category=services).values_list('name', flat=True))
        self.assertTrue(in_cat)
        filtered = self.client.get(
            self._url(self.site, f'democorp/corpproduct/?category__id__exact={services.pk}'),
        )
        for name in in_cat:
            self.assertContains(filtered, name)
        for name in out_cat:
            if name not in in_cat:
                self.assertNotContains(filtered, name)

    def test_photo_and_background_save(self):
        url = self._url(self.site, 'democorp/corpblock/')
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        html = page.content.decode()
        self.assertIn('Змінити фото', html)
        self.assertIn('Змінити фон', html)
        self.assertIn('about__photo', html)
        self.assertIn('name="hero_image"', html)
        self.assertIn('name="color_surface"', html)

        fields = _FormFields()
        fields.feed(html)
        fields.fields['color_surface'] = '#112233'
        fields.fields['hero_image'] = SimpleUploadedFile(
            'hero-new.png', _png((20, 40, 60)), content_type='image/png',
        )
        fields.fields['about__photo'] = SimpleUploadedFile(
            'about-new.png', _png((60, 20, 40)), content_type='image/png',
        )
        saved = self.client.post(url, fields.fields, follow=True)
        self.assertContains(saved, 'Сайт оновлено')

        self.site.refresh_from_db()
        self.assertEqual(self.site.color_surface.lower(), '#112233')
        self.assertIn('hero-new', self.site.hero_image.name)
        photo = CorpBlock.objects.get(tenant=self.site, page='about', key='photo')
        self.assertIn('about-new', photo.value_image.name)
