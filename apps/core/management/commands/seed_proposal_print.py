"""
Management command: seed_proposal_print

КП «Поліграфія» (PDF 30.09.2026): корпоративний каталог у тексті,
демо — стандартний інтернет-магазин.
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

SLUG = 'corporate-print-a7f3'

RECS_LEAD = (
    'Корпоративний каталог поліграфії: Django / HTMX, '
    'фільтр без перезавантаження, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Каталог'},
    {'order': 3, 'title': '3 тижні'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Brand', 'caption': 'Поліграфія', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Фільтри', 'is_accent': True},
    {'order': 2, 'title': 'Card', 'caption': 'PDF · ціна', 'is_accent': False},
    {'order': 3, 'title': 'Lead', 'caption': 'Заявка', 'is_accent': False},
    {'order': 4, 'title': 'CMS', 'caption': 'Імпорт', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI під телефон і ПК',
        'description': (
            'Адаптивний інтерфейс: асортимент читається зі смартфона і з робочого монітора.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог і фільтри',
        'description': (
            'Категорії, підкатегорії, бренд і характеристики. '
            'Список оновлюється без перезавантаження сторінки.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Картка і запит ціни',
        'description': (
            'Специфікація, галерея, PDF-паспорт і кнопка запиту комерційної ціни.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Кабінети за потреби',
        'description': (
            'Окремі прайси для B2B і B2C лишаються опцією пакета. '
            'У стандартне демо їх не збираємо.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Адмінка каталогу',
        'description': (
            'Товари, ціни і контент, імпорт і експорт без програміста.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'SEO, аналітика, запуск',
        'description': (
            'Sitemap, редиректи, GA4 і пікселі. '
            'Сервер, SSL, домен і первинне наповнення.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт з каталогом під ключ',
        'scope': (
            'Діапазон 500–800 €: точна сума після асортиментної сітки. '
            'Архітектура бази, UI, Django і HTMX, адмінка, базова SEO, аналітика, деплой і домен.'
        ),
        'duration': '3 тижні',
        'price': Decimal('500.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Каталог під асортимент',
        'body': (
            'Підбір позицій, технічні паспорти і форма заявки. '
            'Швидкість сторінки тримає контекст і органіку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'PageSpeed 90+',
        'body': 'Каталог на тисячі найменувань без затримки списку. 90+ — умова здачі.',
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Свій код',
        'body': 'Без шаблонної CMS. Немає абонплати за плагіни, які ламаються після оновлень.',
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Запит ціни, не кошик у тексті КП',
        'body': (
            'У пропозиції картка веде на комерційну ціну. '
            'Демо для тесту — стандартний магазин, не версія цього каталогу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед архітектурою і UI.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після тесту і приймання, перед передачею доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка: 35% / 35% / 30%',
        'body': (
            'Старт, екватор після верстки і каталогу, фінал після деплою. '
            'Без відсотків і без фіксованих євро: частки від узгодженої суми.'
        ),
    },
]

TITLE = 'Корпоративний каталог поліграфії під ключ'
LEAD = (
    'Каталог із фільтром і карткою товару, запит комерційної ціни '
    'і запуск за 3 тижні — без комісії конструктора.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає корпоративний сайт з каталогом для поліграфії: бренд, асортимент і заявка на ціну.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без шаблонних CMS.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — список не чекає повного перезавантаження.</li>
<li><strong>500–800 €</strong> — сума після асортиментної сітки.</li>
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
    help = 'Seed print corporate-catalog proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('print'),
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
                'client_name': 'Поліграфія',
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
                'order': 20,
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
