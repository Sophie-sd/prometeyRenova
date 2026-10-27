"""ТЗ 27.10.2026: /rozrobka-sajtiv/ (UA + RU) — new block order, anchors, forms, embedded calculator."""
import re
from decimal import Decimal
from unittest import mock

from django.test import TestCase

from apps.core.fx_models import ExchangeRateSettings

PAGES = {'uk': '/rozrobka-sajtiv/', 'ru': '/ru/rozrobka-sajtiv/'}
BLOCK_ORDER = ['why', 'rs-form-1', 'economy', 'rs-calc-strip', 'portfolio', 'rs-form-2', 'faq', 'pl-rs-calc']
ADS_ANCHORS = ['pl-rs-products-title', 'pl-rs-calc', 'pl-rs-admin-title', 'pl-rs-work-title']
H2 = {
    'uk': [
        'Чому варто обрати',
        'безкоштовна консультація і розрахунок вартості',
        'Що входить у розробку під ключ',
        'Хочете зробити сайт, але не знаєте бюджет?',
        'Наші роботи — сайти від веб-студії PrometeyLabs',
        'обговоримо ваш проєкт безкоштовно',
        'Часті питання про розробку сайтів',
        'Порахуйте бюджет до дзвінка',
    ],
    'ru': [
        'Почему стоит выбрать',
        'бесплатная консультация и расчёт стоимости',
        'Что входит в разработку под ключ',
        'Хотите сделать сайт, но не знаете бюджет?',
        'Наши работы — сайты от веб-студии PrometeyLabs',
        'обсудим ваш проект бесплатно',
        'Частые вопросы о разработке сайтов',
        'Посчитайте бюджет до звонка',
    ],
}


def _rates():
    ExchangeRateSettings.objects.update_or_create(
        pk=1,
        defaults={'uah_per_eur': Decimal('40'), 'usd_per_eur': Decimal('1.085'), 'czk_per_eur': Decimal('25')},
    )


def _main(html):
    return html[html.index('<main'):html.index('</main>')]


def _section(html, sid):
    start = html.index(f'id="{sid}"')
    start = html.rindex('<section', 0, start)
    return html[start:html.index('</section>', start)]


class RozrobkaStructureTests(TestCase):
    def setUp(self):
        _rates()

    def test_block_order_and_h2(self):
        for lang, path in PAGES.items():
            with self.subTest(lang=lang):
                main = _main(self.client.get(path).content.decode())
                positions = [main.index(f'id="{sid}"') for sid in BLOCK_ORDER]
                self.assertEqual(positions, sorted(positions))
                self.assertLess(main.index('class="pl-rs__hero"'), positions[0])
                h2s = [re.sub(r'<[^>]+>', '', h) for h in re.findall(r'<h2[^>]*>(.*?)</h2>', main, re.S)]
                self.assertEqual(len(h2s), len(H2[lang]), h2s)
                for got, want in zip(h2s, H2[lang]):
                    self.assertIn(want, got)
                self.assertEqual(main.count('<h1'), 1)

    def test_ads_anchors_exactly_once(self):
        for lang, path in PAGES.items():
            html = self.client.get(path).content.decode()
            for anchor in ADS_ANCHORS + ['why', 'economy', 'faq']:
                with self.subTest(lang=lang, anchor=anchor):
                    self.assertEqual(html.count(f'id="{anchor}"'), 1)
            # anchors sit on the right headings
            self.assertRegex(html, r'<h2[^>]*id="pl-rs-products-title"')
            self.assertRegex(html, r'<h2[^>]*id="pl-rs-admin-title"')
            self.assertRegex(html, r'<h2[^>]*id="pl-rs-work-title"')
            self.assertRegex(html, r'<section[^>]*id="pl-rs-calc"')

    def test_scroll_margin_for_anchors(self):
        from pathlib import Path

        css = Path('static/css/pages/rozrobka-sajtiv.css').read_text(encoding='utf-8')
        for anchor in ADS_ANCHORS:
            self.assertIn(f'#{anchor}', css)
        self.assertIn('scroll-margin-top:calc(var(--pl-header-offset', css.replace(' ', ''))

    def test_removed_blocks_absent(self):
        for lang, path in PAGES.items():
            with self.subTest(lang=lang):
                main = _main(self.client.get(path).content.decode())
                for marker in ('pl-rs__section--services', 'id="types"', 'id="process"', 'id="guarantee"',
                               'pl-rs__section--admin', 'id="contacts"', 'pl-rs__floats', 'ФОП',
                               'href="/corporate-website-v2/#', 'href="/internet-shop-v2/#', '/telegram-bot/#pakety'):
                    self.assertNotIn(marker, main)

    def test_calc_ctas_scroll_to_embedded_calc(self):
        for lang, path in PAGES.items():
            with self.subTest(lang=lang):
                html = self.client.get(path).content.decode()
                for position in ('hero', 'why', 'mid'):
                    tag = re.search(r'<a[^>]*data-calc-cta="%s"[^>]*>' % position, html).group(0)
                    self.assertIn('href="#pl-rs-calc"', tag)
                    self.assertIn('data-calc-scroll="#pl-rs-calc"', tag)
                    self.assertIn('data-calc-page="rozrobka"', tag)
                self.assertNotIn('/calculator/?start=1', _main(html))

    def test_sticky_desktop_no_arrow_and_event(self):
        for lang, path in PAGES.items():
            with self.subTest(lang=lang):
                html = self.client.get(path).content.decode()
                wrap = re.search(r'<div class="pl-calc-sticky[^>]*>', html).group(0)
                self.assertIn('data-calc-sticky-desktop', wrap)
                self.assertIn('data-calc-target="#pl-rs-calc"', wrap)
                block = html[html.index(wrap):]
                block = block[:block.index('</div>')]
                self.assertNotIn('pl-calc-cta__arrow', block)
                self.assertIn('data-calc-event="sticky_cta_click"', block)
                label = 'Розрахуйте вартість онлайн' if lang == 'uk' else 'Рассчитайте стоимость онлайн'
                self.assertIn(f'<span class="pl-calc-cta__label">{label}</span>', block)


