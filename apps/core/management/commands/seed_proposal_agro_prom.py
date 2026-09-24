"""
Management command: seed_proposal_agro_prom

Idempotent заливка КП «Перенесення агромагазину з Prom.ua» (PDF 24.09.2026)
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

SLUG = 'shop-agro-prom-a7f3'

RECS_LEAD = (
    'Власний магазин агротоварів замість вітрини Prom.ua: '
    'Django / HTMX, каталог без комісії маркетплейсу, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Міграція з Prom.ua'},
    {'order': 3, 'title': 'До 30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Admin', 'caption': 'Ціни · опт', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Культура · фасування', 'is_accent': False},
    {'order': 2, 'title': 'Cart', 'caption': 'Швидке замовлення', 'is_accent': True},
    {'order': 3, 'title': 'Delivery', 'caption': 'НП · Meest', 'is_accent': False},
    {'order': 4, 'title': 'Pay', 'caption': 'Картка · IBAN', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Міграція з Prom.ua',
        'description': (
            'Каталог насіння, добрив, ЗЗР, агрохімії і техніки: фото, описи, '
            'атрибути, залишки і категорії. 301-редиректи зберігають пошукові адреси.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'UI/UX під телефон і ПК',
        'description': (
            'Адаптивний інтерфейс з коротким шляхом до замовлення. '
            'Прайс відкривається і на слабкому мобільному інтернеті.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Каталог агротоварів',
        'description': (
            'Фільтри за діючою речовиною, культурою, нормою внесення, '
            'виробником і фасуванням. Картка з галереєю і наявністю.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Доставка за габаритом і вагою',
        'description': (
            'Нова Пошта, Делівері і Meest: вартість рахується в замовленні '
            'за габаритами та вагою.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Оплата карткою і рахунок для B2B',
        'description': (
            'LiqPay, WayForPay і MonoPay на сайті. Для гурту — рахунок IBAN.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Адмінка асортименту',
        'description': (
            'Ціни, оптові знижки, залишки і замовлення без програміста на кожну правку.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Базовий',
        'scope': (
            'Перенесення бази з Prom.ua, магазин на Django, адаптивний дизайн, '
            'каталог і картки, оплата і доставка, адмінка, базова SEO-підготовка.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('1000.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Преміум',
        'scope': (
            'Усе з Базового плюс преміум UI/UX, Google Shopping і пошук на 3 місяці, '
            'Google Analytics 4 і Meta Pixel, гуртові ціни та B2B-замовлення.'
        ),
        'duration': 'до 35–40 днів',
        'price': Decimal('1500.00'),
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'Платінум',
        'scope': (
            'Усе з Преміум плюс реклама на 6 місяців, AI-консультант з підбору '
            'добрив і ЗЗР, генерація описів, Telegram-бот замовлень і підтримка 24/7.'
        ),
        'duration': 'до 50 днів',
        'price': Decimal('3200.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Перенесення каталогу з Prom.ua',
        'body': (
            'Товари, фото, описи, атрибути, залишки і дерево категорій. '
            '301-редиректи, щоб не втратити адреси, які вже в пошуку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Фільтри під агрономію',
        'body': (
            'Діюча речовина, культура, норма внесення, виробник і фасування. '
            'Покупець звужує прайс, а не гортає весь маркетплейс.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Доставка і оплата',
        'body': (
            'Нова Пошта, Делівері, Meest — розрахунок за габаритом і вагою. '
            'Картка через LiqPay, WayForPay або MonoPay. Гурту — рахунок IBAN.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Свій домен замість комісії Prom.ua',
        'body': (
            'Клієнтська база і замовлення лишаються у вас. '
            'Щомісячного відсотка маркетплейсу і його обмежень немає.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+ у сезон',
        'body': (
            'Посівна і внесення ЗЗР не мають класти кошик. '
            '90+ на телефоні й ПК — умова здачі, інакше реклама платить за очікування.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Чистий код без плагінів',
        'body': (
            'Django, HTMX і PostgreSQL. Без конструктора і платних модулів, '
            'які ламають каталог на оновленні.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': (
            'Перед стартом: архітектура, прототип, середовище '
            'і розбір даних з Prom.ua.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': (
            'Після тесту модулів і перевірки клієнтом, '
            'перед деплоєм на бойовий домен.'
        ),
    },
]

TITLE = 'Інтернет-магазин агротоварів під ключ'
LEAD = (
    'Повне перенесення каталогу, категорій і клієнтів з Prom.ua '
    'на власний швидкий магазин — без комісії маркетплейсу.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає магазин прямих продажів: свій домен, своя база клієнтів, середній чек без відсотка Prom.ua.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript · PostgreSQL</strong>. Без шаблонів маркетплейсу і без платних підписок на плагіни.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — прайс відкривається на слабкому мобільному інтернеті в полі.</li>
<li><strong>Сезон</strong> — посівна, збір і внесення ЗЗР не кладуть кошик.</li>
<li><strong>Пошук</strong> — чиста структура швидше виводить агротовари в Google, ніж вітрина на Prom.ua.</li>
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
    help = 'Seed agro Prom.ua migration proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('agro-prom'),
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
                'client_name': 'Агромагазин з Prom.ua',
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
                'issued_on': date(2026, 9, 24),
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
                'order': 7,
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
