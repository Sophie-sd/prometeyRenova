"""Ads-лендінг /rozrobka-sajtiv/: ranges, FX €/₴, одна H1, CTA."""
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.fx_models import ExchangeRateSettings
from apps.core.sitemaps import StaticViewSitemap


def _landing_markup(html):
    start = html.find('id="plRsRoot"')
    end = html.find('id="pl-rs-calc"')
    if start == -1 or end == -1:
        return ''
    return html[start:end]


class RozrobkaSajtivPageTests(TestCase):
    def setUp(self):
        from decimal import Decimal

        ExchangeRateSettings.objects.update_or_create(
            pk=1,
            defaults={
                'uah_per_eur': Decimal('40'),
                'usd_per_eur': Decimal('1.085'),
                'czk_per_eur': Decimal('25'),
            },
        )

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
        self.assertIn('250–400 €', root)
        self.assertIn('500–700 €', root)
        self.assertIn('800–1\u00a0400 €', root)
        self.assertIn('1\u00a0500–5\u00a0000 €', root)
        self.assertIn('3–7 днів', root)
        self.assertIn('7–14 днів', root)
        self.assertIn('14–21 день', root)
        self.assertIn('14–30 днів', root)
        self.assertIn('У сумі:', root)
        self.assertIn('Не входить:', root)
        self.assertIn('1 рік гарантії на код', root)
        self.assertNotIn('5 років', root)
        self.assertNotIn('індивідуально', root)
        self.assertNotIn('окремий бриф', root)
        soft_hits = [s for s in ('SOFT', 'Soft ·', 'Soft —', 'орієнтири Soft') if s in html]
        self.assertEqual(soft_hits, [], soft_hits)
        self.assertIn('rozrobka-sajtiv.js', html)
        # Hero: 3-row link list removed; mobile-only secondary calc CTA instead.
        self.assertNotIn('pl-rs__links', root)
        self.assertNotIn('pl-rs__link--muted', root)
        self.assertNotIn('Написати в Telegram', root)
        self.assertNotIn('Зателефонувати прямо зараз', root)
        self.assertIn(
            '<a class="pl-rs__cta-alt mobile-touch-target" href="/calculator/">Розрахувати вартість</a>',
            root,
        )
        # Telegram / phone remain in the closing calc block.
        self.assertIn('Написати в Telegram', html)
        self.assertIn('https://t.me/prometeylabs', html)
        self.assertIn('Зателефонувати прямо зараз', html)
        self.assertIn('tel:+380639520565', html)
        self.assertIn('href="/corporate-website-v2/#scale"', root)
        self.assertIn('href="/corporate-website-v2/#economy"', root)
        self.assertIn('href="/internet-shop-v2/#pakety"', root)
        self.assertIn('href="/corporate-website-v2/#tech"', root)
        self.assertIn('href="/telegram-bot/#pakety"', root)
        self.assertEqual(html.count('<h1'), 1)
        self.assertEqual(html.count('</h1>'), 1)
        self.assertIn('data-modal="call-request-modal"', root)
        self.assertIn('pl-rs__product--wide', root)
        self.assertIn('pl-rs__products', root)

    def test_currency_switcher_defaults_to_euro(self):
        for path in ('/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/'):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                root = _landing_markup(html)
                self.assertIn('id="fx-switch-soft"', root)
                self.assertIn('fx-switch--dark', root)
                self.assertIn('value="UAH"', root)
                self.assertNotIn('data-currency="usd"', root)
                self.assertNotIn('data-currency="eur"', root)
                self.assertNotIn('data-pl-rs-amount', root)
                self.assertNotIn('data-usd=', root)
                self.assertIn('250–400 €', root)
                self.assertIn('value="UAH"', root)
                self.assertIn('₴', root)

    def test_soft_fx_htmx_swaps_uah(self):
        response = self.client.post(
            '/i18n/set_currency/',
            {'currency': 'UAH', 'region': 'soft', 'next': '/rozrobka-sajtiv/'},
            HTTP_HX_REQUEST='true',
        )
        body = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies['pl_currency'].value, 'UAH')
        self.assertIn('10\u00a0000–16\u00a0000 ₴', body)
        self.assertIn('id="fx-switch-soft"', body)
        self.assertIn('hx-swap-oob="outerHTML"', body)
        self.assertIn('id="fx-soft-float-landing"', body)

    def test_ru_mirror_has_euro_and_no_dollar_switcher(self):
        html = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        root = _landing_markup(html)
        self.assertIn('Разработка сайтов любой сложности под ключ', html)
        self.assertIn('Получить консультацию', root)
        self.assertIn('€', root)
        self.assertIn('id="fx-switch-soft"', root)
        self.assertNotIn('data-currency="usd"', root)
        self.assertIn(
            '<a class="pl-rs__cta-alt mobile-touch-target" href="/ru/calculator/">Рассчитать стоимость</a>',
            root,
        )
        self.assertNotIn('pl-rs__links', root)
        self.assertIn('tel:+380639520565', html)
        self.assertEqual(html.count('<h1'), 1)

    def test_seo_head(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertIn('Розробка сайтів під ключ в Україні | PrometeyLabs', html)
        self.assertIn('250–400 €', html)
        self.assertIn('500–700 €', html)
        self.assertIn('rel="canonical" href="https://www.prometeylabs.com/rozrobka-sajtiv/"', html)
        self.assertIn('hreflang="uk"', html)
        self.assertIn('hreflang="ru"', html)
        self.assertIn('hreflang="x-default"', html)
        self.assertIn('https://www.prometeylabs.com/ru/rozrobka-sajtiv/', html)
        self.assertIn('https://www.prometeylabs.com/static/images/og-image.jpg', html)
        self.assertIn('twitter:card', html)
        self.assertIn('property="og:image"', html)
        self.assertNotIn('від 250 €', html)

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
