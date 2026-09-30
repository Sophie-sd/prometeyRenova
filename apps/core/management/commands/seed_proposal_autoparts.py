"""
Management command: seed_proposal_autoparts

Idempotent заливка КП «Автозапчастини» (PDF 30.09.2026)
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

SLUG = 'shop-autoparts-a7f3'

RECS_LEAD = (
    'Магазин автозапчастин на Django / HTMX: '
    'підбір за маркою і моделлю, кошик в один екран, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Марка · модель'},
    {'order': 3, 'title': '31 день'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Марка · модель', 'is_accent': False},
    {'order': 1, 'title': 'Card', 'caption': 'Сумісність', 'is_accent': True},
    {'order': 2, 'title': 'Cart', 'caption': '1 екран', 'is_accent': False},
    {'order': 3, 'title': 'Ship', 'caption': 'НП · кур’єр', 'is_accent': False},
    {'order': 4, 'title': 'Feed', 'caption': 'Merchant', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX для підбирача',
        'description': (
            'Інтерфейс під смартфон і робочий монітор. '
            'Підбирач бачить список і картку без зайвих кроків.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог за сумісністю',
        'description': (
            'Фільтр і пошук за маркою, моделлю і параметрами. '
            'Картка з характеристиками і наявністю.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Кошик і доставка',
        'description': (
            'Оформлення в один екран. Нова Пошта, Укрпошта і кур’єр: '
            'відділення і вартість рахуються в замовленні.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Оплата карткою',
        'description': (
            'LiqPay, WayForPay або Monobank. Apple Pay і Google Pay на сайті.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Адмінка залишків і цін',
        'description': (
            'Залишки, пакетне редагування цін і статуси замовлень без програміста.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Аналітика і запуск',
        'description': (
            'GA4, Meta Pixel, Google Merchant фід і SEO-база. '
            'Сервер, SSL і домен.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Базовий',
        'scope': (
            'Від 900 €: точна сума після переліку інтеграцій. '
            'UI/UX, Django і HTMX, адмінка товарів, оплата, пошта, '
            'базова SEO, деплой.'
        ),
        'duration': '31 день',
        'price': Decimal('900.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Турбо-Старт',
        'scope': (
            'Усе з Базового плюс Google Ads: пошук і Shopping, '
            'таргетована реклама під запуск магазину.'
        ),
        'duration': '31 день',
        'price': Decimal('1200.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Швидкість каталогу',
        'body': (
            'Сторінка відкривається до 1,5 с. Кеш запитів і чистий бекенд '
            'тримають прайс під рекламним напливом.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Безпека і HTTPS',
        'body': (
            'CSRF, XSS і SQL-ін’єкції закриті на рівні ядра. '
            'SSL, ізольована адмінка, безпечна авторизація.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Деплой',
        'body': (
            'Nginx, Gunicorn або Daphne, PostgreSQL. '
            'Пошта, домен і тест перед стартом.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без конструктора на автопрайсі',
        'body': (
            'Важкі теми і платні модулі гальмують список запчастин. '
            'Свій код тримає фільтр і кошик без абонплати.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+',
        'body': (
            'Підбирач не чекає картку. '
            '90+ на телефоні й ПК — умова здачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед стартом і прототипом.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після тесту на стенді, перед релізом і передачею доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка Базового: 6 × від 150 €',
        'body': 'Шість рівних частин без відсотків замість схеми 50/50.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 3,
        'title': 'Розстрочка «Турбо-Старт»: 6 × 200 €',
        'body': 'Шість рівних частин без відсотків замість схеми 50/50.',
    },
]

TITLE = 'Інтернет-магазин автозапчастин під ключ'
LEAD = (
    'Каталог із підбором за маркою і моделлю, кошик в один екран '
    'і оплата карткою — без комісії конструктора.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає магазин для автоіндустрії: високий чек, швидкий підбір і стабільний прайс під рекламу.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript · PostgreSQL</strong>. Без шаблонних CMS і без платних плагінів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — список запчастин відкривається одразу.</li>
<li><strong>Сумісність</strong> — марка і модель фільтруються на сервері, не в описі.</li>
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
    help = 'Seed autoparts shop proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('autoparts'),
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
                'client_name': 'Автозапчастини',
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
                'issued_on': date(2026, 9, 30),
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
                'order': 18,
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