class RozrobkaPortfolioTests(TestCase):
    def setUp(self):
        _rates()

    def test_ten_cards_no_external_links(self):
        expected = ['fpsu', 'elit-fasad', 'diodi', 'grand-oblik', 'playvision',
                    'phoenixvet', 'queendrive', 'beauty-opt', 'znomax', 'fortprint']
        for lang, path in PAGES.items():
            with self.subTest(lang=lang):
                block = _section(self.client.get(path).content.decode(), 'pl-rs-work-title')
                self.assertEqual(re.findall(r'data-rs-case="([^"]+)"', block), expected)
                hrefs = re.findall(r'href="([^"]+)"', block)
                self.assertTrue(hrefs)
                portfolio = '/portfolio/' if lang == 'uk' else '/ru/portfolio/'
                self.assertEqual(set(hrefs), {portfolio})
                self.assertNotIn('Beauty Cake', block)
                imgs = re.findall(r'<img[^>]*portfolio/screens/[^>]*>', block)
                self.assertEqual(len(imgs), 10)
                for img in imgs:
                    self.assertIn('loading="lazy"', img)
                    self.assertIn('width="', img)
                    self.assertIn('height="', img)

    def test_ru_names_translated(self):
        block = _section(self.client.get(PAGES['ru']).content.decode(), 'pl-rs-work-title')
        for text in ('ДиОДи', 'Гранд Учёт', 'Феникс', 'ПОДГОТОВКА К НМТ'):
            self.assertIn(text.lower(), block.lower())


class RozrobkaLeadFormsTests(TestCase):
    def setUp(self):
        _rates()

    def test_form_1_and_2_hidden_fields(self):
        details = {
            'uk': ('Сторінка: Розробка сайтів · Форма №1 (після «Чому варто обрати»)',
                   'Сторінка: Розробка сайтів · Форма №2 (після «Наші роботи»)'),
            'ru': ('Страница: Разработка сайтов · Форма №1 (после «Почему стоит выбрать»)',
                   'Страница: Разработка сайтов · Форма №2 (после «Наши работы»)'),
        }
        for lang, path in PAGES.items():
            html = self.client.get(path).content.decode()
            for idx, sid in enumerate(('rs-form-1', 'rs-form-2')):
                with self.subTest(lang=lang, form=sid):
                    block = _section(html, sid)
                    action = '/forms/submit/' if lang == 'uk' else '/ru/forms/submit/'
                    self.assertIn(f'action="{action}"', block)
                    self.assertIn('name="form_type" value="site_request"', block)
                    self.assertIn('name="source_page" value="rozrobka-sajtiv"', block)
                    self.assertIn(f'name="details" value="{details[lang][idx]}"', block)
                    self.assertEqual(len(re.findall(r'type="tel"', block)), 1)
                    self.assertIn('name="name"', block)

    @mock.patch('apps.core.views._dispatch_async')
    def test_form_submit_redirects_to_thank_you(self, _dispatch):
        from apps.core.models import FormSubmission

        response = self.client.post('/forms/submit/', {
            'form_type': 'site_request',
            'source_page': 'rozrobka-sajtiv',
            'details': 'Сторінка: Розробка сайтів · Форма №1 (після «Чому варто обрати»)',
            'name': 'Безкоштовна консультація',
            'phone': '+380671234567',
        })
        data = response.json()
        self.assertTrue(data['success'], data)
        self.assertEqual(data['redirect'], '/thank-you/')
        row = FormSubmission.objects.get()
        self.assertEqual(row.extra_data.get('source_page'), 'rozrobka-sajtiv')
        self.assertIn('Форма №1', row.details)


