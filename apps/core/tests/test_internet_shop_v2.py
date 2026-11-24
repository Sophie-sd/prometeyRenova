"""/internet-shop-v2/ (UA) і /ru/internet-shop-v2/ — Ads-спека: hero з формою, пакети, гарантія."""
import json
import re
from decimal import Decimal
from unittest import mock

from django.test import TestCase

from apps.core.fx_models import ExchangeRateSettings

UA = '/internet-shop-v2/'
RU = '/ru/internet-shop-v2/'

SPEC = {
    UA: {
        # SEO 2026-11-03: title 50–60 chars, keyword first (apps.core.seo.META_OVERRIDES).
        'title': 'Інтернет-магазин під ключ від 650 € — запуск за 3 тижні',
        'h1': '<span class="pl-shop__title-line">Створення інтернет-магазину</span> <span class="pl-shop__title-line">під ключ</span>',
        'line': 'Розробка <span class="pl-shop__nowrap">інтернет-магазину</span> <strong class="pl-shop__hero-acc">від 650 €</strong> · запуск <strong class="pl-shop__hero-acc">за 3 тижні</strong> · 1 рік підтримки безкоштовно · пожиттєва гарантія на код',
        'cta': 'Розрахувати вартість магазину',
        'sticky': 'Розрахуйте вартість онлайн',
        'trust': '5,0 ★ на Google\u00a0· 51 відгук\u00a0· 50+ запущених проєктів',
        'lead': 'Дизайн, код і інтеграції. Без плагінів і без щомісячної абонплати. Магазин залишається вашим.',
        'labels': ('Ім’я', 'Телефон'),
        'button': 'Розрахувати вартість магазину',
        'action': '/forms/submit/',
        'meta': ('650 €', '3 тижні', '1 рік підтримки безкоштовно'),
        'start': ['Дизайн', 'Мобільна версія', 'Базова SEO', 'LiqPay і Mono', 'Нова Пошта',
                  'Адмінка', '1 рік підтримки · пожиттєва гарантія на код', 'Каталог до 100 товарів'],
        'business': ['CRM', 'Telegram-сповіщення', 'Ролі менеджерів в адмінці', 'Онлайн-оплати',
                     'Інтеграції доставки', 'Налаштування рекламного кабінету і стартова кампанія'],
        'scale_keep': 'ШІ-адміністратор сайту',
        'plat_desc': 'Інтернет-магазин з CRM, рекламними кабінетами, SEO і пів року контенту',
        'plat_lead': 'Від вітрини до перших рекламних кампаній — одним пакетом.',
        'plat_note': 'У ціні сам магазин і запуск послуг. Рекламний бюджет оплачується окремо.',
        'plat_groups': ['Магазин', 'Продажі', 'Реклама', 'Пошук і контент'],
        'offers': ['Магазин', 'Магазин з інтеграціями', 'Магазин і маркетинг'],
        'reviews': ('відгук', 'google maps'),
        'garant_h2': 'Ми створюємо — ми й відповідаємо.',
        'garant': ['1 рік безкоштовної підтримки', 'Пожиттєва гарантія на код'],
        'drop': ['Парсинг постачальників', 'Оновлення цін і залишків', 'Передача замовлень', 'Облік маржі'],
        'from': 'від',
        'banned': ('5 років', 'запуск за 7 днів', 'запуск за 2 тижні', '1 рік гарантії', 'до 2 тижнів', 'Завжди.'),
        'quiz_fast': 'Якнайшвидше (близько 3 тижнів)',
        'name_ld': 'Створення інтернет-магазину під ключ',
    },
    RU: {
        'title': 'Интернет-магазин под ключ от 650 € — запуск за 3 недели',
        'h1': '<span class="pl-shop__title-line">Создание интернет-магазина</span> <span class="pl-shop__title-line">под ключ</span>',
        'line': 'Разработка <span class="pl-shop__nowrap">интернет-магазина</span> <strong class="pl-shop__hero-acc">от 650 €</strong> · запуск <strong class="pl-shop__hero-acc">за 3 недели</strong> · 1 год поддержки бесплатно · пожизненная гарантия на код',
        'cta': 'Рассчитать стоимость магазина',
        'sticky': 'Рассчитайте стоимость онлайн',
        'trust': '5,0 ★ в Google\u00a0· 51 отзыв\u00a0· 50+ запущенных проектов',
        'lead': 'Дизайн, код и интеграции. Без плагинов и без ежемесячной абонплаты. Магазин остаётся вашим.',
        'labels': ('Имя', 'Телефон'),
        'button': 'Рассчитать стоимость магазина',
        'action': '/ru/forms/submit/',
        'meta': ('650 €', '3 недели', '1 год поддержки бесплатно'),
        'start': ['Дизайн', 'Мобильная версия', 'Базовое SEO', 'LiqPay и Mono', 'Новая Почта',
                  'Админка', '1 год поддержки · пожизненная гарантия на код', 'Каталог до 100 товаров'],
        'business': ['CRM', 'Telegram-уведомления', 'Роли менеджеров в админке', 'Онлайн-оплаты',
                     'Интеграции доставки', 'Настройка рекламного кабинета и стартовая кампания'],
        'scale_keep': 'ИИ-администратор сайта',
        'plat_desc': 'Интернет-магазин с CRM, рекламными кабинетами, SEO и полгода контента',
        'plat_lead': 'От витрины до первых рекламных кампаний — одним пакетом.',
        'plat_note': 'В цене сам магазин и запуск услуг. Рекламный бюджет оплачивается отдельно.',
        'plat_groups': ['Магазин', 'Продажи', 'Реклама', 'Поиск и контент'],
        'offers': ['Магазин', 'Магазин с интеграциями', 'Магазин и маркетинг'],
        'reviews': ('отзыв', 'google maps'),
        'garant_h2': 'Мы создаём — мы и отвечаем.',
        'garant': ['1 год бесплатной поддержки', 'Пожизненная гарантия на код'],
        'drop': ['Парсинг поставщиков', 'Обновление цен и остатков', 'Передача заказов', 'Учёт маржи'],
        'from': 'от',
        'banned': ('5 лет', 'за 7 дней', 'за 2 недели', '1 год гарантии', 'до 2 недель', 'Всегда.'),
        'quiz_fast': 'Как можно скорее (около 3 недель)',
        'name_ld': 'Создание интернет-магазина под ключ',
    },
}


