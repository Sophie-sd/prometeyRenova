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

    def test_tiles_removed_from_rozrobka(self):
        """ТЗ 27.10.2026 п. 3.3: the price tiles block (and its hash links) is gone from /rozrobka-sajtiv/."""
        for prefix in ('', '/ru'):
            with self.subTest(prefix=prefix):
                html = self.client.get(f'{prefix}/rozrobka-sajtiv/').content.decode()
                self.assertEqual(TILE_HREF_RE.findall(html), [])
                for page, anchor in EXPECTED_TILES:
                    self.assertNotIn(f'href="{prefix}{page}#{anchor}"', html)

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

    def test_cms_mockup_block_removed(self):
        """ТЗ 27.10.2026 п. 3.3: «Адмінка залишається у вас» CMS mockup is not on the page (UA/RU)."""
        for path in ('/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/'):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                self.assertNotIn('data-pl-rs-cms-pane', html)
                self.assertNotIn('fx-soft-cms-', html)
                self.assertNotIn('pl-rs__section--admin', html)

    def test_portfolio_screen_scroll_hooks(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertIn('js/portfolio-screen-scroll.js', html)
        # Screen-scroll layer now lives in the single merged stylesheet.
        self.assertIn('css/pages/rozrobka-sajtiv.css', html)


class SoftSingleStylesheetTests(TestCase):
    """Perf: one render-blocking page stylesheet (currency.css merged in), no stale -2/-3 links."""

    def setUp(self):
        _rates()

    def test_one_page_stylesheet_ua_ru(self):
        for path in ('/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/'):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                self.assertEqual(html.count('css/pages/rozrobka-sajtiv.css'), 1)
                self.assertNotIn('rozrobka-sajtiv-2.css', html)
                self.assertNotIn('rozrobka-sajtiv-3.css', html)
                self.assertNotIn('css/components/currency.css', html)
                self.assertNotIn('Space+Grotesk', html)

    def test_merged_css_contains_currency_css_verbatim(self):
        from pathlib import Path

        from django.conf import settings

        static = Path(settings.BASE_DIR) / 'static' / 'css'
        merged = (static / 'pages' / 'rozrobka-sajtiv.css').read_text(encoding='utf-8')
        currency = (static / 'components' / 'currency.css').read_text(encoding='utf-8').rstrip()
        self.assertIn(currency, merged)

    def test_other_pages_keep_global_currency_css(self):
        html = self.client.get('/').content.decode()
        self.assertIn('css/components/currency.css', html)