class RozrobkaEmbeddedCalcTests(TestCase):
    def setUp(self):
        _rates()

    def test_embedded_test_ids_unique_and_no_price(self):
        for lang, path in PAGES.items():
            with self.subTest(lang=lang):
                html = self.client.get(path).content.decode()
                for dom_id in ('test-section', 'calculator-test', 'test-name', 'test-phone', 'calc-step-nav', 'pl-rs-calc'):
                    self.assertEqual(html.count(f'id="{dom_id}"'), 1, dom_id)
                block = _section(html, 'pl-rs-calc')
                self.assertIn('id="calculator-test"', block)
                self.assertIn('name="source_page" value="rozrobka-sajtiv"', block)
                for token in ('€', '₴', 'грн'):
                    self.assertNotIn(token, block)
                self.assertIn('href="https://t.me/prometeylabs"', block)
                self.assertIn('href="tel:+380639520565"', block)
                self.assertNotIn('Відкрити калькулятор', block)
                self.assertIn('calculator.js', html)
                self.assertRegex(html, r'<script[^>]*src="[^"]*calculator\.js[^"]*"[^>]*defer')

    @mock.patch('apps.core.views._dispatch_async')
    def test_forms_test_saves_details_and_redirects(self, _dispatch):
        from apps.core.models import FormSubmission

        response = self.client.post('/forms/test/', {
            'name': 'TEST не дзвонити',
            'phone': '+380671234567',
            'question_1': 'landing',
            'source_page': 'rozrobka-sajtiv',
            'details': 'Сторінка: Розробка сайтів · Вбудований калькулятор',
        })
        data = response.json()
        self.assertTrue(data['success'], data)
        self.assertEqual(data['redirect'], '/thank-you/')
        row = FormSubmission.objects.get()
        self.assertEqual(row.extra_data.get('source_page'), 'rozrobka-sajtiv')
        self.assertIn('Вбудований калькулятор', row.details + str(row.extra_data))

    def test_calculator_page_still_renders_test(self):
        for path in ('/calculator/', '/ru/calculator/'):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                self.assertEqual(html.count('id="calculator-test"'), 1)
                self.assertEqual(html.count('id="test-section"'), 1)
                self.assertNotIn('name="source_page" value="rozrobka-sajtiv"', html)


class ContactWidgetAndSharedComponentsTests(TestCase):
    def setUp(self):
        _rates()

    def test_contact_widget_opens_call_request_modal(self):
        for path, label in (('/', 'Замовити дзвінок'), ('/ru/', 'Заказать звонок'),
                            ('/rozrobka-sajtiv/', 'Замовити дзвінок'), ('/ru/rozrobka-sajtiv/', 'Заказать звонок')):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                btn = re.search(r'<button[^>]*id="contact-widget-toggle"[^>]*>', html, re.S).group(0)
                self.assertIn('data-modal="call-request-modal"', btn)
                self.assertIn(f'aria-label="{label}"', btn)
                self.assertNotIn('id="contact-widget-panel"', html)
                self.assertNotIn('contact-widget__item', html)
                self.assertIn('id="call-request-modal"', html)

    def test_corporate_v2_shared_blocks_unchanged(self):
        for path in ('/corporate-website-v2/', '/ru/corporate-website-v2/'):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                self.assertEqual(html.count('id="free-analysis"'), 1)
                self.assertEqual(html.count('id="calc-promo"'), 1)
                self.assertEqual(html.count('id="economy"'), 1)
                self.assertIn('id="pl-corp-economy-title"', html)
                self.assertIn('value="corporate-website-v2-free-analysis"', html)
                self.assertNotIn('rozrobka-sajtiv', _section(html, 'free-analysis'))

    def test_home_why_keeps_default_ids(self):
        html = self.client.get('/').content.decode()
        self.assertEqual(html.count('id="hf-why-title"'), 1)
        self.assertIn('id="fx-switch-home"', html)
        self.assertNotIn('pl-rs-products-title', html)
