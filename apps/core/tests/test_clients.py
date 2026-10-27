import re
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client as DjangoTestClient, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from apps.core.home_clients_data import HOME_CLIENTS
from apps.core.management.commands.seed_clients import is_legacy_seed_logo
from apps.core.mixins import homepage_clients
from apps.core.models import Client
from apps.core.portfolio_images import resolve_client_logo_srcset, resolve_client_logo_url

EXCLUDED_DOMAINS = ('auto-lot.online', 'alexmodul', 'maisonpolina')

MINIMAL_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00'
    b'\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


def make_client(name, order=0, is_active=True):
    logo = SimpleUploadedFile(f'{name.lower()}.png', MINIMAL_PNG, content_type='image/png')
    return Client.objects.create(
        name=name,
        logo=logo,
        order=order,
        is_active=is_active,
    )


class ClientLogoResolutionTests(SimpleTestCase):
    @override_settings(MEDIA_ROOT='/tmp/prometey-empty-media-test')
    def test_static_logo_when_no_upload_on_disk(self):
        client = Client(name='Play Vision', logo_static='images/clients/playvision.webp')
        client.logo.name = 'clients/playvision_missing.png'
        self.assertIn('/static/images/clients/playvision.webp', resolve_client_logo_url(client))
        srcset = resolve_client_logo_srcset(client)
        self.assertIn('playvision-128.webp 128w', srcset)
        self.assertIn('playvision.webp 256w', srcset)

    def test_admin_upload_wins_over_static(self):
        with tempfile.TemporaryDirectory() as media:
            (Path(media) / 'clients').mkdir()
            (Path(media) / 'clients' / 'new-logo.png').write_bytes(MINIMAL_PNG)
            with override_settings(MEDIA_ROOT=media):
                client = Client(name='Play Vision', logo_static='images/clients/playvision.webp')
                client.logo.name = 'clients/new-logo.png'
                self.assertEqual(resolve_client_logo_url(client), '/media/clients/new-logo.png')
                self.assertEqual(resolve_client_logo_srcset(client), '')

    def test_no_name_based_override_left(self):
        client = Client(name='BeautyShop')
        self.assertEqual(client.get_logo_url(), '')

    def test_alt_per_language_and_override(self):
        client = Client(name='ФПУ')
        with translation.override('uk'):
            self.assertEqual(client.get_logo_alt(), 'ФПУ — сайт від PrometeyLabs')
        with translation.override('ru'):
            self.assertEqual(client.get_logo_alt(), 'ФПУ — сайт от PrometeyLabs')
        client.logo_alt = 'Custom'
        self.assertEqual(client.get_logo_alt(), 'Custom')


class ClientsMarqueeSpeedTests(SimpleTestCase):
    """Old 9-logo strip ran one set per 40s; keep that px/s with any number of clients."""

    def test_js_scales_duration_per_item_and_starts_on_any_intersection(self):
        for rel in ('static/js/components/clients-marquee.js', 'static/js/corporate-website-v2.js'):
            with self.subTest(js=rel):
                js = (Path(settings.BASE_DIR) / rel).read_text(encoding='utf-8')
                self.assertIn('var SECONDS_PER_ITEM = 40 / 9;', js)
                self.assertIn("'--marquee-duration'", js)
                # Стрічка з 33 кіл ширша за мобільний в'юпорт у ~8 разів: 10% площі не досягається.
                self.assertIn("{ threshold: 0, rootMargin: '50px' }", js)
                self.assertNotIn("{ threshold: 0.1, rootMargin: '50px' }", js)
                self.assertIn('story-clone', js)
                self.assertIn("img.loading = 'eager'", js)


class HomeClientsDataTests(SimpleTestCase):
    def test_list_size_unique_https_and_logo_files(self):
        self.assertGreaterEqual(len(HOME_CLIENTS), 20)
        self.assertLessEqual(len(HOME_CLIENTS), 35)
        self.assertEqual(len({c['name'] for c in HOME_CLIENTS}), len(HOME_CLIENTS))
        static_root = Path(settings.BASE_DIR) / 'static'
        for item in HOME_CLIENTS:
            with self.subTest(client=item['name']):
                self.assertTrue(item['site_url'].startswith('https://'))
                self.assertFalse(any(d in item['site_url'] for d in EXCLUDED_DOMAINS))
                self.assertTrue((static_root / item['logo_static']).is_file())
                self.assertTrue((static_root / item['logo_static'].replace('.webp', '-128.webp')).is_file())

    def test_every_client_site_is_in_portfolio(self):
        from apps.core.portfolio_seed_data import PORTFOLIO_PROJECTS

        def host(url):
            return re.sub(r'^https?://(www\.)?', '', url).split('/')[0]

        portfolio_hosts = {host(p['site_url']) for p in PORTFOLIO_PROJECTS if p.get('site_url')}
        portfolio_hosts.add('airinua.com')  # PROJECTS_MAP.md (Render), old homepage logo
        for item in HOME_CLIENTS:
            with self.subTest(client=item['name']):
                self.assertIn(host(item['site_url']), portfolio_hosts)


