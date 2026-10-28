"""Calc CTA: головна помаранчева кнопка-квіз на першому екрані всіх Ads-посадкових UA/RU."""
import re
from html import unescape

from django.test import TestCase

from apps.core.calc_cta import CALC_CTA

PAGES = (
    ('/', 'home', 'uk', '/calculator/?start=1'),
    ('/ru/', 'home', 'ru', '/ru/calculator/?start=1'),
    # ТЗ 27.10.2026: rozrobka embeds the quiz → hero/sticky scroll to it on the same page
    ('/rozrobka-sajtiv/', 'rozrobka', 'uk', '#pl-rs-calc'),
    ('/ru/rozrobka-sajtiv/', 'rozrobka', 'ru', '#pl-rs-calc'),
    ('/internet-shop-v2/', 'shop', 'uk', '#zayavka'),
    ('/ru/internet-shop-v2/', 'shop', 'ru', '#zayavka'),
    ('/corporate-website-v2/', 'corp', 'uk', '#calculator'),
    ('/ru/corporate-website-v2/', 'corp', 'ru', '#calculator'),
    ('/dorobka-sajtu/', 'dorobka', 'uk', '/calculator/?start=1'),
    ('/ru/dorabotka-sajta/', 'dorobka', 'ru', '/ru/calculator/?start=1'),
)

HERO_RE = re.compile(r'<a href="([^"]+)" class="pl-calc-cta__btn[^"]*"[^>]*data-calc-cta="hero"[^>]*>'
                     r'<span class="pl-calc-cta__label">([^<]+)</span>')
STICKY_RE = re.compile(r'<a href="([^"]+)" class="pl-calc-sticky__btn"[^>]*data-calc-cta="sticky"[^>]*>'
                       r'<span class="pl-calc-cta__label">([^<]+)</span>')


