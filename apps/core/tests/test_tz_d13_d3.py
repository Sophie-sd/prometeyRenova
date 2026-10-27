"""ТЗ D13 (SSR-речення «30+ інтернет-магазинів») і D3 (ціни в hero /rozrobka-sajtiv/ один раз)."""
from decimal import Decimal

from django.test import TestCase

from apps.core.fx_models import ExchangeRateSettings
from apps.core.models import PortfolioProject

UK_NOTE = 'Ми розробили 30+ інтернет-магазинів — тут добірка найкращих'
RU_NOTE = 'Мы разработали 30+ интернет-магазинов — здесь подборка лучших'


class ShopsNoteTests(TestCase):
    def setUp(self):
        PortfolioProject.objects.create(
            title='Demo', slug='demo-d13', card_description='Desc', is_published=True, show_on_portfolio=True,
        )

    def _html(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200, path)
        return response.content.decode()

    def test_note_server_rendered_on_portfolio_pages(self):
        for path, note, other in (
            ('/portfolio/', UK_NOTE, RU_NOTE),
            ('/ru/portfolio/', RU_NOTE, UK_NOTE),
        ):
            with self.subTest(path=path):
                html = self._html(path)
                self.assertEqual(html.count(note), 1)
                self.assertNotIn(other, html)

    def test_portfolio_note_above_filter(self):
        html = self._html('/portfolio/')
        self.assertLess(html.index(UK_NOTE), html.index('id="pfg-filters-title"'))


class RozrobkaHeroPricesOnceTests(TestCase):
    def setUp(self):
        ExchangeRateSettings.objects.update_or_create(
            pk=1,
            defaults={'uah_per_eur': Decimal('40'), 'usd_per_eur': Decimal('1.085'), 'czk_per_eur': Decimal('25')},
        )

    def test_hero_has_single_price_block(self):
        for path in ('/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                hero = html[html.index('class="pl-rs__hero"'):]
                hero = hero[:hero.index('</section>')]
                self.assertNotIn('pl-rs__prices', hero)
                self.assertNotIn('fx-soft-strip-', html)
                self.assertEqual(hero.count('class="pl-rs__float pl-rs__float--'), 4)
                for key in ('landing', 'corp', 'shop', 'platform'):
                    self.assertEqual(hero.count('id="fx-soft-float-%s"' % key), 1)
                self.assertNotIn('pl-rs__floats" aria-hidden', hero)

    def test_self_hosted_fonts_no_google(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertNotIn('fonts.googleapis.com', html)
        self.assertIn('font-display:optional', html)
        self.assertIn('fonts/v2/inter-cyrillic.woff2', html)
        self.assertNotIn('{#', html)
        self.assertNotIn('#}', html)

    def test_hero_form_card_reserves_height(self):
        from pathlib import Path

        css = Path('static/css/pages/rozrobka-sajtiv.css').read_text(encoding='utf-8')
        self.assertIn('.pl-rs__hero-form-card{', css)
        self.assertIn('min-height:292px', css)
        self.assertIn('min-height:308px', css)

    def test_lang_suggest_not_in_hero_form_flow(self):
        html = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        hero = html[html.index('class="pl-rs__hero"'):]
        hero = hero[:hero.index('</section>')]
        self.assertNotIn('id="lang-suggest"', hero)
        self.assertNotIn('lang-suggest.js', hero)
        if 'id="lang-suggest"' in html:
            self.assertIn('class="lang-suggest"', html)
            self.assertLess(html.index('</main>'), html.index('id="lang-suggest"'))

    def test_no_standalone_facebook_or_doubleclick_scripts(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertNotIn('connect.facebook.net', html)
        self.assertNotIn('fbevents.js', html)
        self.assertNotIn('googleads.g.doubleclick.net', html)
        self.assertNotIn('www.googleadservices.com/pagead', html)
        self.assertIn('gclid-capture.js', html)
        self.assertIn('GTM-K2FVPPTK', html)
        self.assertIn('function _loadGTM()', html)

    def test_price_ranges_once_in_hero_floats(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        hero = html[html.index('class="pl-rs__hero"'):]
        hero = hero[:hero.index('</section>')]
        self.assertEqual(hero.count('class="pl-rs__floats"'), 1)
        self.assertEqual(hero.count('250–400 €'), 1)
        self.assertEqual(hero.count('500–700 €'), 1)
        self.assertEqual(hero.count('<span id="fx-soft-float-shop">від 800 €</span>'), 1)
        self.assertEqual(hero.count('1\u00a0500–5\u00a0000 €'), 1)
