"""TZ D4–D8: ads landings — 200, hreflang, canonical, FAQ JSON-LD, sitemap, prices."""
import json
import re
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.ads_copy import RS, SHOP, faq_pairs
from apps.core.ads_copy_dorobka import DOROBKA
from apps.core.sitemaps import StaticViewSitemap

ADS = (
    '/internet-shop-v2/',
    '/ru/internet-shop-v2/',
    '/rozrobka-sajtiv/',
    '/ru/rozrobka-sajtiv/',
    '/corporate-website-v2/',
    '/ru/corporate-website-v2/',
    '/dorobka-sajtu/',
    '/ru/dorabotka-sajta/',
    '/',
    '/ru/',
)


def _ld_blocks(html):
    return [json.loads(chunk) for chunk in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S,
    )]


def _visible_faq(html):
    block = html
    if 'id="pl-ads-faq-title"' in html:
        start = html.index('id="pl-ads-faq-title"')
        block = html[start:html.index('</section>', start)]
    return re.findall(
        r'<summary class="pl-ads-faq__q">(.*?)</summary>\s*<p class="pl-ads-faq__a">(.*?)</p>',
        block, re.S,
    )


class AdsLandingSeoTests(TestCase):
    def test_pages_200(self):
        for path in ADS + ('/portfolio/', '/ru/portfolio/', '/sitemap.xml', '/offer/'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200, path)

    def test_hreflang_and_canonical(self):
        pairs = (
            ('/internet-shop-v2/', '/ru/internet-shop-v2/'),
            ('/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/'),
            ('/corporate-website-v2/', '/ru/corporate-website-v2/'),
            ('/dorobka-sajtu/', '/ru/dorabotka-sajta/'),
            ('/', '/ru/'),
        )
        for uk, ru in pairs:
            for path, canonical in ((uk, uk), (ru, ru)):
                with self.subTest(path=path):
                    html = self.client.get(path).content.decode()
                    self.assertIn(
                        f'rel="canonical" href="https://www.prometeylabs.com{canonical}"',
                        html,
                    )
                    self.assertIn(f'hreflang="uk" href="https://www.prometeylabs.com{uk}"', html)
                    self.assertIn(f'hreflang="ru" href="https://www.prometeylabs.com{ru}"', html)
                    self.assertIn(
                        f'hreflang="x-default" href="https://www.prometeylabs.com{uk}"',
                        html,
                    )

    def test_json_ld_valid_and_faq_matches(self):
        cases = (
            ('/internet-shop-v2/', SHOP['uk']['faq']),
            ('/ru/internet-shop-v2/', SHOP['ru']['faq']),
            ('/rozrobka-sajtiv/', RS['uk']['faq']),
            ('/ru/rozrobka-sajtiv/', RS['ru']['faq']),
            ('/dorobka-sajtu/', DOROBKA['uk']['faq']),
            ('/ru/dorabotka-sajta/', DOROBKA['ru']['faq']),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                blocks = _ld_blocks(html)
                types = [block.get('@type') for block in blocks]
                self.assertIn('BreadcrumbList', types, path)
                self.assertIn('FAQPage', types, path)
                org = [block for block in blocks if 'Organization' in str(block.get('@type'))]
                self.assertTrue(org, path)
                address = org[0]['address']
                self.assertEqual(address['streetAddress'], 'бульвар Тараса Шевченка 46а')
                self.assertEqual(address['addressCountry'], 'UA')
                self.assertIn(address['addressLocality'], ('Київ', 'Kyiv'))
                faq = next(block for block in blocks if block.get('@type') == 'FAQPage')
                json_pairs = [
                    (item['name'], item['acceptedAnswer']['text'])
                    for item in faq['mainEntity']
                ]
                self.assertEqual(json_pairs, list(expected), path)
                visible = [(q.strip(), a.strip()) for q, a in _visible_faq(html)]
                self.assertEqual(visible, json_pairs, path)

    def test_corporate_has_breadcrumb_and_org(self):
        for path in ('/corporate-website-v2/', '/ru/corporate-website-v2/'):
            html = self.client.get(path).content.decode()
            types = [block.get('@type') for block in _ld_blocks(html)]
            self.assertIn('BreadcrumbList', types, path)
            self.assertIn('Service', types, path)

    def test_sitemap_contains_new_and_ads_pages(self):
        self.assertIn('dorobka_sajtu', StaticViewSitemap.PAGES)
        body = self.client.get('/sitemap.xml').content.decode()
        for path in (
            '/dorobka-sajtu/',
            '/ru/dorabotka-sajta/',
            '/internet-shop-v2/',
            '/ru/internet-shop-v2/',
            '/rozrobka-sajtiv/',
        ):
            self.assertIn(path, body)

    def test_rozrobka_prices_once_in_hero(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        hero = html[html.index('class="pl-rs__hero"'):html.index('</section>')]
        self.assertEqual(hero.count('class="pl-rs__floats"'), 1)
        self.assertEqual(hero.count('250–400 €'), 1)

    def test_shop_dom_under_1500(self):
        html = self.client.get('/internet-shop-v2/').content.decode()
        self.assertLess(len(re.findall(r'<[a-zA-Z]', html)), 1500)

    def test_shop_copy_and_skips(self):
        html = self.client.get('/internet-shop-v2/').content.decode()
        self.assertIn('Портфоліо: інтернет-магазини, які ми запустили', html)
        self.assertIn('Що входить у Base', html)
        self.assertIn('Телефон потрібен, щоб менеджер передзвонив і назвав орієнтовну вартість.', html)
        self.assertNotIn('Не передаємо третім особам.', html)
        self.assertNotIn('Відгуки власників магазинів', html)
        self.assertIn('Виконавець: ФОП Дмитренко Софія Дмитрівна', html)
        self.assertNotIn('РНОКПП', html)
        self.assertIn('Усі роботи', html)
        self.assertNotIn('Відкрити магазин', html)

    def test_rozrobka_types_and_faq(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertIn('Створити сайт для бізнесу: який тип обрати', html)
        self.assertIn('Гарантія і підтримка', html)
        self.assertIn('50+ запущених проєктів', html)
        self.assertNotIn('Відгуки клієнтів', html)

    def test_dorobka_form_and_skipped_facts(self):
        html = self.client.get('/dorobka-sajtu/').content.decode()
        self.assertIn('name="website"', html)
        self.assertIn('Отримати аналіз сайту', html)
        self.assertIn('Вартість рахуємо після безкоштовного аналізу сайту.', html)
        self.assertNotIn('і фіксуємо до старту робіт', html)
        self.assertNotIn('и фиксируем до старта работ', html)
        self.assertNotIn('developer-modal', html)
        self.assertNotIn('noindex', html)
        self.assertIn('Доробка сайтів', html)
        ru = self.client.get('/ru/dorabotka-sajta/').content.decode()
        self.assertIn('Стоимость считаем после бесплатного анализа сайта.', ru)
        self.assertIn('Получить анализ сайта', ru)

    def test_menu_and_home_link_to_dorobka(self):
        home = self.client.get('/').content.decode()
        self.assertIn('/dorobka-sajtu/', home)
        self.assertIn('Оновлення проєктів', home)

    def test_dorobka_url_reverse(self):
        with translation.override('uk'):
            self.assertEqual(reverse('dorobka_sajtu'), '/dorobka-sajtu/')
        with translation.override('ru'):
            self.assertEqual(reverse('dorobka_sajtu'), '/ru/dorabotka-sajta/')

    @mock.patch('apps.core.views._dispatch_async')
    def test_website_field_lands_in_details(self, _dispatch):
        from apps.core.models import FormSubmission

        response = self.client.post('/forms/submit/', {
            'form_type': 'site_request',
            'source_page': 'dorobka-sajtu',
            'details': 'Сторінка: Доробка сайту',
            'name': 'Тест',
            'phone': '+380671234567',
            'website': 'https://example.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['redirect'], '/thank-you/')
        row = FormSubmission.objects.get()
        self.assertIn('Адреса сайту: https://example.com', row.details)
        self.assertEqual(row.extra_data.get('website'), 'https://example.com')
        self.assertEqual(row.extra_data.get('source_page'), 'dorobka-sajtu')

    def test_faq_pairs_helper_matches_copy(self):
        self.assertEqual(
            [(item['q'], item['a']) for item in faq_pairs(SHOP['uk']['faq'])],
            list(SHOP['uk']['faq']),
        )
