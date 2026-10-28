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
        # ТЗ 27.10.2026 п. 3.1 / 3.10
        self.assertIn('Розробка сайтів під ключ. Створення сайтів від 250 €</h1>', html)
        self.assertIn('Замовте сайт для бізнесу: лендінг <span class="pl-rs__acc">від 250 € за 3–7 днів</span>', root)
        # ТЗ Софії 28.10.2026 п. 4.3: два фрагменти прибрано, рівно 4 помаранчеві акценти
        lead = root[root.index('<p class="pl-rs__lead">'):]
        lead = lead[:lead.index('</p>')]
        self.assertEqual(lead.count('class="pl-rs__acc"'), 4)
        self.assertNotIn('Ціну й строк фіксуємо в договорі.', lead)
        self.assertNotIn('адмінка залишається у вас', lead)
        # ТЗ Софії 28.10.2026 п. 4.1: форми в херо немає
        self.assertNotIn('id="pl-rs-hero-form"', html)
        self.assertNotIn('Розрахуємо вартість вашого сайту', root)
        self.assertIn('Ціна і строк у договорі · Адмінка залишається у вас · 50+ запущених проєктів</p>', root)
        self.assertNotIn('Відповідаємо протягом 15 хвилин', root)
        # price ranges live in «Чому варто обрати» (home component), not in hero floats
        self.assertIn('250–400 €', root)
        self.assertIn('500–700 €', root)
        self.assertIn('від 800 €', root)
        self.assertNotIn('800–1\u00a0400 €', root)
        self.assertIn('1\u00a0500–5\u00a0000 €', root)
        self.assertIn('3–7 днів', root)
        self.assertIn('7–14 днів', root)
        self.assertIn('14–30 днів', root)
        self.assertNotIn('pl-rs__floats', html)
        self.assertNotIn('fx-soft-float-', html)
        # canon warranty wording (wins over the ТЗ «рік підтримки безкоштовно»)
        self.assertIn('Пожиттєва гарантія на код, <span class="pl-rs__acc">1 рік безкоштовної підтримки</span>.', root)
        self.assertNotIn('1 рік гарантії', html)
        self.assertNotIn('5 років', root)
        self.assertNotIn('індивідуально', root)
        self.assertNotIn('окремий бриф', root)
        soft_hits = [s for s in ('SOFT', 'Soft ·', 'Soft —', 'орієнтири Soft') if s in html]
        self.assertEqual(soft_hits, [], soft_hits)
        self.assertIn('rozrobka-sajtiv.js', html)
        self.assertNotIn('pl-rs__links', root)
        self.assertNotIn('pl-rs__link--muted', root)
        self.assertIn('Написати в Telegram</a> · <a href="tel:+380639520565">+38 (063) 952-05-65</a>', root)
        self.assertNotIn('Зателефонувати прямо зараз', html)
        self.assertNotIn('pl-rs__cta-alt', root)
        self.assertIn('https://t.me/prometeylabs', html)
        self.assertIn('tel:+380639520565', html)
        # п. 3.3: old blocks and their outbound hash links are gone
        for gone in ('Ціни на розробку сайтів під ключ', 'який тип обрати', 'Гарантія і підтримка',
                     'Контакти PrometeyLabs', 'ФОП', 'pl-rs__products', 'pl-rs__section--admin',
                     'id="types"', 'id="process"', 'id="guarantee"', 'id="contacts"',
                     '#scale"', '#tech"', '/internet-shop-v2/#pakety', '/telegram-bot/#pakety'):
            self.assertNotIn(gone, root, gone)
        self.assertEqual(html.count('<h1'), 1)
        self.assertEqual(html.count('</h1>'), 1)

    def test_currency_switcher_defaults_to_euro(self):
        for path in ('/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/'):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                root = _landing_markup(html)
                self.assertIn('id="fx-switch-soft-why"', root)
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
        self.assertNotIn('id="fx-switch-soft"', body)
        self.assertIn('id="fx-switch-soft-why"', body)
        self.assertIn('hx-swap-oob="outerHTML"', body)
        self.assertIn('id="fx-home-prices"', body)

    def test_ru_mirror_has_euro_and_no_dollar_switcher(self):
        html = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        root = _landing_markup(html)
        self.assertIn('Разработка сайтов под ключ. Создание сайтов от 250 €</h1>', html)
        self.assertIn('Закажите сайт для бизнеса: лендинг <span class="pl-rs__acc">от 250 €', root)
        self.assertNotIn('id="pl-rs-hero-form"', html)
        self.assertNotIn('Рассчитаем стоимость вашего сайта', root)
        self.assertIn('Пожизненная гарантия на код, <span class="pl-rs__acc">1 год бесплатной поддержки</span>.', root)
        self.assertIn('Цена и срок в договоре · Админка остаётся у вас · 50+ запущенных проектов</p>', root)
        self.assertNotIn('Отвечаем в течение 15 минут', root)
        self.assertIn('€', root)
        self.assertIn('id="fx-switch-soft-why"', root)
        self.assertNotIn('data-currency="usd"', root)
        self.assertNotIn('pl-rs__cta-alt', root)
        self.assertNotIn('pl-rs__links', root)
        self.assertIn('tel:+380639520565', html)
        self.assertEqual(html.count('<h1'), 1)

    def test_seo_head(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertIn('Створити сайт під ключ — розробка сайтів від 250 € | PrometeyLabs', html)
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
        self.assertIn('Ціна і строк у договорі, рік підтримки безкоштовно.', html)

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
