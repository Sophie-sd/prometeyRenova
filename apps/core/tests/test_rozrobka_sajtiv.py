"""Ads-лендінг /rozrobka-sajtiv/: шлях, Soft €, одна H1, конверсійні CTA."""
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.sitemaps import StaticViewSitemap


def _landing_markup(html):
    start = html.find('id="plRsRoot"')
    end = html.find('id="pl-rs-calc"')
    if start == -1 or end == -1:
        return ''
    return html[start:end]


class RozrobkaSajtivPageTests(TestCase):
    def test_reverse_uk_path(self):
        with translation.override('uk'):
            self.assertEqual(reverse('rozrobka_sajtiv'), '/rozrobka-sajtiv/')

    def test_uk_and_ru_return_200(self):
        for path in ('/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_uk_offer_lock_and_single_h1(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        root = _landing_markup(html)
        self.assertIn('rozrobka-sajtiv.css', html)
        self.assertIn('Розробка сайтів будь-якої складності під ключ', html)
        self.assertIn('Отримати консультацію', root)
        self.assertIn('250', root)
        self.assertIn('500', root)
        self.assertIn('800', root)
        self.assertIn('€', root)
        self.assertIn('rozrobka-sajtiv.js', html)
        self.assertIn('href="/calculator/"', root)
        self.assertIn('Розрахувати вартість', root)
        self.assertIn('Написати в Telegram', root)
        self.assertIn('https://t.me/prometeylabs', root)
        self.assertIn('Зателефонувати прямо зараз', root)
        self.assertIn('tel:+380639520565', root)
        self.assertIn('href="/corporate-website/"', root)
        self.assertIn('href="/internet-shop/"', root)
        self.assertIn('href="/telegram-bot/"', root)
        self.assertEqual(html.count('<h1'), 1)
        self.assertEqual(html.count('</h1>'), 1)
        self.assertIn('data-modal="call-request-modal"', root)

    def test_currency_switcher_defaults_to_euro(self):
        import re

        for path in ('/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/'):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                root = _landing_markup(html)
                self.assertIn('class="pl-rs__cur"', root)
                self.assertIn('role="group"', root)
                self.assertIn('data-currency="eur"', root)
                self.assertIn('data-currency="usd"', root)
                self.assertRegex(
                    root,
                    r'data-currency="eur"[^>]*aria-pressed="true"',
                )
                self.assertRegex(
                    root,
                    r'data-currency="usd"[^>]*aria-pressed="false"',
                )
                amounts = re.findall(
                    r'data-pl-rs-amount[^>]*>\s*([^<]+?)\s*<',
                    root,
                )
                signs = re.findall(
                    r'data-pl-rs-sign[^>]*>\s*([^<]+?)\s*<',
                    root,
                )
                self.assertEqual(amounts, ['250', '500', '800', '250', '500', '800'])
                self.assertTrue(signs)
                self.assertTrue(all(sign == '€' for sign in signs))
                self.assertNotIn('$', ''.join(signs))
                self.assertIn('data-eur="250"', root)
                self.assertIn('data-usd="270"', root)
                self.assertIn('data-eur="500"', root)
                self.assertIn('data-usd="540"', root)
                self.assertIn('data-eur="800"', root)
                self.assertIn('data-usd="865"', root)
                self.assertNotIn('>270<', root)
                self.assertNotIn('>540<', root)
                self.assertNotIn('>865<', root)

    def test_ru_mirror_has_soft_euro_and_no_dollar(self):
        html = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        root = _landing_markup(html)
        self.assertIn('Разработка сайтов любой сложности под ключ', html)
        self.assertIn('Получить консультацию', root)
        self.assertIn('€', root)
        self.assertIn('role="group"', root)
        self.assertIn('href="/ru/calculator/"', root)
        self.assertIn('tel:+380639520565', root)
        self.assertEqual(html.count('<h1'), 1)

    def test_seo_head(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertIn('Розробка сайтів під ключ в Україні | PrometeyLabs', html)
        self.assertIn('rel="canonical" href="https://www.prometeylabs.com/rozrobka-sajtiv/"', html)
        self.assertIn('hreflang="uk"', html)
        self.assertIn('hreflang="ru"', html)
        self.assertIn('hreflang="x-default"', html)
        self.assertIn('https://www.prometeylabs.com/ru/rozrobka-sajtiv/', html)
        self.assertIn('https://www.prometeylabs.com/static/images/og-image.jpg', html)
        self.assertIn('twitter:card', html)
        self.assertIn('property="og:image"', html)

    def test_ru_canonical(self):
        html = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        self.assertIn(
            'rel="canonical" href="https://www.prometeylabs.com/ru/rozrobka-sajtiv/"',
            html,
        )


class RozrobkaSajtivSitemapTests(TestCase):
    def test_static_sitemap_includes_page(self):
        self.assertIn('rozrobka_sajtiv', StaticViewSitemap.PAGES)
        self.assertEqual(StaticViewSitemap.PAGES['rozrobka_sajtiv'][0], 0.9)
        with translation.override('uk'):
            self.assertEqual(reverse('rozrobka_sajtiv'), '/rozrobka-sajtiv/')

    def test_sitemap_xml_contains_path(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/rozrobka-sajtiv/', response.content.decode())
