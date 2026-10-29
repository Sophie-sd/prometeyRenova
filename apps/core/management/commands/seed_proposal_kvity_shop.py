"""
Management command: seed_proposal_kvity_shop

КП №2 із пари «Квіти» (троянди, лаванда, саджанці), заявка kp-kvity/2026-10-29-001:
ІНТЕРНЕТ-МАГАЗИН під ключ — окрема ціна 1 200 € (канон сайту: магазин від 800 €), 30 днів.
З адмін-панеллю CMS (адмінка є лише тут, у лендингу її немає).
Демо — стандартний демо-магазин (provision_demo_shop), НЕ адаптований під клієнта.
На сторінці КП — дві кнопки демо «Лендинг» / «Інтернет-магазин» (Proposal.DEMO_PAIRS).
"""
import sys
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.core.management.commands._kvity_common import seed_rows
from apps.core.proposal_models import Proposal, ProposalSpec

SLUG = 'shop-kvity-r7l2'
CLIENT = 'Квіти: троянди, лаванда, саджанці (інтернет-магазин)'
DEMO_TENANT_SLUG = 'kvity-shop-8b54d0'
ISSUED_ON = date(2026, 10, 29)
ORDER = 50
KIND = Proposal.DemoKind.SHOP

TITLE = 'Інтернет-магазин квітів (троянди, лаванда, саджанці) під ключ'
LEAD = (
    'Повноцінний магазин з каталогом, кошиком, онлайн-оплатою, доставкою та власною '
    'адмін-панеллю CMS: ви самі керуєте цінами, наявністю, замовленнями й акціями.'
)
RECS_LEAD = (
    'Технічне завдання (індивідуальні деталі проєкту): онлайн-магазин зрізаних квітів, авторських '
    'букетів, сухоцвітів лаванди та посадкового матеріалу з адмін-панеллю CMS.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'Адмін-панель CMS'},
    {'order': 2, 'title': 'Онлайн-оплата · доставка'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Троянди · лаванда · букети · саджанці', 'is_accent': False},
    {'order': 1, 'title': 'Card', 'caption': 'Кількість · стебло · пакування', 'is_accent': True},
    {'order': 2, 'title': 'Checkout', 'caption': 'Дата/час · листівка · оплата', 'is_accent': False},
    {'order': 3, 'title': 'Delivery', 'caption': "Кур'єр · Нова Пошта", 'is_accent': False},
    {'order': 4, 'title': 'CMS', 'caption': 'Ціни · наявність · замовлення', 'is_accent': False},
]

MODULES = [
    {'number': 1, 'order': 0, 'title': 'Floral UI/UX дизайн',
     'description': 'Витончений інтерфейс під швидкий вибір квітів, букетів і саджанців зі смартфона й ПК.'},
    {'number': 2, 'order': 1, 'title': 'Каталог і картка товару',
     'description': ('Категорії (сортові троянди, лаванда, сезонні квіти, букети, саджанці), фільтри за '
                     'кольором, висотою та приводом.')},
    {'number': 3, 'order': 2, 'title': 'Кошик і доставка',
     'description': ("Оформлення в 1 екран: дата й інтервал доставки кур'єром, текст листівки. Саджанці — "
                     'Новою Поштою по Україні.')},
    {'number': 4, 'order': 3, 'title': 'Онлайн-оплата',
     'description': ('Еквайринг: Visa/Mastercard, Apple Pay, Google Pay. Договір еквайрингу клієнт '
                     'укладає з банком сам, ми підключаємо його до сайту.')},
    {'number': 5, 'order': 4, 'title': 'Адмін-панель CMS',
     'description': ('Повнофункціональна панель: замовлення, ціни, наявність квітів, нові позиції, банери '
                     'й акції до 14 лютого та 8 березня — без програмістів.')},
    {'number': 6, 'order': 5, 'title': 'Маркетинг і SEO-структура',
     'description': 'GA4, GTM, Meta Pixel, фід Google Shopping, сторінки під сезонні запити.'},
]

PACKAGES = [
    {'order': 0, 'name': 'Інтернет-магазин квітів під ключ',
     'scope': ('Дизайн, чистий код (Django/HTMX), адмін-панель CMS, каталог і фільтри, кошик, онлайн-оплата, '
               "доставка кур'єром і Новою Поштою, Telegram-сповіщення, аналітика, деплой і підключення домену. "
               'Наповнення каталогу та оплата домену й хостингу — на стороні клієнта.'),
     'duration': '30 днів', 'price': Decimal('1200.00'), 'currency': '€', 'is_recommended': False},
]

SPECS = [
    {'kind': ProposalSpec.Kind.SPEC, 'order': 0, 'title': 'Django / HTML5 / HTMX / JS',
     'body': 'Без важких конструкторів і платних плагінів: чистий код на надійному стеку.'},
    {'kind': ProposalSpec.Kind.SPEC, 'order': 1, 'title': 'Швидкість на смартфоні',
     'body': 'Легкі сторінки й оптимізовані фотогалереї: каталог швидко відкривається з телефона.'},
    {'kind': ProposalSpec.Kind.SPEC, 'order': 2, 'title': 'Святкові піки',
     'body': 'Без залежності від плагінів: стабільна робота 14 лютого, 8 березня й у сезон саджанців.'},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 0, 'title': 'Конструктор букета (HTMX)',
     'body': ('Вибір кількості (15 / 25 / 51 / 101 троянда), довжини стебла й пакування з миттєвим '
              'перерахунком ціни. Входить у 1 200 €.')},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 1, 'title': 'Дата вручення й листівка',
     'body': ("Календар дати й інтервалу доставки, текст листівки, опція «доставка-сюрприз». Зони й ціну "
              "кур'єрської доставки задаєте в адмінці; кур'єри — ваші або служба доставки.")},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 2, 'title': 'Сповіщення',
     'body': ('Нові замовлення — у Telegram флористам і диспетчерам; покупцю — лист про статус '
              'замовлення.')},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 3, 'title': 'Наповнення каталогу',
     'body': ('Ми робимо структуру категорій і фільтрів та показуємо, як додавати товари. Товари, фото, '
              'описи й ціни заводить клієнт через адмін-панель.')},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 4, 'title': 'Деплой та запуск',
     'body': ('Сервер, SSL, підключення домену. Домен і хостинг купує й оплачує клієнт; ми допомагаємо '
              'обрати й усе налаштовуємо.')},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 0, 'title': '1-й платіж (50%) — 600 €',
     'body': 'Передплата перед стартом проєктування та UI/UX.'},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 1, 'title': '2-й платіж (50%) — 600 €',
     'body': 'Після фінального тестування, перед деплоєм і передачею доступів.'},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 2,
     'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів по 240 €/міс.',
     'body': ('Рівні частини до 5 місяців без відсотків. Договір розстрочки клієнт оформлює з банком сам. '
              'Старт розробки одразу після погодження.')},
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда розробників і маркетологів. Це КП саме на <strong>інтернет-магазин</strong> квітів з адмін-панеллю CMS: каталог, кошик, онлайн-оплата, доставка.</p>
<ul>
<li><strong>Адмін-панель CMS</strong> — є лише в магазині: замовлення, ціни, наявність, акції без програмістів.</li>
<li><strong>Каталог</strong> — троянди, лаванда, сезонні квіти, букети, саджанці; фільтри за кольором, висотою, приводом.</li>
<li><strong>Замовлення</strong> — конструктор букета, дата й час доставки, листівка, онлайн-оплата, Telegram-сповіщення.</li>
<li><strong>Ціна окремо</strong> — інтернет-магазин 1 200 €, 30 днів (лендинг — окреме КП і окрема ціна).</li>
<li><strong>Що робить клієнт</strong> — наповнює каталог, оплачує домен і хостинг, укладає з банком договори еквайрингу й розстрочки.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. office@prometeylabs.com</p>
""".strip()


class Command(BaseCommand):
    help = 'Seed flowers E-SHOP proposal (1 200 €, з адмінкою CMS) + standard demo-shop (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('--no-demo', action='store_true', help='Тільки КП, без демо')

    def handle(self, *args, **options):
        proposal, created = seed_rows(sys.modules[__name__])
        if not options['no_demo']:
            self._provision_demo(proposal)
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Updated'}: /proposal/{SLUG}/"))

    def _provision_demo(self, proposal):
        """Стандартний демо-магазин (канон), без змін під клієнта."""
        from apps.demoshop.models import DemoShop
        from apps.demoshop.services.provision import provision_demo_shop

        if not DemoShop.objects.filter(proposal=proposal).exists():
            DemoShop(proposal=proposal, name='Demo Shop', slug=DEMO_TENANT_SLUG).save()
        shop = provision_demo_shop(proposal)
        if shop.name != 'Demo Shop':
            shop.name = 'Demo Shop'
            shop.save(update_fields=['name'])
        self.stdout.write(self.style.SUCCESS(f'Demo: {shop.get_absolute_url()} (slug={shop.slug})'))