def _between(html, start, end):
    a = html.index(start)
    return html[a:html.index(end, a)]


def _list_after(html, marker):
    block = _between(html, marker, '</ul>')
    return re.findall(r'<li>([^<]+)</li>', block)


class ShopV2SpecTests(TestCase):
    def setUp(self):
        ExchangeRateSettings.objects.update_or_create(pk=1, defaults={
            'uah_per_eur': Decimal('51.45'),
            'usd_per_eur': Decimal('1.085'),
            'czk_per_eur': Decimal('25'),
        })

    def _get(self, url, **cookies):
        for k, v in cookies.items():
            self.client.cookies[k] = v
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_head_title_meta_and_json_ld(self):
        for url, s in SPEC.items():
            html = self._get(url)
            self.assertIn(f'<title>{s["title"]}</title>', html, url)
            desc = re.search(r'<meta name="description"\s+content="([^"]*)"', html).group(1)
            og = re.search(r'<meta property="og:title" content="([^"]*)"', html).group(1)
            self.assertEqual(og, s['title'], url)
            for part in s['meta']:
                self.assertIn(part, desc, url)
            lds = [json.loads(m) for m in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
            service = [d for d in lds if d.get('@type') == 'Service']
            self.assertEqual(len(service), 1, url)
            self.assertEqual(service[0]['name'], s['name_ld'])
            self.assertEqual(service[0]['url'], 'https://www.prometeylabs.com' + url)
            offers = service[0]['offers']
            self.assertEqual([(o['@type'], o['name'], o['price'], o['priceCurrency']) for o in offers],
                             [('Offer', name, price, 'EUR') for name, price in zip(s['offers'], ('650', '1500', '7000'))],
                             url)
            for o in offers:
                self.assertTrue(o.get('description'), url)
            self.assertNotIn('highPrice', html, url)
            self.assertNotIn('AggregateOffer', html, url)
            # 7 000 € must not leak into title / H1 / meta
            head_bits = [s['title'], desc, og, re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S).group(1)]
            for bit in head_bits:
                self.assertNotRegex(bit, r'7[\s\u00a0]?000', url)

    def test_hero_copy_form_and_contacts(self):
        for url, s in SPEC.items():
            html = self._get(url)
            hero = _between(html, 'id="top"', 'id="portfolio"')
            self.assertEqual(html.count('<h1'), 1, url)
            self.assertIn(f'id="pl-shop-hero-title" class="pl-shop__title pl-shop__title--hero">{s["h1"]}</h1>', hero)
            self.assertIn(f'<p class="pl-shop__hero-line">{s["line"]}</p>', hero)
            self.assertIn(f'<p class="pl-shop__hero-lead">{s["lead"]}</p>', hero)
            # ТЗ 27.10.2026 п. 4.1–4.2: без видимих крошок і без форми в hero; CTA → квіз #zayavka.
            self.assertNotIn('<form', hero, url)
            self.assertNotIn('pl-ads-crumbs', hero, url)
            self.assertIn('"BreadcrumbList"', html, url)
            card = _between(hero, 'class="pl-shop__hero-card"', '</section>')
            self.assertIn('href="#zayavka" class="pl-calc-cta__btn mobile-touch-target" data-calc-cta="hero" data-calc-page="shop" data-calc-scroll="#zayavka"', card)
            self.assertIn(f'<span class="pl-calc-cta__label">{s["cta"]}</span>', card)
            self.assertNotIn('pl-calc-cta__micro', card)
            self.assertIn('data-calc-event="sticky_cta_click"', card)
            self.assertIn(f'<span class="pl-calc-cta__label">{s["sticky"]}</span></a>', card)
            trust = _between(card, 'class="pl-shop__hero-trust"', '</p>')
            self.assertIn(s['trust'], trust)
            contacts = _between(hero, 'class="pl-shop__hero-contacts"', '</p>')
            self.assertIn('href="tel:+380639520565"', contacts)
            self.assertIn('+38 (063) 952-05-65', contacts)
            self.assertIn('href="https://t.me/prometeylabs"', contacts)
            self.assertIn('>Telegram</a>', contacts)

    def test_hero_price_is_plain_text_and_ignores_currency(self):
        for url, s in SPEC.items():
            html = self._get(url, pl_currency='UAH')
            hero = _between(html, 'id="top"', 'id="portfolio"')
            self.assertIn(s['line'], hero)
            self.assertNotIn('fx-', hero)
            self.assertNotIn('hx-', hero)
            self.assertNotIn('₴', hero)
            # packages still follow FX
            self.assertIn(f'{s["from"]} 33\u00a0443 ₴', html)

    def test_no_developer_modal_and_no_lang_suggest(self):
        for url in SPEC:
            html = self._get(url)
            self.assertNotIn('id="developer-modal"', html, url)
            self.assertNotIn('id="lang-suggest"', html, url)
            self.assertNotIn('lang-suggest.js', html, url)
            self.assertIn('id="call-request-modal"', html, url)
        self.assertIn('id="developer-modal"', self._get('/'))
        self.assertIn('id="lang-suggest"', self._get('/ru/'))

    def test_packages_content(self):
        for url, s in SPEC.items():
            html = self._get(url)
            pak = _between(html, 'id="pakety"', '</section>')
            self.assertEqual(_list_after(pak, '<article class="pl-shop__pkg-card">'), s['start'], url)
            self.assertEqual(_list_after(pak, 'pl-shop__pkg-card--featured'), s['business'], url)
            self.assertNotIn('pl-shop-pkg-extra-premium', pak)
            self.assertIn(s['scale_keep'], pak)
            self.assertIn(f'id="fx-pkg-base" class="pl-shop__pkg-price">{s["from"]} 650 €', pak)
            self.assertIn(f'id="fx-pkg-premium" class="pl-shop__pkg-price">{s["from"]} 1\u00a0500 €', pak)
            self.assertIn(f'id="fx-pkg-platinum" class="pl-shop__pkg-price">{s["from"]} 7\u00a0000 €', pak)
            self.assertEqual(pak.count(f'>{s["button"]}</a>'), 3, url)

    def test_platinum_is_shop_plus_marketing_and_no_review_services(self):
        for url, s in SPEC.items():
            html = self._get(url)
            plat = _between(html, 'pl-shop__pkg-card--platinum', '</article>')
            self.assertIn(f'<p class="pl-shop__pkg-desc">{s["plat_desc"]}</p>', plat)
            self.assertIn(f'<p class="pl-shop__pkg-lead">{s["plat_lead"]}</p>', plat)
            self.assertIn(f'<p class="pl-shop__pkg-note">{s["plat_note"]}</p>', plat)
            self.assertEqual(re.findall(r'<strong class="pl-shop__pkg-theme-name">([^<]+)</strong>', plat),
                             s['plat_groups'], url)
            self.assertEqual(plat.count('data-calc-pkg='), 1, url)
            self.assertIn(f'>{s["button"]}</a>', plat)
            self.assertNotIn('pl-shop__pkg-read-more', plat)
            plat_low = plat.lower()
            for bad in s['reviews']:
                self.assertNotIn(bad, plat_low, f'{url}: {bad}')
            low = html.lower()
            for bad in ('кінематограф', 'кинематограф'):
                self.assertNotIn(bad, low, f'{url}: {bad}')
            # visible card eyebrows = JSON-LD Offer names (message match page <-> schema)
            pak = _between(html, 'id="pakety"', '</section>')
            self.assertEqual(re.findall(r'<span class="pl-shop__pkg-eyebrow">([^<]+)</span>', pak), s['offers'], url)
            self.assertNotIn('Не лише сайт', html)
            self.assertNotIn('Не только сайт', html)
            matrix = _between(html, 'class="pl-shop__pkg-matrix-table"', '</table>')
            groups = re.findall(r'<th scope="rowgroup" colspan="4">([^<]+)</th>', matrix)
            self.assertEqual(groups, s['plat_groups'], url)

    def test_guarantee_two_points_and_banned_strings(self):
        for url, s in SPEC.items():
            html = self._get(url)
            gar = _between(html, 'id="garantiya"', '</section>')
            self.assertIn(f'>{s["garant_h2"]}</h2>', gar)
            titles = re.findall(r'<p class="pl-shop__garant-box-title">([^<]+)</p>', gar)
            self.assertEqual(titles, s['garant'], url)
            low = html.lower()
            for bad in s['banned']:
                self.assertNotIn(bad.lower(), low, f'{url}: {bad}')
            self.assertIn(s['quiz_fast'], html)

    def test_anchors_and_dropshipping(self):
        for url, s in SPEC.items():
            html = self._get(url)
            for anchor in ('pakety', 'portfolio', 'zayavka', 'dropshipping'):
                self.assertEqual(html.count(f'id="{anchor}"'), 1, f'{url} #{anchor}')
            self.assertIn('id="pl-shop-quiz-form"', _between(html, 'id="zayavka"', '</section>'))
            drop = _between(html, 'id="dropshipping"', '</section>')
            self.assertIn(f'{s["from"]} 1\u00a0500 €', drop)
            self.assertEqual(re.findall(r'<li>([^<]+)</li>', drop), s['drop'], url)
        self.assertEqual(self.client.get('/dropshipping/').status_code, 404)

    def test_ru_footer_monobank_translated(self):
        html = self._get(RU)
        self.assertIn('>Покупка частями monobank</a>', html)
        self.assertIn('>Покупка частинами monobank</a>', self._get(UA))


