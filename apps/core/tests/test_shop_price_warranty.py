"""Ціна старту магазину 800 €, дропшиппінг від 1 500 €, гарантія 1 рік (як в оферті 8.1)."""
from decimal import Decimal

from django.test import TestCase

from apps.core.fx_models import ExchangeRateSettings

NBSP = '\u00a0'
WARRANTY_BAD = (
    '5 років', '5 лет', '5-річна', '5-летняя', '5-year',
    'пожиттєв', 'Пожиттєв', 'пожизнен', 'Пожизнен', 'довічн', 'lifetime',
)
PAGES = (
    '/', '/ru/', '/en/',
    '/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/', '/en/rozrobka-sajtiv/',
    '/corporate-website-v2/', '/ru/corporate-website-v2/', '/en/corporate-website-v2/',
    '/internet-shop-v2/', '/ru/internet-shop-v2/', '/en/internet-shop-v2/',
    '/internet-shop/', '/ru/internet-shop/', '/en/internet-shop/',
    '/calculator/', '/ru/calculator/',
)


class ShopPriceTests(TestCase):
    def setUp(self):
        ExchangeRateSettings.objects.update_or_create(pk=1, defaults={
            'uah_per_eur': Decimal('51.45'),
            'usd_per_eur': Decimal('1.085'),
            'czk_per_eur': Decimal('25'),
        })

    def test_shop_v2_start_800_and_dropshipping_1500_eur(self):
        for url, word in (('/internet-shop-v2/', 'від'), ('/ru/internet-shop-v2/', 'от')):
            html = self.client.get(url).content.decode()
            self.assertIn(f'id="fx-pkg-base" class="pl-shop__pkg-price">{word} 800 €', html)
            self.assertIn(f'id="fx-drop-from" class="pl-shop__accent">{word} 1{NBSP}500 €', html)
            self.assertIn(f'data-fx-price-base="{word} 800 €"', html)
            self.assertNotIn('700&nbsp;€', html)
            self.assertNotIn(f'{word} 700 €', html)

    def test_uah_swap_shop_start_and_dropshipping(self):
        response = self.client.post('/i18n/set_currency/', {
            'currency': 'UAH', 'region': 'shop', 'next': '/internet-shop-v2/',
        }, HTTP_HX_REQUEST='true')
        body = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'id="fx-pkg-base" class="pl-shop__pkg-price" hx-swap-oob="outerHTML">від 41{NBSP}160 ₴', body)
        self.assertIn(f'id="fx-drop-from" class="pl-shop__accent" hx-swap-oob="outerHTML">від 77{NBSP}175 ₴', body)

    def test_uah_cookie_page_render(self):
        self.client.cookies['pl_currency'] = 'UAH'
        html = self.client.get('/internet-shop-v2/').content.decode()
        self.assertIn(f'від 41{NBSP}160 ₴', html)
        self.assertIn(f'від 77{NBSP}175 ₴', html)


class WarrantyOneYearTests(TestCase):
    def test_no_five_year_or_lifetime_claims(self):
        for url in PAGES:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)
            html = response.content.decode()
            for bad in WARRANTY_BAD:
                self.assertNotIn(bad, html, f'{url}: {bad}')

    def test_one_year_claims_present(self):
        checks = {
            '/rozrobka-sajtiv/': 'Безкоштовна підтримка та 1 рік гарантії на код.',
            '/ru/rozrobka-sajtiv/': 'Бесплатная поддержка и 1 год гарантии на код.',
            '/en/rozrobka-sajtiv/': 'Free support and a 1-year code warranty.',
            '/corporate-website-v2/': '1 рік гарантії на код',
            '/ru/corporate-website-v2/': '1 год гарантии на код',
            '/internet-shop-v2/': '1 рік гарантії на код',
            '/ru/internet-shop-v2/': '1 год гарантии на код',
            '/': 'Річна',
            '/ru/': 'Годовая',
            '/en/': '1-year',
        }
        for url, text in checks.items():
            self.assertIn(text, self.client.get(url).content.decode(), url)

    def test_telegram_bot_states_offer_one_year(self):
        html = self.client.get('/telegram-bot/').content.decode()
        self.assertIn('1 рік на багфікс', html)
