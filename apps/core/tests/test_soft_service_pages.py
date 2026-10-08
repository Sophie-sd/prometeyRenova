"""Soft tiles → service landings; new slugs /rozrobka-lendingu/, /rozrobka-veb-platform/; CMS tabs; screen scroll."""
import re
from decimal import Decimal

from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import translation

from apps.core.fx_models import ExchangeRateSettings
from apps.core.sitemaps import StaticViewSitemap

TILE_HREF_RE = re.compile(r'class="pl-rs__product[^"]*" href="([^"]+)"')

EXPECTED_TILES_UK = [
    '/rozrobka-lendingu/',
    '/corporate-website-v2/',
    '/internet-shop-v2/',
    '/rozrobka-veb-platform/',
    '/telegram-bot/',
]


def _rates():
    ExchangeRateSettings.objects.update_or_create(
        pk=1,
        defaults={
            'uah_per_eur': Decimal('40'),
            'usd_per_eur': Decimal('1.085'),
            'czk_per_eur': Decimal('25'),
        },
    )


class SoftTileLinksTests(TestCase):
    def setUp(self):
        _rates()

    def test_uk_tiles_map_to_service_pages(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertEqual(TILE_HREF_RE.findall(html), EXPECTED_TILES_UK)

    def test_ru_tiles_keep_ru_prefix(self):
        html = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        self.assertEqual(TILE_HREF_RE.findall(html), ['/ru' + h for h in EXPECTED_TILES_UK])

    def test_every_tile_href_resolves_and_returns_200(self):
        for prefix in ('', '/ru'):
            html = self.client.get(f'{prefix}/rozrobka-sajtiv/').content.decode()
            hrefs = TILE_HREF_RE.findall(html)
            self.assertEqual(len(hrefs), 5)
            self.assertEqual(len(set(hrefs)), 5, 'two tiles point to the same page')
            for href in hrefs:
                with self.subTest(href=href):
                    resolve(href)
                    response = self.client.get(href)
                    self.assertEqual(response.status_code, 200)


class SoftServicePagesTests(TestCase):
    PAGES = {
        'rozrobka_lendingu': {
            'path': '/rozrobka-lendingu/',
            'h1_uk': 'Розробка лендінгу під ключ',
            'h1_ru': 'Разработка лендинга под ключ',
            'range': '250–400 €',
            'days': '3–7 днів',
        },
        'rozrobka_veb_platform': {
            'path': '/rozrobka-veb-platform/',
            'h1_uk': 'Розробка веб-платформ під ключ',
            'h1_ru': 'Разработка веб-платформ под ключ',
            'range': '1\u00a0500–5\u00a0000 €',
            'days': '14–30 днів',
        },
    }

    def setUp(self):
        _rates()

    def test_reverse_and_200_uk_ru_en(self):
        for name, cfg in self.PAGES.items():
            with translation.override('uk'):
                self.assertEqual(reverse(name), cfg['path'])
            for prefix in ('', '/ru', '/en'):
                with self.subTest(page=name, prefix=prefix):
                    response = self.client.get(prefix + cfg['path'])
                    self.assertEqual(response.status_code, 200)

    def test_uk_message_match_and_single_h1(self):
        for name, cfg in self.PAGES.items():
            with self.subTest(page=name):
                html = self.client.get(cfg['path']).content.decode()
                self.assertEqual(html.count('<h1'), 1)
                self.assertIn(f'>{cfg["h1_uk"]}</h1>', html)
                title = re.search(r'<title>(.*?)</title>', html, re.S).group(1)
                self.assertIn(cfg['h1_uk'], title)
                self.assertIn(cfg['range'], html)
                self.assertIn(cfg['days'], html)
                self.assertIn('data-modal="call-request-modal"', html)
                self.assertIn('Отримати консультацію', html)
                self.assertIn('id="fx-switch-soft"', html)
                self.assertIn(
                    f'rel="canonical" href="https://www.prometeylabs.com{cfg["path"]}"', html
                )
                self.assertIn('hreflang="ru"', html)
                self.assertIn('application/ld+json', html)
                self.assertIn('data-pl-rs-cms', html)
                self.assertIn('pl-rs__siblings', html)
                self.assertNotIn('Чотири орієнтири', html)

    def test_ru_page_translated(self):
        for name, cfg in self.PAGES.items():
            with self.subTest(page=name):
                html = self.client.get('/ru' + cfg['path']).content.decode()
                self.assertIn(f'>{cfg["h1_ru"]}</h1>', html)
                self.assertIn('Получить консультацию', html)
                self.assertIn(
                    f'rel="canonical" href="https://www.prometeylabs.com/ru{cfg["path"]}"', html
                )
                self.assertIn('href="/ru/rozrobka-sajtiv/"', html)

    def test_in_sitemap(self):
        for name, cfg in self.PAGES.items():
            self.assertIn(name, StaticViewSitemap.PAGES)
        body = self.client.get('/sitemap.xml').content.decode()
        for cfg in self.PAGES.values():
            self.assertIn(cfg['path'], body)


class SoftCmsTabsAndScreensTests(TestCase):
    def setUp(self):
        _rates()

    def test_cms_tabs_markup(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertIn('role="tablist"', html)
        self.assertEqual(html.count('role="tab"'), 3)
        self.assertEqual(html.count('role="tabpanel"'), 3)
        self.assertEqual(html.count('aria-selected="true"'), 1)
        # Progressive enhancement: only the first pane visible without JS.
        self.assertEqual(html.count('data-pl-rs-cms-pane hidden'), 2)
        for text in ('Олена · Лендінг', 'Нова', 'В роботі', 'Закрита', 'Редагувати'):
            self.assertIn(text, html)
        # CMS prices = lower bounds of the Soft ranges, swappable by FX.
        self.assertIn('id="fx-soft-cms-landing">250 €<', html)
        self.assertIn('id="fx-soft-cms-corp">500 €<', html)
        self.assertIn('id="fx-soft-cms-shop">800 €<', html)

    def test_cms_tabs_ru(self):
        html = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        for text in ('Страницы', 'Елена · Лендинг', 'Новая', 'В работе', 'Закрыта', 'Редактировать'):
            self.assertIn(text, html)

    def test_fx_swap_updates_cms_prices(self):
        response = self.client.post(
            '/i18n/set_currency/',
            {'currency': 'UAH', 'region': 'soft', 'next': '/rozrobka-sajtiv/'},
            HTTP_HX_REQUEST='true',
        )
        body = response.content.decode()
        self.assertIn('id="fx-soft-cms-landing" hx-swap-oob="outerHTML">10\u00a0000 ₴', body)

    def test_portfolio_screen_scroll_hooks(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertIn('js/portfolio-screen-scroll.js', html)
        self.assertIn('rozrobka-sajtiv-3.css', html)