class ShopV2HeroFormSubmitTests(TestCase):
    @mock.patch('apps.core.views._dispatch_async')
    def test_hero_form_post_redirects_to_thank_you(self, dispatch):
        from apps.core.models import FormSubmission
        for url, path in ((UA, '/forms/submit/'), (RU, '/ru/forms/submit/')):
            response = self.client.post(path, {
                'form_type': 'site_request',
                'source_page': 'internet-shop-v2',
                'details': 'hero',
                'name': 'Тест',
                'phone': '+380671234567',
            })
            self.assertEqual(response.status_code, 200, path)
            data = response.json()
            self.assertTrue(data['success'], data)
            self.assertEqual(data['redirect'], '/thank-you/')
        self.assertEqual(dispatch.call_count, 2)
        self.assertEqual(FormSubmission.objects.count(), 2)


class ShopV2EnglishTests(TestCase):
    """EN /internet-shop-v2/ uses the approved English copy; uk and ru stay put."""

    EN = '/en/internet-shop-v2/'
    EN_TITLE = 'Turnkey online store development — price from €650 | PrometeyLabs'
    EN_H1 = '<span class="pl-shop__title-line">Turnkey online store</span> <span class="pl-shop__title-line">development</span>'
    HIDDEN_DETAILS = 'Сторінка: Інтернет-магазини · Форма №1 (після «Переросли Prom»)'

    def _get(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        return response.content.decode()

    def test_en_copy_and_uk_ru_unchanged(self):
        html = self._get(self.EN)
        self.assertIn(f'<title>{self.EN_TITLE}</title>', html)
        self.assertIn('from €650', html)
        self.assertIn('from €1,500', html)
        self.assertIn('from €7,000', html)
        self.assertNotIn('650 €', html)
        self.assertIn(
            f'id="pl-shop-hero-title" class="pl-shop__title pl-shop__title--hero">{self.EN_H1}</h1>',
            html,
        )
        for banned in (
            'Створення інтернет-магазину',
            'Часті питання',
            'Розрахувати вартість магазину',
        ):
            self.assertNotIn(banned, html, banned)
        self.assertIn('noindex, follow', html)
        self.assertIn(f'value="{self.HIDDEN_DETAILS}"', html)
        self.assertIn('Frequently asked questions about creating an online store', html)
        self.assertIn('Calculate the store cost', html)
        self.assertNotIn('Take the quiz in 1 minute', html)
        self.assertIn('5.0 ★ on Google\u00a0· 51 reviews\u00a0· 50+ launched projects', html)
        self.assertIn('How much does it cost to create an online store', html)
        self.assertIn('The warranty is set out in the public contract (clause 8 of the offer)', html)
        self.assertIn('>offer</a>', html)

        blocks = [json.loads(chunk) for chunk in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S,
        )]
        crumbs = next(block for block in blocks if block.get('@type') == 'BreadcrumbList')
        items = crumbs['itemListElement']
        self.assertEqual([item['name'] for item in items], ['Home', 'E-commerce stores'])
        for item in items:
            self.assertIn('/en/', item['item'])
        faq = next(block for block in blocks if block.get('@type') == 'FAQPage')
        self.assertEqual(
            faq['mainEntity'][-1]['acceptedAnswer']['text'],
            'We build the admin panel ourselves, in any language you need — English, Ukrainian or another: '
            'a new manager will master it in 15 minutes. Stock and price updates and order processing — in 1–2 clicks.',
        )
        org = next(
            block for block in blocks
            if 'Organization' in (block.get('@type') if isinstance(block.get('@type'), list) else [block.get('@type')])
        )
        self.assertEqual(org['address']['streetAddress'], '46a Taras Shevchenko Blvd')
        self.assertEqual(org['address']['addressLocality'], 'Kyiv')

        uk = self._get(UA)
        self.assertIn(f'<title>{SPEC[UA]["title"]}</title>', uk)
        self.assertIn(SPEC[UA]['h1'], uk)
        self.assertNotIn(self.EN_TITLE, uk)
        ru = self._get(RU)
        self.assertIn(f'<title>{SPEC[RU]["title"]}</title>', ru)
        self.assertIn(SPEC[RU]['h1'], ru)
        self.assertNotIn(self.EN_TITLE, ru)


