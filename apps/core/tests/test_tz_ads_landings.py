"""TZ D4–D8: ads landings — 200, hreflang, canonical, FAQ JSON-LD, sitemap, prices."""
import json
import re
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.ads_copy import CORP, RS, SHOP, faq_pairs
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
            ('/corporate-website-v2/', CORP['uk']['faq']),
            ('/ru/corporate-website-v2/', CORP['ru']['faq']),
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
        self.assertIn(
            'Менеджер передзвонить за 15 хвилин, відповість на питання і підбере пакет під ваш магазин. '
            'Ми не продаємо ваші дані і не використовуємо їх для спам-розсилок.',
            html,
        )
        self.assertNotIn('Телефон потрібен, щоб менеджер передзвонив', html)
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

    def test_rozrobka_types_link_and_offer_line(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertIn('Вартість 250–400 €, строк 3–7 днів.', html)
        self.assertIn('href="/internet-shop-v2/"', html)
        self.assertIn('href="/corporate-website-v2/"', html)
        self.assertIn('Гарантію закріплено в публічному договорі (п. 8 оферти)', html)
        ru = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        self.assertIn('Стоимость 250–400 €, срок 3–7 дней.', ru)
        self.assertIn('Гарантия закреплена в публичном договоре (п. 8 оферты)', ru)

    def test_contacts_schedule_label(self):
        for path, text in (
            ('/internet-shop-v2/', 'Графік: цілодобово'),
            ('/ru/internet-shop-v2/', 'График: круглосуточно'),
            ('/rozrobka-sajtiv/', 'Графік: цілодобово'),
            ('/ru/dorabotka-sajta/', 'График: круглосуточно'),
        ):
            with self.subTest(path=path):
                self.assertIn(text, self.client.get(path).content.decode())

    def test_shop_cases_use_small_card_thumbs(self):
        import re

        for path in ('/internet-shop-v2/', '/ru/internet-shop-v2/'):
            html = self.client.get(path).content.decode()
            imgs = re.findall(r'<img class="pl-ads-case__img"[^>]*>', html)
            if not imgs:
                continue  # no published shop projects in this DB
            for tag in imgs:
                with self.subTest(path=path, tag=tag[:80]):
                    self.assertIn('/ads-cards/', tag)
                    self.assertIn('400w', tag)
                    self.assertIn('width="280"', tag)
                    self.assertIn('height="180"', tag)

    def test_sitemap_has_no_en_dorobka_duplicate(self):
        xml = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('https://www.prometeylabs.com/dorobka-sajtu/', xml)
        self.assertIn('https://www.prometeylabs.com/ru/dorabotka-sajta/', xml)
        self.assertNotIn('/en/dorobka-sajtu/', xml)

    def test_dorobka_form_and_skipped_facts(self):
        html = self.client.get('/dorobka-sajtu/').content.decode()
        self.assertIn('name="website"', html)
        self.assertIn('Отримати аналіз сайту', html)
        self.assertIn(
            'Вартість і строк рахуємо після безкоштовного аналізу сайту і фіксуємо в договорі до старту робіт.',
            html,
        )
        self.assertNotIn('developer-modal', html)
        self.assertNotIn('noindex', html)
        self.assertIn('Доробка сайтів', html)
        ru = self.client.get('/ru/dorabotka-sajta/').content.decode()
        self.assertIn(
            'Стоимость и срок считаем после бесплатного анализа сайта и фиксируем в договоре до старта работ.',
            ru,
        )
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


class SophieAnswersTests(TestCase):
    """Sophie's answers to the open TZ questions (26.10.2026)."""

    def test_shop_form_note_and_privacy_link(self):
        cases = (
            ('/internet-shop-v2/', 'Менеджер передзвонить за 15 хвилин, відповість на питання і підбере пакет під ваш магазин. '
             'Ми не продаємо ваші дані і не використовуємо їх для спам-розсилок.',
             'href="/privacy/"', 'політикою конфіденційності'),
            ('/ru/internet-shop-v2/', 'Менеджер перезвонит за 15 минут, ответит на вопросы и подберёт пакет под ваш магазин. '
             'Мы не продаём ваши данные и не используем их для спам-рассылок.',
             'href="/ru/privacy/"', 'политикой конфиденциальности'),
        )
        for path, note, href, link_text in cases:
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                hero = html[html.index('id="pl-shop-hero-form"'):html.index('</form>', html.index('id="pl-shop-hero-form"'))]
                self.assertIn(note, hero)
                self.assertRegex(hero, href + r'[^>]*>' + link_text + '</a>')
                self.assertNotIn('Відкрити магазин', html)
                self.assertNotIn('Открыть магазин', html)

    def test_shop_premium_and_dropshipping_stay_from_1500(self):
        html = self.client.get('/internet-shop-v2/').content.decode()
        self.assertIn('від 1 500 €', html.replace('\xa0', ' '))

    def test_rozrobka_shop_price_from_800(self):
        for path, label in (('/rozrobka-sajtiv/', 'від 800 €'), ('/ru/rozrobka-sajtiv/', 'от 800 €')):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode().replace('\xa0', ' ')
                self.assertNotRegex(html, r'800\s?–\s?1\s?400')
                self.assertIn(f'<span id="fx-soft-float-shop">{label}</span>', html)
                self.assertIn(f'<span id="fx-soft-prod-shop">{label}</span>', html)
                self.assertIn('50+', html)

    def test_dorobka_steps_faq_and_portfolio(self):
        cases = (
            ('/dorobka-sajtu/', 'Погоджуємо обсяг робіт, вартість і строк — фіксуємо в договорі до старту.',
             'Портфоліо наших робіт', 'href="/portfolio/"', 'Скільки займає доробка?'),
            ('/ru/dorabotka-sajta/', 'Согласуем объём работ, стоимость и срок — фиксируем в договоре до старта.',
             'Портфолио наших работ', 'href="/ru/portfolio/"', 'Сколько занимает доработка?'),
        )
        for path, step3, h2, href, faq_q in cases:
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                steps = re.findall(r'<p class="pl-ads-process__text">(.*?)</p>', html)
                self.assertEqual(len(steps), 5)
                self.assertEqual(steps[2], step3)
                self.assertIn(h2, html)
                self.assertIn(href, html)
                self.assertIn(faq_q, html)
                self.assertNotIn('Приклади робіт', html)
                self.assertNotIn('Примеры работ', html)

    def test_corporate_faq_only_uk_ru(self):
        html = self.client.get('/corporate-website-v2/').content.decode()
        self.assertIn('Пожиттєва гарантія на код і 1 рік безкоштовної підтримки.', html)
        self.assertEqual(html.count('"@type":"FAQPage"'), 1)
        en = self.client.get('/en/corporate-website-v2/')
        if en.status_code == 200:
            self.assertNotIn('FAQPage', en.content.decode())
