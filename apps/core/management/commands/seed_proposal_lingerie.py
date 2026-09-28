"""
Management command: seed_proposal_lingerie

Idempotent заливка КП «Білизна та парфумерія» (PDF 28.09.2026)
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

SLUG = 'shop-lingerie-a7f3'

RECS_LEAD = (
    'Магазин білизни і парфумерії на Django / HTMX: '
    'розмір і об’єм міняють ціну, крос-сейл піднімає чек, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Нова Пошта'},
    {'order': 3, 'title': '30–35 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Розмір · ноти', 'is_accent': False},
    {'order': 1, 'title': 'Card', 'caption': 'Колір · об’єм', 'is_accent': True},
    {'order': 2, 'title': 'Wish', 'caption': 'Список бажаного', 'is_accent': False},
    {'order': 3, 'title': 'Cart', 'caption': 'Пакування', 'is_accent': False},
    {'order': 4, 'title': 'Pay', 'caption': 'Картка · НП', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX під телефон і ПК',
        'description': (
            'Інтерфейс під преміальний вигляд білизни і парфумерії. '
            'Телефон, планшет і десктоп без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог і картка',
        'description': (
            'Фільтр за брендом, типом білизни, сімейством аромату, ціною і наявністю. '
            'Живий пошук і галерея, яка не ронить швидкість.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розмір, колір, об’єм',
        'description': (
            'Білизна: таблиця розмірів, колір і розмір на одній картці, коротке відео комплекту. '
            'Парфуми: верхні ноти, серце і база; 30 / 50 / 100 мл міняють ціну.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Кошик, доставка, оплата',
        'description': (
            'Нова Пошта і Укрпошта: відділення або поштомат, розрахунок доставки. '
            'Картка через Mono, LiqPay або WayForPay.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Крос-сейл і список бажаного',
        'description': (
            '«З цим купують», схожі аромати, подарункове пакування. '
            'Обране зберігає комплект або парфум на потім.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Адмінка, аналітика, запуск',
        'description': (
            'Асортимент, ціни і залишки без програміста. '
            'Пікселі Facebook і Google, мікророзмітка, сервер і домен.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин під ключ',
        'scope': (
            'Коридор 900–1 100 €: точна сума після переліку інтеграцій. '
            'Дизайн, Django, адмінка, оплата, пошта, крос-сейл, '
            'фільтри білизни і парфумерії, деплой і домен.'
        ),
        'duration': '30–35 днів',
        'price': Decimal('900.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Картка білизни',
        'body': (
            'Таблиця розмірів, колір і розмір в одній картці. '
            'Коротке відео комплекту не підміняє галерею фото.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Картка парфуму',
        'body': (
            'Верхні ноти, ноти серця, базові ноти. '
            'Об’єм 30, 50 і 100 мл перемикає ціну на сервері.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Середній чек',
        'body': (
            'Панчохи до комплекту, схожий аромат, подарункове пакування. '
            'Список бажаного лишає товар до наступного візиту.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без WordPress і OpenCart',
        'body': (
            'Платні галереї і фільтри гальмують каталог моди. '
            'Прайс і залишок у своєму коді, без абонплати за плагіни.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+ на розпродажі',
        'body': (
            'Святковий трафік не має класти картку. '
            '90+ на телефоні й ПК — умова здачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Перед стартом: закріплює команду і запускає розробку.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після тесту на стенді, перед деплоєм і передачею доступів.',
    },
]

TITLE = 'Інтернет-магазин білизни та парфумерії під ключ'
LEAD = (
    'Каталог, де розмір, колір і об’єм флакона міняють ціну, '
    'а супутнє піднімає середній чек.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає магазин для ніші краси: вигляд картки, швидкий вибір і стабільність на розпродажі.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без WordPress і OpenCart.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — галерея не з’їдає конверсію і позиції в пошуку.</li>
<li><strong>Святковий трафік</strong> — кошик лишається на місці, коли йде кампанія.</li>
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
    help = 'Seed lingerie shop proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('lingerie'),
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
                'client_name': 'Білизна та парфумерія',
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
                'issued_on': date(2026, 9, 28),
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
                'order': 13,
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
