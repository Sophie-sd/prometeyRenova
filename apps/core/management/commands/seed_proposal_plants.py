"""
Management command: seed_proposal_plants

Idempotent заливка КП «Рослини та добрива» (PDF 28.09.2026)
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

SLUG = 'shop-plants-a7f3'

RECS_LEAD = (
    'Магазин рослин, саджанців і добрив на Django / HTMX: '
    'літраж міняє ціну, догляд у фільтрі, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Нова Пошта'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Світло · тінь', 'is_accent': False},
    {'order': 1, 'title': 'Card', 'caption': '1 л · висота', 'is_accent': True},
    {'order': 2, 'title': 'Care', 'caption': 'Календар', 'is_accent': False},
    {'order': 3, 'title': 'Cart', 'caption': 'Ґрунт поруч', 'is_accent': False},
    {'order': 4, 'title': 'Ship', 'caption': 'Живі рослини', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX каталогу рослин',
        'description': (
            'Ергономічний інтерфейс під саджанці і добрива. '
            'Телефон, планшет і ПК без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог і картка',
        'description': (
            'Фільтр за типом, призначенням і фасуванням. '
            'Рослини: світлолюбні, тіньовитривалі, вуличні, кімнатні. '
            'Добрива: мінеральні, органічні, стимулятори.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Фасування на картці',
        'description': (
            'Добриво 1 / 5 / 20 л і висота саджанця міняють ціну. '
            'Інструкція і галерея лишаються на тій самій картці.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Кошик, пошта, оплата',
        'description': (
            'Нова Пошта і Укрпошта: відділення або адреса. '
            'Картка через Monobank, LiqPay або WayForPay. '
            'Поруч — ґрунт і добриво до цієї рослини.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Догляд і відправка живого',
        'description': (
            'Блог або агрокалендар для пошукового трафіку. '
            'Підказка про пакування і температуру для живих рослин, '
            'плюс контроль мінімального замовлення.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Адмінка і запуск',
        'description': (
            'Залишки, ціни і замовлення без програміста. '
            'GA4, Meta Pixel, Schema.org, сервер, SSL і домен.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин під ключ',
        'scope': (
            'Рослини та добрива. UI/UX, Django і HTMX, адмінка під фасування, '
            'оплата, пошта, базова SEO, деплой.'
        ),
        'duration': '30 днів',
        'price': Decimal('900.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Фасування і висота',
        'body': (
            '1 л, 5 л і 20 л добрива або вік і висота саджанця — '
            'варіанти однієї картки, ціна рахується на сервері.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Фільтр догляду',
        'body': (
            'Світло, тінь, вулиця, кімната. '
            'Добрива — за типом дії, не за довгим описом.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Жива відправка',
        'body': (
            'Підказка про пакування і температурний режим. '
            'Мінімальне замовлення видно до оплати.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без OpenCart і WooCommerce',
        'body': (
            'Платні модулі фасування конфліктують на сезонному піку. '
            'Прайс і залишок у своєму коді.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+ навесні',
        'body': (
            'Весняний трафік не має класти картку саджанця. '
            '90+ на телефоні — умова здачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50% — 450 €',
        'body': 'Перед стартом проєктування і дизайну.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50% — 450 €',
        'body': 'Після тесту, перед передачею доступів і домену.',
    },
]

TITLE = 'Інтернет-магазин рослин, саджанців і добрив'
LEAD = (
    'Каталог, де літраж добрива і висота саджанця міняють ціну, '
    'а ґрунт пропонується до рослини в кошику.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає магазин агробізнесу: повторне замовлення, сезонний пік і середній чек без конструктора.</p>
<p>Стек: <strong>Django (Python) · HTMX · JavaScript · HTML5 · CSS3</strong>. Без OpenCart і WooCommerce.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — картка відкривається з телефону в сезон.</li>
<li><strong>Фасування</strong> — 1 л і 20 л не два товари з однією ціною.</li>
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
    help = 'Seed plants shop proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('plants'),
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
                'client_name': 'Рослини та добрива',
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
                'order': 15,
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
