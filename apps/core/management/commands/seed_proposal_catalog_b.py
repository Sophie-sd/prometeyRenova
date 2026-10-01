"""
Management command: seed_proposal_catalog_b

КП «Сайт з каталогом» (PDF 01.10.2026): корпоративний сайт з каталогом
+ стандартне корпоративне демо. Це не версія сайту клієнта
і не стара КП corporate-catalog-a7f3.
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

SLUG = 'corporate-catalog-b7f3'

RECS_LEAD = (
    'Корпоративний сайт з каталогом: Django / HTMX, '
    'фільтр без перезавантаження, заявка на ціну, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Каталог'},
    {'order': 3, 'title': '21 день'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Фільтри', 'is_accent': True},
    {'order': 1, 'title': 'Card', 'caption': 'PDF · ціна', 'is_accent': False},
    {'order': 2, 'title': 'Lead', 'caption': 'Заявка', 'is_accent': False},
    {'order': 3, 'title': 'CMS', 'caption': 'Ціни', 'is_accent': False},
    {'order': 4, 'title': 'Ads', 'caption': 'Окремо', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI каталогу',
        'description': (
            'Структурований інтерфейс: список і картка читаються зі смартфона і з ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Категорії і фільтри',
        'description': (
            'Ієрархія категорій, брендів, модифікацій і характеристик. '
            'Список оновлюється без перезавантаження сторінки.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Картка і запит ціни',
        'description': (
            'Специфікація, галерея, PDF-паспорт і форма запиту ціни. '
            'Це не кошик інтернет-магазину.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Адмінка',
        'description': (
            'Товари, ціни і банери змінює менеджер без розробника.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'SEO і аналітика',
        'description': (
            'Мета-теги, Open Graph, GA4, Google Tag Manager і Meta Pixel.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Деплой',
        'description': 'Сервер, SSL і корпоративний домен.',
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт з каталогом',
        'scope': (
            'Базовий контракт: архітектура бази, адаптивний UI, каталог з фільтрами, '
            'панель керування, SEO, перенесення матеріалів, деплой.'
        ),
        'duration': '21 день',
        'price': Decimal('550.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Налаштування рекламного кабінету',
        'scope': (
            'Окрема послуга: аудит аудиторії, Google Ads і Meta Ads, '
            'семантика, конверсії і події. У демо кабінет не збираємо.'
        ),
        'duration': '3–5 днів',
        'price': Decimal('400.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 2,
        'name': 'Сайт + рекламний кабінет',
        'scope': (
            '850 € замість 950 €. Сайт з каталогом 550 € і рекламний кабінет '
            '300 € замість 400 €, одноразово до сайту. Цілі й події під час розробки.'
        ),
        'duration': '21 день',
        'price': Decimal('850.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Каталог і ліди',
        'body': (
            'Підбір позицій за параметрами. '
            'Заявка на розрахунок і контактна форма, без оплати на сайті.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'PageSpeed 90+',
        'body': 'Каталог на тисячі позицій без затримки списку. 90+ — умова здачі.',
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Свій код',
        'body': 'Без WordPress і Tilda. Немає абонплати за плагіни.',
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Кабінет і 1С — пізніше',
        'body': (
            'Персональний кабінет, CRM і склад лишаються можливістю розширення. '
            'У базове демо їх не збираємо.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед стартом і проєктуванням.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після тесту і демонстрації, перед публікацією на домені.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка: 4 рівні частини',
        'body': 'Чотири платежі на час реалізації, без комісії і без фіксованих євро.',
    },
]

TITLE = 'Корпоративний сайт з каталогом під ключ'
LEAD = (
    'Каталог із фільтром, картка з паспортом і запит ціни. '
    'Рекламний кабінет — окремий пакет, не частина демо.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає корпоративний сайт з каталогом: підбір позицій і заявка на розрахунок.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без WordPress і Tilda.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — список не чекає повного перезавантаження.</li>
<li><strong>550 € / 21 день</strong> — базовий контракт. Разом із рекламою — 850 € замість 950 €.</li>
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
    help = 'Seed catalog-b corporate proposal + classic demo-corp (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_corp',
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
        from apps.democorp.models import CorpSite
        from apps.democorp.services.provision import provision_demo_corp

        site = CorpSite.objects.filter(proposal=proposal).first()
        if site is None:
            site = CorpSite(
                proposal=proposal,
                name='Demo Site',
                slug=CorpSite.generate_slug('catalog-b'),
            )
            site.save()
        site = provision_demo_corp(proposal)
        if site.name != 'Demo Site':
            site.name = 'Demo Site'
            site.save(update_fields=['name'])
        self.stdout.write(self.style.SUCCESS(
            f'Demo: {site.get_absolute_url()} (slug={site.slug})'
        ))

    def _seed_rows(self):
        proposal, created = Proposal.objects.update_or_create(
            slug=SLUG,
            defaults={
                'client_name': 'Сайт з каталогом',
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
                'issued_on': date(2026, 10, 1),
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
                'kind': Proposal.DemoKind.CORPORATE,
                'corp_catalog': True,
                'is_published': True,
                'order': 22,
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
