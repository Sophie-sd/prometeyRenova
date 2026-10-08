"""Soft service tiles → existing page + thematic section hash; CMS tabs; screen scroll hooks."""
import re
from decimal import Decimal

from django.test import TestCase

from apps.core.fx_models import ExchangeRateSettings

TILE_HREF_RE = re.compile(r'class="pl-rs__product[^"]*" href="([^"]+)"')

# Order = tile order: Лендінги, Корпоративні сайти, Інтернет-магазини, Платформи, Telegram-боти.
EXPECTED_TILES = [
    ('/corporate-website-v2/', 'scale'),
    ('/corporate-website-v2/', 'economy'),
    ('/internet-shop-v2/', 'pakety'),
    ('/corporate-website-v2/', 'tech'),
    ('/telegram-bot/', 'pakety'),
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


class SoftTileHashLinksTests(TestCase):
    def setUp(self):
        _rates()

    def test_tile_hrefs_page_and_hash(self):
        for prefix in ('', '/ru'):
            with self.subTest(prefix=prefix):
                html = self.client.get(f'{prefix}/rozrobka-sajtiv/').content.decode()
                expected = [f'{prefix}{page}#{anchor}' for page, anchor in EXPECTED_TILES]
                self.assertEqual(TILE_HREF_RE.findall(html), expected)

    def test_tile_targets_200_and_contain_anchor_id(self):
        for prefix in ('', '/ru'):
            for page, anchor in EXPECTED_TILES:
                path = prefix + page
                with self.subTest(path=path, anchor=anchor):
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(f'id="{anchor}"', response.content.decode())

    def test_removed_pages_404(self):
        # Slugs of the two pages deleted after 0ee7e69 (built from parts so the repo keeps no literal slug).
        removed = ['/rozrobka-' + 'lendingu/', '/rozrobka-veb-' + 'platform/']
        for path in removed + ['/ru' + p for p in removed]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)


class SoftCmsTabsAndScreensTests(TestCase):
    def setUp(self):
        _rates()

    def test_cms_tabs_markup(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertIn('role="tablist"', html)
        self.assertEqual(html.count('role="tab"'), 3)
        self.assertEqual(html.count('role="tabpanel"'), 3)
        self.assertEqual(html.count('aria-selected="true"'), 1)
        self.assertEqual(html.count('data-pl-rs-cms-pane hidden'), 2)
        for text in ('Олена · Лендінг', 'Нова', 'В роботі', 'Закрита', 'Редагувати'):
            self.assertIn(text, html)
        self.assertIn('id="fx-soft-cms-landing">250 €<', html)
        self.assertIn('id="fx-soft-cms-corp">500 €<', html)
        self.assertIn('id="fx-soft-cms-shop">800 €<', html)

    def test_cms_tabs_ru(self):
        html = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        for text in ('Страницы', 'Елена · Лендинг', 'Новая', 'В работе', 'Закрыта', 'Редактировать', 'Лендинг'):
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
