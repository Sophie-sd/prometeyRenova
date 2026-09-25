"""
Management command: seed_proposal_4isp

Idempotent заливка КП «4-ISP» (PDF 25.09.2026)
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

SLUG = 'shop-4isp-a7f3'

RECS_LEAD = (
    'Портал заводу і магазин ЗІП на одному домені: '
    'Django / HTMX, калькулятор різки, кошик і PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'UA / EN'},
    {'order': 3, 'title': 'До 30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Plant', 'caption': 'Різка · цех', 'is_accent': False},
    {'order': 1, 'title': 'Calc', 'caption': 'DXF · DWG', 'is_accent': True},
    {'order': 2, 'title': 'Machines', 'caption': 'кВт · стіл', 'is_accent': False},
    {'order': 3, 'title': 'Parts', 'caption': 'Сопла · лінзи', 'is_accent': False},
    {'order': 4, 'title': 'Cart', 'caption': 'Картка · НП', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Єдиний інтерфейс',
        'description': (
            'Імідж заводу і кошик в одному стилі. '
            'Телефон, планшет і ПК без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Корпоративні сторінки',
        'description': (
            'Цехи, обладнання, лазерна різка, гнуття, зварювання, фарбування, '
            'сервіс, команда і новини.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Калькулятор різки',
        'description': (
            'Онлайн-розрахунок із файлом DXF або DWG. '
            'Заявка йде в продаж, сторінка не перезавантажується.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Каталог верстатів',
        'description': (
            'Оптоволоконні комплекси. Фільтр за потужністю 1–12 кВт і розміром столу. '
            'Відео, специфікація, запит лізингу і виклик інженера.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Магазин ЗІП',
        'description': (
            'До 50 категорій: сопла, лінзи, запчастини. '
            'Фільтр сумісності з брендом верстата, наявність і ціна у валюті.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Кошик, оплата, адмінка',
        'description': (
            'Швидке замовлення, картка, рахунок, Нова Пошта або кур’єр. '
            'Статті, верстати, ціни і залишки в одній панелі. Мови UA та EN.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Базовий',
        'scope': (
            'Корпоративний сайт і магазин: єдиний UI, Django і HTMX, блоки про цех і сервіс, '
            'калькулятор DXF/DWG, каталог верстатів, магазин ЗІП, кошик, оплата, '
            'Нова Пошта, UA/EN, синхронізація з BAS і боти заявок, деплой.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('1900.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Преміум',
        'scope': (
            'Усе з Базового плюс Google Ads на різку, Performance Max і Shopping для ЗІП, '
            'GA4 з e-commerce подіями, 3 місяці SEO і пріоритетна підтримка.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('2700.00'),
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'Платінум',
        'scope': (
            'Усе з Преміум плюс AI-помічник підбору верстатів і оптики, '
            'попередній розрахунок креслень, чат на сайті, 6 місяців SEO, '
            'наскрізна аналітика і куратор.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('4200.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Завод і послуги',
        'body': (
            'Про компанію, цехи, лазерна різка, гнуття, зварювання, фарбування. '
            'Сервіс, гарантії і блог — на тому ж домені, що й магазин.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Верстати і ЗІП',
        'body': (
            'Картка комплексу: відео, специфікація, лізинг, виклик інженера. '
            'Поруч магазин сопел і лінз із фільтром під бренд верстата.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Облік і сповіщення',
        'body': (
            'Залишки і статуси замовлень синхронізуються з BAS. '
            'Заявка йде в Telegram або Viber і на пошту продажу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Один код на два розділи',
        'body': (
            'Корпоративні сторінки і кошик на спільній базі. '
            'Немає двох сайтів, які роз’їжджаються після оновлення плагіна.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+ на B2B-трафіку',
        'body': (
            'Каталог верстатів і прайс ЗІП мають відкриватися разом із рекламою. '
            '90+ на телефоні й ПК — умова здачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Фіксує структуру, єдиний інтерфейс і старт розробки.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': (
            'Після показу корпоративних і торгових модулів, '
            'перед публікацією на домен.'
        ),
    },
]

TITLE = 'Портал «4-ISP»: завод і магазин комплектуючих'
LEAD = (
    'Один домен: імідж виробництва, розрахунок лазерної різки, '
    'каталог верстатів і замовлення ЗІП.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає портал виробника: бренд заводу і пряме замовлення комплектуючих без другого сайту.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Одна адмінка на корпоративні сторінки і магазин. Без конфлікту плагінів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — картка верстата і прайс ЗІП відкриваються під B2B-трафік.</li>
<li><strong>UA / EN</strong> — ті самі розділи для внутрішнього і зарубіжного партнера.</li>
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
    help = 'Seed 4-ISP portal proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('4isp'),
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
                'client_name': '4-ISP',
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
                'issued_on': date(2026, 9, 25),
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
                'order': 11,
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
