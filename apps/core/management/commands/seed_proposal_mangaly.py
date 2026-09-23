"""
Management command: seed_proposal_mangaly

Idempotent заливка КП «E-Commerce Мангали & Метал» (PDF 23.09.2026)
+ класичний demo-shop. Це не версія сайту клієнта.
"""
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.i18n_content import translate_ua_to_ru
from apps.core.legacy_schema import (
    create_with_leftovers,
    ensure_leftover_not_null_defaults,
)
from apps.core.proposal_models import (
    Proposal,
    ProposalModule,
    ProposalPackage,
    ProposalSpec,
)
from apps.core.proposal_visual_models import ProposalArchNode, ProposalHighlight

SLUG = 'shop-mangaly-a7f3'

RECS_LEAD = (
    'Інженерні рішення для інтернет-магазину металовиробів під ключ — '
    'Django / HTMX / CSS / JS, без конструкторів і без платних плагінів.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Нова Пошта'},
    {'order': 3, 'title': 'До 30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Admin', 'caption': 'Залишки · замовлення', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Товщина · розмір', 'is_accent': False},
    {'order': 2, 'title': 'Cart', 'caption': '1 клік · кошик', 'is_accent': True},
    {'order': 3, 'title': 'Delivery', 'caption': 'Вага · Нова Пошта', 'is_accent': False},
    {'order': 4, 'title': 'Pay', 'caption': 'Картка · післяплата', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX у стилі металообробки',
        'description': (
            'Лаконічний інтерфейс під крафт і метал, mobile-first: '
            'смартфон і ПК без окремої «мобільної версії з конструктора».'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог і картка товару',
        'description': (
            'Фільтри за товщиною металу (2 / 3 / 4 мм), кількістю шампурів, '
            'розміром і опцією гравіювання. Галерея, міцність, габарити '
            'у зібраному й розібраному вигляді, залишок на складі.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Кошик і логістика',
        'description': (
            'Швидке замовлення в один клік або звичайний кошик. '
            'Габарити й вага металовиробу рахуються для Нової Пошти '
            'та інших перевізників. Мінімум полів на оформленні.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Оплата на сайті і післяплата',
        'description': (
            'WayForPay, LiqPay або Mono: картка, Apple Pay, Google Pay. '
            'Окремо — накладений платіж при отриманні на пошті.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Адмінка асортименту і замовлень',
        'description': (
            'Ціни, залишки сталі, статуси замовлень — без програміста '
            'на кожну правку прайсу.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Аналітика, пікселі і товарний фід',
        'description': (
            'Google Analytics, пікселі Meta і TikTok, Schema.org, '
            'XML-фід для Merchant Center і сезонних кампаній.'
        ),
    },
    {
        'number': 7,
        'order': 6,
        'title': 'Деплой, домен і SSL',
        'description': (
            'Хмарний сервер, сертифікат, пошта сповіщень і робочий домен '
            'входять у запуск під ключ.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Базовий',
        'scope': (
            'Інтернет-магазин під ключ: дизайн, Django / HTMX, каталог готових виробів, '
            'кошик і оформлення, онлайн-оплата, доставка, адмінка асортименту '
            'й замовлень, деплой на сервер.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('1150.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Преміум',
        'scope': (
            'Усе з Базового плюс запуск реклами: Google Ads, Google Shopping, Meta Ads, '
            'SEO-структура і товарні фіди під сезонний попит.'
        ),
        'duration': 'до 35 днів',
        'price': Decimal('2000.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 2,
        'name': 'Платінум',
        'scope': (
            'Усе з Преміум плюс AI-консультант на сайті 24/7, генерація описів товарів '
            'і Telegram-бот, який одразу сповіщає менеджера про нове замовлення.'
        ),
        'duration': 'до 45 днів',
        'price': Decimal('3500.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Прямий продаж без конфігуратора',
        'body': (
            'Фокус на швидкому виборі готових розбірних мангалів і металовиробів. '
            'Без покрокового конструктора і зайвих кроків до кошика.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Оформлення в один клік або через кошик',
        'body': (
            'Мінімум полів. Можна замовити в один клік або зібрати кошик '
            'і обрати відділення перевізника.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Подача металу, не «картка з описом»',
        'body': (
            'Галерея, акцент на товщині й міцності, габарити у зібраному '
            'і розібраному вигляді, наявність на складі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 3,
        'title': 'Оплата карткою або післяплата',
        'body': (
            'Моментальна оплата на сайті або накладений платіж на пошті. '
            'Платіжний провайдер підключається в пакеті запуску.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Не OpenCart і не WordPress',
        'body': (
            'Платні плагіни кошика й доставки ламаються на оновленнях ядра. '
            'Django тримає ціну, вагу і залишок на сервері.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Вага для Нової Пошти рахується сама',
        'body': (
            'Металовиріб не відправляють «як посилку до 2 кг». '
            'Габарити й вага йдуть у розрахунок доставки, інакше клієнт бачить '
            'чужу ціну на відділенні.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'PageSpeed 90+ до сезону',
        'body': (
            'Повільна картка піднімає ціну кліка в Google Ads. '
            '90+ — умова здачі, не оптимізація «після запуску реклами».'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Фід для Shopping, не ручні оголошення',
        'body': (
            'Сезонний попит на мангали не збирають по одному товару в кабінеті. '
            'XML-фід годує Merchant Center і автоматичні кампанії.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й етап: 50%',
        'body': 'Передоплата на старт розробки і проєктування.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й етап: 50%',
        'body': 'Після тестування й узгодження, перед релізом.',
    },
]

TITLE = 'Розробка інтернет-магазину під ключ'
LEAD = (
    'Високонавантажений інтернет-магазин для виробництва розбірних мангалів '
    'і металевих виробів: каталог, кошик, оплата і доставка.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> будує інструмент прямих продажів: високий середній чек, окупність реклами і масштаб виробництва без конструктора.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без WordPress і OpenCart — їхні платні плагіни кошика й доставки ламаються на оновленнях.</p>
<ul>
<li><strong>Django і HTMX</strong> — бекенд на Python, інтерфейс без важкого бандла. Ціна, вага і залишок живуть на сервері.</li>
<li><strong>PageSpeed 90+</strong> — швидша картка знижує ціну кліка в Google Ads і тримає сайт у сезон пікніків.</li>
</ul>
""".strip()

GUARANTEE_HTML = """
<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів, він не потребує постійних ризикованих оновлень, які ламають верстку.</p>
<p>Ми надаємо <strong>пожиттєву гарантію</strong> на працездатність нашого коду протягом усього періоду життя ресурсу.</p>
""".strip()


def _with_ru(payload: dict, text_keys: tuple[str, ...]) -> dict:
    out = dict(payload)
    for key in text_keys:
        ru_key = f'{key}_ru'
        if ru_key not in out:
            out[ru_key] = translate_ua_to_ru(out.get(key, ''))
        for lang in ('en', 'cs'):
            out.setdefault(f'{key}_{lang}', '')
    return out


def _attach_hero(proposal: Proposal) -> None:
    src = Path(settings.BASE_DIR) / 'static' / 'proposal' / 'img' / 'seal-on-dark.webp'
    if not src.is_file():
        return
    if proposal.hero_image:
        proposal.hero_image.delete(save=False)
    with src.open('rb') as handle:
        proposal.hero_image.save(src.name, File(handle), save=True)


class Command(BaseCommand):
    help = 'Seed mangal e-commerce proposal + classic demo-shop (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_shop',
        )

    def handle(self, *args, **options):
        for model in (
            Proposal,
            ProposalModule,
            ProposalPackage,
            ProposalSpec,
            ProposalHighlight,
            ProposalArchNode,
        ):
            ensure_leftover_not_null_defaults(model)
        with transaction.atomic():
            proposal, created = self._seed_rows()
        if not options['no_demo']:
            self._provision_demo(proposal)
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action}: /proposal/{SLUG}/ '
            f'({proposal.modules.count()} modules, '
            f'{proposal.packages.count()} packages)'
        ))

    def _provision_demo(self, proposal: Proposal) -> None:
        from apps.demoshop.models import DemoShop
        from apps.demoshop.services.provision import provision_demo_shop

        shop = DemoShop.objects.filter(proposal=proposal).first()
        if shop is None:
            shop = DemoShop(
                proposal=proposal,
                name='Demo Shop',
                slug=DemoShop.generate_slug('mangaly'),
            )
            shop.save()
        shop = provision_demo_shop(proposal)
        if shop.name != 'Demo Shop':
            shop.name = 'Demo Shop'
            shop.save(update_fields=['name'])
        self.stdout.write(self.style.SUCCESS(
            f'Demo: {shop.get_absolute_url()} (slug={shop.slug})'
        ))

    def _seed_rows(self):
        proposal, created = Proposal.objects.update_or_create(
            slug=SLUG,
            defaults={
                'client_name': 'E-Commerce Мангали & Метал',
                'title': TITLE,
                'title_ru': translate_ua_to_ru(TITLE),
                'title_en': '',
                'title_cs': '',
                'lead': LEAD,
                'lead_ru': translate_ua_to_ru(LEAD),
                'lead_en': '',
                'lead_cs': '',
                'recommendations_lead': RECS_LEAD,
                'recommendations_lead_ru': translate_ua_to_ru(RECS_LEAD),
                'recommendations_lead_en': '',
                'recommendations_lead_cs': '',
                'issued_on': date(2026, 9, 23),
                'intro_html': INTRO_HTML,
                'intro_html_ru': translate_ua_to_ru(INTRO_HTML),
                'intro_html_en': '',
                'intro_html_cs': '',
                'guarantee_html': GUARANTEE_HTML,
                'guarantee_html_ru': translate_ua_to_ru(GUARANTEE_HTML),
                'guarantee_html_en': '',
                'guarantee_html_cs': '',
                'cta_label': 'Обговорити проєкт',
                'cta_label_ru': 'Обсудить проект',
                'cta_label_en': '',
                'cta_label_cs': '',
                'kind': Proposal.DemoKind.SHOP,
                'corp_catalog': False,
                'is_published': True,
                'order': 3,
            },
        )
        proposal.modules.all().delete()
        for data in MODULES:
            create_with_leftovers(
                ProposalModule, proposal=proposal, **_with_ru(data, ('title', 'description')),
            )
        proposal.packages.all().delete()
        for data in PACKAGES:
            create_with_leftovers(
                ProposalPackage,
                proposal=proposal,
                **_with_ru(data, ('name', 'scope', 'duration')),
            )
        proposal.specs.all().delete()
        for data in SPECS:
            create_with_leftovers(
                ProposalSpec, proposal=proposal, **_with_ru(data, ('title', 'body')),
            )
        proposal.highlights.all().delete()
        for data in HIGHLIGHTS:
            create_with_leftovers(
                ProposalHighlight, proposal=proposal, **_with_ru(data, ('title',)),
            )
        proposal.arch_nodes.all().delete()
        for data in ARCH_NODES:
            create_with_leftovers(
                ProposalArchNode, proposal=proposal, **_with_ru(data, ('title', 'caption')),
            )
        _attach_hero(proposal)
        return proposal, created
