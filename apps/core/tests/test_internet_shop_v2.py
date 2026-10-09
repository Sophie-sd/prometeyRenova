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
        'title': 'Створення інтернет-магазину під ключ від 800€ | PrometeyLabs',
        'h1': 'Створення інтернет-магазину під ключ',
        'line': 'Від 800€. Запуск за 3 тижні. 1 рік підтримки безкоштовно.',
        'lead': 'Дизайн, код і інтеграції. Без плагінів і без щомісячної абонплати. Магазин залишається вашим.',
        'labels': ('Ім’я', 'Телефон'),
        'button': 'Дізнатися вартість',
        'action': '/forms/submit/',
        'meta': ('800 €', '3 тижні', '1 рік підтримки'),
        'start': ['Дизайн', 'Мобільна версія', 'Базова SEO', 'LiqPay і Mono', 'Нова Пошта',
                  'Адмінка', '1 рік підтримки', 'Каталог до 100 товарів'],
        'business': ['CRM', 'Telegram-сповіщення', 'Ролі менеджерів в адмінці', 'Онлайн-оплати',
                     'Інтеграції доставки'],
        'scale_keep': 'ШІ-адміністратор сайту',
        'plat_desc': 'Інтернет-магазин з CRM, рекламними кабінетами, SEO і пів року контенту',
        'plat_lead': 'Від вітрини до перших рекламних кампаній — одним пакетом.',
        'plat_note': 'У ціні сам магазин і запуск послуг. Рекламний бюджет оплачується окремо.',
        'plat_groups': ['Магазин', 'Продажі', 'Реклама', 'Пошук і контент'],
        'offers': ['Магазин', 'Магазин з інтеграціями', 'Магазин і маркетинг'],
        'reviews': ('відгук', 'google maps'),
        'garant_h2': 'Ми створюємо — ми й відповідаємо.',
        'garant': ['1 рік безкоштовної підтримки', 'Гарантія на код без плагінів'],
        'drop': ['Парсинг постачальників', 'Оновлення цін і залишків', 'Передача замовлень', 'Облік маржі'],
        'from': 'від',
        'banned': ('5 років', 'запуск за 7 днів', 'запуск за 2 тижні', 'пожиттєв', 'до 2 тижнів', 'Завжди.'),
        'quiz_fast': 'Якнайшвидше (близько 3 тижнів)',
        'name_ld': 'Створення інтернет-магазину під ключ',
    },
    RU: {
        'title': 'Создание интернет-магазина под ключ от 800€ | PrometeyLabs',
        'h1': 'Создание интернет-магазина под ключ',
        'line': 'От 800€. Запуск за 3 недели. 1 год поддержки бесплатно.',
        'lead': 'Дизайн, код и интеграции. Без плагинов и без ежемесячной абонплаты. Магазин остаётся вашим.',
        'labels': ('Имя', 'Телефон'),
        'button': 'Узнать стоимость',
        'action': '/ru/forms/submit/',
        'meta': ('800 €', '3 недели', '1 год поддержки'),
        'start': ['Дизайн', 'Мобильная версия', 'Базовое SEO', 'LiqPay и Mono', 'Новая Почта',
                  'Админка', '1 год поддержки', 'Каталог до 100 товаров'],
        'business': ['CRM', 'Telegram-уведомления', 'Роли менеджеров в админке', 'Онлайн-оплаты',
                     'Интеграции доставки'],
        'scale_keep': 'ИИ-администратор сайта',
        'plat_desc': 'Интернет-магазин с CRM, рекламными кабинетами, SEO и полгода контента',
        'plat_lead': 'От витрины до первых рекламных кампаний — одним пакетом.',
        'plat_note': 'В цене сам магазин и запуск услуг. Рекламный бюджет оплачивается отдельно.',
        'plat_groups': ['Магазин', 'Продажи', 'Реклама', 'Поиск и контент'],
        'offers': ['Магазин', 'Магазин с интеграциями', 'Магазин и маркетинг'],
        'reviews': ('отзыв', 'google maps'),
        'garant_h2': 'Мы создаём — мы и отвечаем.',
        'garant': ['1 год бесплатной поддержки', 'Гарантия на код без плагинов'],
        'drop': ['Парсинг поставщиков', 'Обновление цен и остатков', 'Передача заказов', 'Учёт маржи'],
        'from': 'от',
        'banned': ('5 лет', 'за 7 дней', 'за 2 недели', 'пожизненн', 'до 2 недель', 'Всегда.'),
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
                             [('Offer', name, price, 'EUR') for name, price in zip(s['offers'], ('800', '1500', '7000'))],
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
            form = _between(hero, '<form', '</form>')
            self.assertIn('id="pl-shop-hero-form"', form)
            self.assertIn(f'action="{s["action"]}"', form)
            self.assertIn('method="post"', form)
            self.assertIn('data-form-type="site_request"', form)
            self.assertIn('name="csrfmiddlewaretoken"', form)
            self.assertIn('<input type="hidden" name="form_type" value="site_request">', form)
            self.assertIn('<input type="hidden" name="source_page" value="internet-shop-v2">', form)
            self.assertRegex(form, r'<input type="text" id="pl-shop-hero-name" name="name"[^>]*required')
            self.assertRegex(form, r'<input type="tel" id="pl-shop-hero-phone" name="phone"[^>]*required')
            for label in s['labels']:
                self.assertIn(f'>{label}</label>', form)
            self.assertIn(f'type="submit"', form)
            self.assertIn(f'>{s["button"]}</button>', form)
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
            self.assertIn(f'{s["from"]} 41\u00a0160 ₴', html)

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
            self.assertIn(f'id="fx-pkg-base" class="pl-shop__pkg-price">{s["from"]} 800 €', pak)
            self.assertIn(f'id="fx-pkg-premium" class="pl-shop__pkg-price">{s["from"]} 1\u00a0500 €', pak)
            self.assertIn(f'id="fx-pkg-platinum" class="pl-shop__pkg-price">{s["from"]} 7\u00a0000 €', pak)

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
            low = html.lower()
            for bad in s['reviews'] + ('кінематограф', 'кинематограф'):
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