class ShopV2VideoIntroTests(TestCase):
    """Секція під hero. Картки №4 і №5 відкривають діалог з обкладинки."""

    def test_placeholder_follows_hero(self):
        expect = {
            UA: ('Як ми робимо', 'Широке портфоліо інтернет-магазинів на різну тематику', 'Замовити консультацію'),
            RU: ('Как мы делаем', 'Широкое портфолио интернет-магазинов разной тематики', 'Заказать консультацию'),
            '/en/internet-shop-v2/': ('How we build', 'A wide portfolio of online stores in different niches', 'Request a consultation'),
        }
        for url, (how, fact, btn) in expect.items():
            html = self.client.get(url).content.decode()
            video = html.index('id="yak-my-robymo"')
            self.assertLess(html.index('id="top"'), video, url)
            self.assertLess(video, html.index('id="portfolio"'), url)
            block = html[video:html.index('id="portfolio"', video)]
            self.assertIn(how, block, url)
            self.assertIn(fact, block, url)
            self.assertIn('>' + btn + '<', block, url)
            self.assertIn('data-modal="call-request-modal"', block, url)
            self.assertIn('>00:47<', block, url)
            self.assertIn('pl-rs-video__poster', block, url)
            self.assertIn('images/internet-shop/video/shop-video-4.webp', block, url)
            self.assertIn('loading="lazy"', block, url)
            self.assertNotIn('<iframe', block, url)
            self.assertIn('data-rs-video="o4OvYDAMeGE"', block, url)
            self.assertIn('css/pages/shop-video.css?v=2', html, url)
            self.assertIn('css/components/pl-proof-blocks.css?v=4', html, url)
            self.assertIn('js/rozrobka-video.js?v=4', html, url)
            self.assertIn('data-rs-video-dialog', html, url)

    def test_packages_video_placeholder(self):
        titles = {
            UA: 'Що входить у пакети?',
            RU: 'Что входит в пакеты?',
            '/en/internet-shop-v2/': 'What’s included in the packages?',
        }
        for url, title in titles.items():
            html = self.client.get(url).content.decode()
            pak = html[html.index('id="pakety"'):html.index('id="svoboda"')]
            self.assertIn(title, pak, url)
            self.assertIn('>01:06<', pak, url)
            self.assertIn('pl-rs-video__poster', pak, url)
            self.assertIn('images/internet-shop/video/shop-video-5.webp', pak, url)
            self.assertIn('loading="lazy"', pak, url)
            self.assertNotIn('<iframe', pak, url)
            self.assertIn('data-rs-video="T3ldCTDRrrM"', pak, url)

    def test_video_ids_and_posters_in_context(self):
        for url in (UA, RU, '/en/internet-shop-v2/'):
            response = self.client.get(url)
            videos = response.context['shop_videos']
            self.assertEqual(videos['intro']['id'], 'o4OvYDAMeGE', url)
            self.assertEqual(videos['intro']['time'], '00:47', url)
            self.assertEqual(videos['intro']['poster'], 'images/internet-shop/video/shop-video-4.webp', url)
            self.assertEqual(videos['packages']['id'], 'T3ldCTDRrrM', url)
            self.assertEqual(videos['packages']['time'], '01:06', url)
            self.assertEqual(videos['packages']['poster'], 'images/internet-shop/video/shop-video-5.webp', url)