class CalcCtaLandingTests(TestCase):
    def _html(self, url):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, url)
        return resp.content.decode()

    def test_hero_button_text_href_and_micro(self):
        for url, page, lang, href in PAGES:
            with self.subTest(url=url):
                html = self._html(url)
                copy = CALC_CTA[page][lang]
                hero = HERO_RE.findall(html)
                self.assertEqual(len(hero), 1, f'{url}: exactly one hero calc CTA')
                self.assertEqual(unescape(hero[0][0]), href)
                self.assertEqual(unescape(hero[0][1]), copy['label'])
                self.assertIn(f'data-calc-page="{page}"', html)
                self.assertIn(copy['micro'], unescape(html))
                self.assertIn('css/components/calc-cta.css', html)

    def test_sticky_present_same_label_and_target(self):
        for url, page, lang, href in PAGES:
            with self.subTest(url=url):
                html = self._html(url)
                sticky = STICKY_RE.findall(html)
                self.assertEqual(len(sticky), 1, url)
                self.assertEqual(unescape(sticky[0][0]), href)
                self.assertEqual(unescape(sticky[0][1]), CALC_CTA[page][lang].get('sticky', CALC_CTA[page][lang]['label']))
                self.assertLessEqual(len(unescape(sticky[0][1])), 28, url)  # «Рассчитайте стоимость онлайн» = 28
                self.assertIn('js/components/calc-cta.js', html)

    def test_on_page_quiz_anchor_exists(self):
        for url, page, lang, href in PAGES:
            if not href.startswith('#'):
                continue
            with self.subTest(url=url):
                self.assertIn(f'id="{href[1:]}"', self._html(url))

    def test_hero_cta_is_in_first_screen_markup(self):
        """Calc CTA renders inside the hero section (before the first </section>)."""
        for url, _page, _lang, _href in PAGES:
            with self.subTest(url=url):
                html = self._html(url)
                start = html.index('<main') if '<main' in html else 0
                first_section_end = html.index('</section>', html.index('<section', start))
                self.assertLess(html.index('data-calc-cta="hero"'), first_section_end, url)

    def test_ru_copy_is_russian_and_uk_is_ukrainian(self):
        for page, entry in CALC_CTA.items():
            with self.subTest(page=page):
                self.assertTrue(entry['ru']['label'].startswith('Рассчитать'))
                self.assertTrue(entry['uk']['label'].startswith('Розрахувати'))
                for lang in ('uk', 'ru'):
                    micro = entry[lang]['micro'].lower()
                    for banned in ('одразу', 'сразу', 'без дзвін', 'без звон', 'миттєв', 'мгновен'):
                        self.assertNotIn(banned, micro, f'{page}/{lang}: quiz does not promise {banned}')

    def test_home_secondary_buttons_are_ghost(self):
        for url in ('/', '/ru/'):
            with self.subTest(url=url):
                html = self._html(url)
                hero = html[html.index('class="hf-hero"'):html.index('</section>', html.index('class="hf-hero"'))]
                self.assertNotIn('hf-btn--light', hero)
                self.assertIn('hf-hero__secondary', hero)

    def test_forms_kept_on_rozrobka_hero(self):
        for url, form_id in (('/rozrobka-sajtiv/', 'pl-rs-hero-form'), ('/ru/rozrobka-sajtiv/', 'pl-rs-hero-form')):
            with self.subTest(url=url):
                html = self._html(url)
                self.assertIn(f'id="{form_id}"', html)
                self.assertLess(html.index('data-calc-cta="hero"'), html.index(f'id="{form_id}"'))

    def test_shop_hero_has_no_form_and_form1_after_svoboda(self):
        # ТЗ 27.10.2026 п. 4.2 / 4.9: форму з hero прибрано, «Форма №1» — після «Переросли Prom».
        for url in ('/internet-shop-v2/', '/ru/internet-shop-v2/'):
            with self.subTest(url=url):
                html = self._html(url)
                self.assertNotIn('id="pl-shop-hero-form"', html)
                self.assertLess(html.index('id="svoboda"'), html.index('id="forma-1"'))
                self.assertLess(html.index('id="forma-1"'), html.index('id="dropshipping"'))
                self.assertLess(html.index('id="garantiya"'), html.index('id="rozrahunok"'))
                self.assertLess(html.index('id="rozrahunok"'), html.index('id="faq"'))

    def test_shop_order_matches_tz_section_3(self):
        # ТЗ 27.10.2026 розд. 3 (канон): херо → логотипи → тест #zayavka → пакети → … → смуга → FAQ → підвал.
        order = ('top', 'portfolio', 'zayavka', 'pakety', 'svoboda', 'forma-1', 'pl-shop-admin-title', 'dropshipping', 'garantiya', 'rozrahunok', 'faq')
        for url in ('/internet-shop-v2/', '/ru/internet-shop-v2/'):
            with self.subTest(url=url):
                html = self._html(url)
                pos = [html.index(f'id="{a}"') for a in order]
                self.assertEqual(pos, sorted(pos))
                self.assertLess(pos[-1], html.index('<footer'))
                self.assertEqual(html[pos[1]:pos[2]].count('<section'), 1)  # між логотипами і тестом нічого
                sticky = html[html.index('data-calc-sticky'):]
                self.assertIn('data-calc-target="#zayavka"', sticky[:300])
                self.assertIn('href="#zayavka"', sticky[:700])
                # Фони закріплені за позиціями: тест (№3) без полум'я, полум'я — у слоті №10 (смуга).
                self.assertNotIn('pl-shop__calc-bg', html[pos[2]:pos[3]])
                self.assertEqual(html.count('class="pl-shop__calc-bg"'), 1)
                self.assertIn('class="pl-shop__calc-bg"', html[pos[8]:pos[10]])

    def test_calculator_supports_autostart(self):
        for url in ('/calculator/', '/ru/calculator/'):
            with self.subTest(url=url):
                resp = self.client.get(url + '?start=1')
                self.assertEqual(resp.status_code, 200)
                self.assertContains(resp, 'id="test-section"')
                self.assertContains(resp, 'js/calculator.js')