class SeedClientsTests(TestCase):
    def setUp(self):
        Client.objects.all().delete()

    def test_seed_replaces_legacy_rows_idempotently(self):
        legacy = make_client('Coresync', order=0)
        play = make_client('Play Vision', order=2)
        play.logo.name = 'clients/playvision_Ab12Cd3.png'
        play.save()
        admin_added = Client.objects.create(name='Admin Added', site_url='https://example.com/')

        call_command('seed_clients', verbosity=0)
        call_command('seed_clients', verbosity=0)

        legacy.refresh_from_db()
        play.refresh_from_db()
        admin_added.refresh_from_db()
        self.assertFalse(legacy.is_active)
        self.assertTrue(admin_added.is_active)
        self.assertTrue(play.is_active)
        self.assertEqual(play.site_url, 'https://playvision.com.ua/')
        self.assertEqual(play.logo.name, '')
        self.assertEqual(Client.objects.filter(name='Play Vision').count(), 1)
        active = list(homepage_clients().exclude(name='Admin Added').values_list('name', flat=True))
        self.assertEqual(active, [c['name'] for c in HOME_CLIENTS])

    def test_legacy_logo_detection(self):
        self.assertTrue(is_legacy_seed_logo('clients/playvision.png'))
        self.assertTrue(is_legacy_seed_logo('clients/pulvas_store_Xy12Ab3.png'))
        self.assertFalse(is_legacy_seed_logo('clients/fpsu-new.webp'))
        self.assertFalse(is_legacy_seed_logo(''))


class HomepageClientsTests(TestCase):
    def setUp(self):
        # seed_clients may already have filled the table (build/start); these tests need a clean one.
        Client.objects.all().delete()

    def test_homepage_clients_returns_only_active_in_order(self):
        make_client('Alpha', order=2)
        make_client('Beta', order=1)
        make_client('Hidden', order=0, is_active=False)

        clients = list(homepage_clients())
        self.assertEqual([client.name for client in clients], ['Beta', 'Alpha'])

    def test_home_view_includes_home_clients(self):
        make_client('Play Vision', order=0)

        response = DjangoTestClient().get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('home_clients', response.context)
        self.assertEqual(
            [client.name for client in response.context['home_clients']],
            ['Play Vision'],
        )

    def test_home_page_renders_active_client_names(self):
        make_client('BeautyShop', order=0)

        response = DjangoTestClient().get(reverse('home'))
        self.assertContains(response, 'BeautyShop')

    def test_inactive_client_not_rendered(self):
        make_client('Visible Client', order=0, is_active=True)
        make_client('Hidden Client', order=1, is_active=False)

        response = DjangoTestClient().get(reverse('home'))
        self.assertContains(response, 'Visible Client')
        self.assertNotContains(response, 'Hidden Client')


class ClientAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin-pass-123',
        )
        self.client = DjangoTestClient()
        self.client.force_login(self.admin_user)

    def test_admin_changelist_accessible(self):
        response = self.client.get(reverse('admin:core_client_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_admin_add_form_accessible(self):
        response = self.client.get(reverse('admin:core_client_add'))
        self.assertEqual(response.status_code, 200)


class ShopV2MarkupTests(SimpleTestCase):
    def _client(self):
        return Client(
            name='Play Vision',
            site_url='https://playvision.com.ua/',
            logo_static='images/clients/playvision.webp',
        )

    def test_client_story_links_to_client_site(self):
        from django.template.loader import render_to_string

        with translation.override('uk'):
            html = render_to_string(
                'components/client_home_story.html',
                {'client': self._client(), 'is_clone': False},
            )
        self.assertIn('class="project-story-wrap" role="listitem"', html)
        self.assertIn('href="https://playvision.com.ua/" target="_blank" rel="noopener"', html)
        self.assertNotIn('nofollow', html)
        self.assertIn('alt="Play Vision — сайт від PrometeyLabs"', html)
        self.assertIn('playvision-128.webp 128w', html)
        self.assertIn('width="256" height="256" loading="lazy" decoding="async"', html)
        self.assertNotIn('tabindex', html)

    def test_clone_is_hidden_from_a11y_and_tab_order(self):
        from django.template.loader import render_to_string

        clone = render_to_string(
            'components/client_home_story.html',
            {'client': self._client(), 'is_clone': True},
        )
        self.assertIn('aria-hidden="true"', clone)
        self.assertIn('tabindex="-1"', clone)
        self.assertIn('alt=""', clone)
        self.assertNotIn('role="listitem"', clone)

    def test_marquee_is_clickable(self):
        css = (Path(settings.BASE_DIR) / 'static/css/components/clients-marquee.css').read_text()
        rule = css.split('[data-clients-marquee] {', 1)[1].split('}', 1)[0]
        self.assertNotIn('pointer-events', rule)
        self.assertIn(':has(.project-story:focus-visible)', css)
        self.assertIn('@media (hover: hover) and (pointer: fine)', css)
        self.assertIn('var(--marquee-duration, 40s)', css)
        self.assertIn('prefers-reduced-motion', css)
        corp = (Path(settings.BASE_DIR) / 'static/css/corporate-website-v2.css').read_text()
        self.assertIn('pl-corp-marquee var(--marquee-duration, 40s)', corp)
        shop = (Path(settings.BASE_DIR) / 'static/css/internet-shop-v2.css').read_text()
        rule = shop.split('.pl-shop__clients-stories-container {', 1)[1].split('}', 1)[0]
        self.assertNotIn('pointer-events', rule)

    def test_internet_shop_v2_template_self_hosts_fonts(self):
        page = (Path(settings.BASE_DIR) / 'templates/pages/internet-shop-v2.html').read_text()
        self.assertIn('fonts/v2/inter-latin.woff2', page)
        self.assertNotIn('fonts.googleapis.com', page)
        self.assertNotIn('imagesrcset', page)
        self.assertNotIn('internet-shop-v2-anim.css', page)
        js = (Path(settings.BASE_DIR) / 'static/js/internet-shop-v2.js').read_text()
        self.assertNotIn("setAttribute('role', 'marquee')", js)
