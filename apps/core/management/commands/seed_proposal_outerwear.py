"""
Management command: seed_proposal_outerwear

Idempotent заливка КП «Верхній одяг» (PDF 28.09.2026)
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

SLUG = 'shop-outerwear-a7f3'

RECS_LEAD = (
    'Магазин верхнього одягу на Django / HTMX: '
    'розмір і колір на картці, менше повернень, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Розмірна сітка'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Card', 'caption': 'Колір · шви', 'is_accent': True},
    {'order': 1, 'title': 'Size', 'caption': 'Зріст · обхват', 'is_accent': False},
    {'order': 2, 'title': 'Filter', 'caption': 'Сезон · пух', 'is_accent': False},
    {'order': 3, 'title': 'Ship', 'caption': 'НП · Укрпошта', 'is_accent': False},
    {'order': 4, 'title': 'Ads', 'caption': 'Pixel · фід', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX під одяг',
        'description': (
            'Верстка, щоб було видно тканину і фурнітуру. '
            'Телефон і ПК без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Картка і колір',
        'description': (
            'Галерея: загальний вигляд, капюшон, шви, підкладка, водовідштовхування. '
            'Колір міняє фото на картці. Поруч склад і температурний режим.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розмірна сітка',
        'description': (
            'Зріст, обхват грудей, талії і стегон. '
            'Інструкція заміру під куртку, пальто або парку — щоб річ не повернулась.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Фільтр каталогу',
        'description': (
            'Сезон, утеплювач, довжина, капюшон і матеріал верху. '
            'Список оновлюється без перезавантаження.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Доставка, оплата, залишки',
        'description': (
            'Нова Пошта і Укрпошта. Картка через LiqPay, WayForPay, Monobank або NovaPay. '
            'Залишок ведеться за розміром і кольором.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Рекламний кабінет',
        'description': (
            'Meta Pixel, Conversions API, події кошика і покупки, '
            'динамічний каталог для ретаргетингу і перші аудиторії.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин верхнього одягу під ключ',
        'scope': (
            'UI/UX, Django і HTMX, розмір і колір, оплата, пошта, адмінка, '
            'деплой, домен і налаштування Meta Ads: Pixel, Conversions API, фід товарів.'
        ),
        'duration': '30 днів',
        'price': Decimal('1200.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Картка куртки',
        'body': (
            'Кілька кадрів тканини і фурнітури. '
            'Селектор кольору підміняє фото, а не лишає один ракурс на всі кольори.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Розмір до покупки',
        'body': (
            'Таблиця зріст / груди / талія / стегна і як знімати заміри. '
            'Мета — менше повернень через розмір.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Реклама в пакеті',
        'body': (
            'Pixel, Conversions API, верифікація домену і XML-каталог. '
            'Події Add to Cart і Purchase йдуть у кабінет Meta.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без конструктора на розпродажі',
        'body': (
            'Сезонний стрибок не має класти галерею. '
            'Свій код тримає картку, коли йде трафік з реклами.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+ з телефону',
        'body': (
            'Куртку обирають з телефону. '
            '90+ на мобільному — умова здачі, інакше клік з реклами зникає.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50% — 600 €',
        'body': 'Передоплата перед стартом робіт.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50% — 600 €',
        'body': 'Після тесту, перед передачею доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка: 3 × 400 €',
        'body': 'Без відсотків, три частини за 30 днів проєкту.',
    },
]

TITLE = 'Інтернет-магазин верхнього одягу під ключ'
LEAD = (
    'Картка, де видно тканину і розмір до покупки, '
    'плюс рекламний кабінет Meta на запуск.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає магазин верхнього одягу під високий чек і сезонний пік: менше повернень через розмір, стабільна галерея на розпродажі.</p>
<p>Стек: <strong>Django (Python) · HTMX · JavaScript · HTML5 · CSS3</strong>. Без конструктора і без підписок на плагіни.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — картка відкривається з телефону, клік з реклами не губиться.</li>
<li><strong>Розмір</strong> — таблиця замірів стоїть на картці, не в окремому PDF.</li>
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
    help = 'Seed outerwear shop proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('outerwear'),
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
                'client_name': 'Верхній одяг',
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
                'order': 16,
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