class ShopV2Round4Tests(TestCase):
    """Конструктор, смуга з формою, відео адмінки, відгуки, FAQ +2, опція квізу."""

    def test_sections(self):
        from apps.core.ads_copy import SHOP

        self.assertEqual(len(SHOP['uk']['faq']), 9)
        self.assertEqual(len(SHOP['ru']['faq']), 9)
        self.assertEqual(len(SHOP['en']['faq']), 9)
        pages = {
            UA: (
                'Конструктор чи магазин під ключ:',
                'що вам підходить?',
                'Графік роботи: цілодобово',
                'Дропшиппінг-платформа',
                'Чому не зробити сайт у конструкторі? Це ж швидше.',
            ),
            RU: (
                'Конструктор или магазин под ключ:',
                'что вам подходит?',
                'График работы: круглосуточно',
                'Дропшиппинг-платформа',
                'Почему не сделать сайт в конструкторе? Это же быстрее.',
            ),
            '/en/internet-shop-v2/': (
                'Website builder or turnkey online store:',
                'which one suits you?',
                'Working hours: 24/7',
                'Dropshipping platform',
                'Why not build the site in a website builder?',
            ),
        }
        for url, (h2, h2b, hours, drop, faq) in pages.items():
            html = self.client.get(url).content.decode()
            sv = html[html.index('id="svoboda"'):html.index('id="forma-1"')]
            self.assertIn(h2, sv, url)
            self.assertIn(h2b, sv, url)
            self.assertIn('100 000+', sv, url)
            self.assertNotIn('Переросли', sv, url)
            strip = html[html.index('id="rozrahunok"'):html.index('id="rs-reviews"')]
            self.assertIn('<form', strip, url)
            self.assertIn('name="phone"', strip, url)
            self.assertIn(hours, strip, url)
            admin = html[html.index('id="pl-shop-admin-title"'):html.index('id="dropshipping"')]
            self.assertIn('data-rs-video="giim7h-DlVg"', admin, url)
            self.assertIn('id="rs-reviews"', html, url)
            quiz = html[html.index('id="zayavka"'):html.index('class="main-footer"')]
            self.assertIn(drop, quiz, url)
            self.assertIn('pl-shop__quiz-option-tick', quiz, url)
            self.assertNotIn(hours, quiz, url)
            self.assertNotIn('4 коротких', quiz, url)
            self.assertNotIn('4 quick questions', quiz, url)
            self.assertNotIn('Залиште телефон — менеджер', quiz, url)
            self.assertNotIn('Оставьте телефон', quiz, url)
            self.assertNotIn('name the price based on your answers', quiz, url)
            self.assertIn(faq, html, url)
