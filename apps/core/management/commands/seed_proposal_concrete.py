"""
Management command: seed_proposal_concrete

КП «Вироби з бетону» (PDF 30.09.2026): корпоративний сайт з каталогом
+ стандартне корпоративне демо. Це не версія сайту клієнта.
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

SLUG = 'corporate-concrete-a7f3'

RECS_LEAD = (
    'Корпоративний сайт виробника бетонних виробів: '
    'Django / HTMX, каталог із запитом ціни, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Каталог виробів'},
    {'order': 3, 'title': '21 день'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Home', 'caption': 'Фактури', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Запит ціни', 'is_accent': True},
    {'order': 2, 'title': 'Works', 'caption': 'Об’єкти', 'is_accent': False},
    {'order': 3, 'title': 'Lead', 'caption': 'Telegram', 'is_accent': False},
    {'order': 4, 'title': 'CMS', 'caption': 'Ціни · фото', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI під бетонні вироби',
        'description': (
            'Плитка, малі форми, стільниці і фасади на телефоні і на ПК. '
            'Фактура читається без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог і галерея',
        'description': (
            'Фільтр за категоріями, фото текстур і реалізованих об’єктів. '
            'На картці — характеристики і запит ціни, не кошик магазину.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Заявка на розрахунок',
        'description': (
            'Форма вартості і замовлення дзвінка йде в Telegram і на пошту '
            'без перезавантаження сторінки.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Виробництво і довіра',
        'description': (
            'Сторінки про виробництво, сертифікати, портфоліо робіт і статті '
            'для забудовників, дизайнерів і приватних клієнтів.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Адмінка каталогу',
        'description': (
            'Ціни, фото і склад каталогу змінює менеджер без розробника.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'SEO і запуск',
        'description': (
            'GA4, Meta Pixel, Schema.org. Сервер, SSL, пошта і домен.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Базовий корпоративний сайт',
        'scope': (
            'Діапазон 650–750 €: сума після обсягу контенту і дизайну. '
            'UI, Django і HTMX, базовий каталог виробів, адмінка, SEO, '
            'заявки в Telegram, деплой і домен.'
        ),
        'duration': '21 день',
        'price': Decimal('650.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Головна і каталог',
        'body': (
            'Перший екран, напрямки, переваги виробництва. '
            'Перелік виробів з фото, характеристиками і запитом ціни.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Виробництво і об’єкти',
        'body': (
            'Технології, потужності, сертифікати і галерея виконаних робіт.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Контакти',
        'body': (
            'Виклик менеджера, карта виробництва або складу, заявка в Telegram.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Калькулятор і 1С — пізніше',
        'body': (
            'Калькулятор бетону, кабінет опту і ERP лишаються можливістю розширення. '
            'У базове демо їх не збираємо.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед стартом, щоб зафіксувати термін і почати проєктування.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після погодження і тесту, перед вивантаженням на робочий домен.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка: 4 × від 162,50 до 187,50 €',
        'body': (
            'Чотири рівні частини раз на місяць, без відсотків. '
            '162,50 € — від суми 650 €, 187,50 € — від 750 €.'
        ),
    },
]

TITLE = 'Корпоративний сайт для виробів з бетону'
LEAD = (
    'Каталог плитки, малих форм і фасадів, галерея об’єктів '
    'і заявка на розрахунок — без комісії конструктора.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає корпоративний сайт для виробника бетонних виробів: асортимент, фактури і прямі заявки.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без Tilda, Wix і WordPress.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — галерея відкривається на телефоні одразу.</li>
<li><strong>650–750 €</strong> — сума після обсягу контенту і дизайну.</li>
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
    help = 'Seed concrete corporate proposal + classic demo-corp (idempotent)'

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
                slug=CorpSite.generate_slug('concrete'),
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
                'client_name': 'Вироби з бетону',
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
                'kind': Proposal.DemoKind.CORPORATE,
                'corp_catalog': True,
                'is_published': True,
                'order': 21,
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
