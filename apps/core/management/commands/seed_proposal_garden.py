"""
Management command: seed_proposal_garden

Idempotent заливка КП «Все для саду та городу» (PDF 23.09.2026)
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

SLUG = 'shop-sad-gorod-a7f3'

RECS_LEAD = (
    'Інженерні рішення для інтернет-магазину насіння, добрив і садового інвентарю — '
    'Django / HTMX / CSS / JS, без конструкторів і без платних плагінів.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Нова Пошта'},
    {'order': 3, 'title': 'До 30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Admin', 'caption': 'Ціни · залишки', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Фасування · культура', 'is_accent': False},
    {'order': 2, 'title': 'Cart', 'caption': '1 екран · 1 клік', 'is_accent': True},
    {'order': 3, 'title': 'Delivery', 'caption': 'НП · Укрпошта', 'is_accent': False},
    {'order': 4, 'title': 'Pay', 'caption': 'LiqPay · Mono', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX під смартфон і ПК',
        'description': (
            'Чистий адаптивний інтерфейс: телефон, планшет і десктоп. '
            'Без окремої «мобільної шкіри» конструктора.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог і картка товару',
        'description': (
            'Фільтри за фасуванням, виробником і культурою, живий пошук, галереї. '
            'Варіації: вага насіння 0,5 / 10 / 100 г, літраж 100 мл / 1 л, '
            'колір і щільність покривних матеріалів — ціна змінюється разом із варіантом. '
            'Бейджі «Хіт сезону», «Знижка», «Новинка» і статуси наявності.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Кошик в один екран і доставка',
        'description': (
            'Оформлення на одному екрані. Місто й відділення або поштомат '
            'через API Нової Пошти, плюс Укрпошта. Вартість доставки рахується в замовленні. '
            '«Купити в 1 клік» — лише номер телефону.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Оплата карткою',
        'description': (
            'LiqPay, Monobank, WayForPay або NovaPay: миттєва оплата карткою на сайті.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Адмінка номенклатури',
        'description': (
            'Ціни, залишки і замовлення без спеціаліста на кожну правку прайсу.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Аналітика і базове SEO',
        'description': (
            'Google Analytics 4, Meta Pixel, Schema.org і базове SEO в пакеті запуску.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин під ключ',
        'scope': (
            'Ніша: сад, город, дім. Коридор вартості 900–950 €. '
            'Адаптивний дизайн, Django і HTMX, адмін-панель, фільтри і пошук, '
            'оплата і доставка, аналітика, базове SEO, деплой і домен.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('900.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Каталог ніші сад і город',
        'body': (
            'Насіння і садивний матеріал, добрива та ЗЗР, крапельний полив, '
            'інвентар, парники, агроволокно. Варіації фасування і літражу '
            'міняють ціну на картці.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Доставка і сповіщення',
        'body': (
            'Місто, відділення або поштомат Нової Пошти через API, розрахунок вартості. '
            'Укрпошта. SMS, Viber або Telegram клієнту: замовлення прийнято і номер ТТН.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Купити в 1 клік',
        'body': 'Лише номер телефону. Менеджер передзвонює, без довгої форми.',
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без WordPress і OpenCart',
        'body': (
            'Платні модулі кошика й доставки гальмують сайт і ламаються на оновленнях. '
            'Підписок на ліцензії плагінів немає: прайс і залишок у своєму коді.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Варіант товару міняє ціну',
        'body': (
            '0,5 г і 100 г насіння — не два описи в одній картці з однією ціною. '
            'Фасування, літраж і щільність агроволокна перемикають ціну на сервері.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'PageSpeed 90+ у сезон',
        'body': (
            'Акція на добрива не має класти сайт. 90+ на телефоні й ПК — '
            'умова здачі, інакше реклама платить за очікування.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': (
            'Після затвердження структури і підписання домовленостей, '
            'на старт проєктування і прототипу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': (
            'Після розробки і тесту на стенді, перед релізом на бойовий домен '
            'і передачею доступів.'
        ),
    },
]

TITLE = 'Інтернет-магазин «Все для саду та городу» під ключ'
LEAD = (
    'Швидкий e-commerce для роздробу і дрібного опту: насіння, добрива, '
    'полив, інвентар і товари для дачі.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> будує інструмент продажів: середній чек, швидка обробка замовлення і масштаб без конструктора.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript · PostgreSQL</strong>. Без WordPress і OpenCart — їхні платні модулі гальмують каталог і ламаються на оновленнях. Ліцензій на плагіни немає.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — на смартфоні й на ПК. Швидша сторінка піднімає конверсію і дає перевагу в Google.</li>
<li><strong>Сезонні акції</strong> — сайт лишається швидким, коли на добрива і насіння приходить наплив.</li>
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
    help = 'Seed garden e-commerce proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('sad-gorod'),
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
                'client_name': 'Все для саду та городу',
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
                'order': 4,
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
