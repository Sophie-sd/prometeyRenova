"""
Management command: seed_proposal_tools

Idempotent заливка КП «Інструменти з Prom.ua» (PDF 29.09.2026)
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

SLUG = 'shop-tools-a7f3'

RECS_LEAD = (
    'Магазин інструментів після Prom.ua на Django / HTMX: '
    '301 зі старих адрес, фільтр за потужністю і диском, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Міграція з Prom.ua'},
    {'order': 3, 'title': '31 робочий день'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Import', 'caption': 'База Prom', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'кВт · диск', 'is_accent': True},
    {'order': 2, 'title': 'Cart', 'caption': '1 екран', 'is_accent': False},
    {'order': 3, 'title': 'Feed', 'caption': 'Shopping · Rozetka', 'is_accent': False},
    {'order': 4, 'title': 'Pay', 'caption': 'Картка · НП', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX під інструмент',
        'description': (
            'Адаптивний інтерфейс для вибору інструменту. '
            'Телефон і ПК без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Міграція з Prom.ua',
        'description': (
            'Товари, категорії, описи, параметри і фото з кабінету Prom. '
            '301 зі старих адрес, щоб не втратити пошуковий трафік.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Каталог і картка',
        'description': (
            'Фільтр за живленням, потужністю, брендом, діаметром диска, '
            'типом патрона і класом. Живий пошук, галерея, характеристики.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Кошик, пошта, оплата',
        'description': (
            'Оформлення в один екран. Нова Пошта і Укрпошта. '
            'Картка через LiqPay, Monobank або WayForPay.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Адмінка складу',
        'description': (
            'Товари, ціни, залишки і замовлення без програміста.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Аналітика і фіди',
        'description': (
            'GA4, Meta Pixel, Schema.org і Google Merchant XML. '
            'Щоденний YML для Shopping і Rozetka. Сервер, SSL і домен.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин під ключ',
        'scope': (
            'Міграція з Prom.ua. UI/UX, Django і HTMX, адмінка складу, '
            'оплата, Нова Пошта, GA4, Pixel, Merchant-фід, деплой, SSL і домен.'
        ),
        'duration': '31 робочий день',
        'price': Decimal('950.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Вивантаження з Prom.ua',
        'body': (
            'Асортимент, категорії, описи, технічні параметри і фото. '
            'Дані не губляться між кабінетом і новим каталогом.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': '301 зі старих адрес',
        'body': (
            'Таблиця перенаправлень з індексованих сторінок Prom '
            'на нові URL власного сайту.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Підбір інструменту',
        'body': (
            'Живлення, потужність, бренд, діаметр диска, патрон, клас. '
            'Покупець звужує прайс, а не гортає весь маркетплейс.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Свій домен замість комісії Prom',
        'body': (
            'Замовлення і база лишаються у вас. '
            'Щомісячної абонплати маркетплейсу немає.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+ на рекламі',
        'body': (
            'Кампанія Google Ads не має чекати картку. '
            '90+ на телефоні й ПК — умова здачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50% — 475 €',
        'body': 'Перед стартом: архітектура і первинна міграція бази.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50% — 475 €',
        'body': 'Після перевірки, перед релізом і передачею доступів.',
    },
]

TITLE = 'Інтернет-магазин інструментів під ключ'
LEAD = (
    'Повний перехід з Prom.ua: ручний і електроінструмент, '
    'розхідники й оснащення на власному домені.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає магазин інструментів без комісії маркетплейсу: чистий каталог, кошик і масштаб прайсу.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без конструктора і без абонплати Prom.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — картка і фільтр відкриваються без перезавантаження.</li>
<li><strong>301</strong> — старі адреси Prom ведуть на нові сторінки, пошуковий трафік не обнуляється.</li>
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
    help = 'Seed tools shop proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('tools'),
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
                'client_name': 'Інструменти з Prom.ua',
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
                'issued_on': date(2026, 9, 29),
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
                'order': 17,
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
