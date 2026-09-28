"""
Management command: seed_proposal_catalog

Idempotent заливка КП «Корпоративний каталог» (PDF 28.09.2026).
Без демо-тенанта: сторінка лише за прямим посиланням.
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

SLUG = 'corporate-catalog-a7f3'

RECS_LEAD = (
    'Корпоративний каталог із заявкою на розрахунок: '
    'Django / HTMX, тисячі позицій, без кошика інтернет-магазину.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'PostgreSQL'},
    {'order': 3, 'title': '40 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Brand', 'caption': 'Імідж', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Фільтри', 'is_accent': True},
    {'order': 2, 'title': 'Card', 'caption': 'PDF · запит', 'is_accent': False},
    {'order': 3, 'title': 'Order', 'caption': 'Специфікація', 'is_accent': False},
    {'order': 4, 'title': 'Desk', 'caption': 'Статуси', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX під телефон і ПК',
        'description': (
            'Візуальний стиль під нішу. '
            'Телефон, планшет і десктоп без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог з фільтрами',
        'description': (
            'Категорії, бренди, модифікації і технічні характеристики. '
            'Список оновлюється без перезавантаження сторінки.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Картка і PDF',
        'description': (
            'Специфікація, галерея, файл документації і форма швидкого запиту.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Заявка на розрахунок',
        'description': (
            'Клієнт збирає перелік позицій, вказує доставку або отримання '
            'і надсилає заявку. Це не оплата карткою в кошику магазину.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Диспетчер заявок',
        'description': (
            'Список звернень із позиціями. Статуси: новий, в обробці, '
            'підтверджено, відвантажено. Сповіщення менеджеру.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Адмінка, SEO, запуск',
        'description': (
            'Товари і масове редагування цін без програміста. '
            'Schema.org, Open Graph, Google Analytics 4, сервер і SSL.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт-каталог під ключ',
        'scope': (
            'Логіка замовлень і PostgreSQL, адаптивний UI, Django і HTMX, '
            'картки товарів, адмінка асортименту і заявок, SEO, аналітика, деплой і SSL.'
        ),
        'duration': '40 днів',
        'price': Decimal('1500.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Заявка замість кошика магазину',
        'body': (
            'Клієнт складає специфікацію позицій і параметри отримання. '
            'Заявка йде на розрахунок або підтвердження, без оплати на сайті.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Статуси обробки',
        'body': (
            'Новий, в обробці, підтверджено, відвантажено. '
            'Менеджер бачить позиції звернення в одному списку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Кабінет за потреби',
        'body': (
            'B2B-партнер може бачити історію запитів і статус відвантаження, '
            'якщо цей кабінет входить у затверджений обсяг.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без WordPress, OpenCart і Tilda',
        'body': (
            'Конструктор не тримає тисячі позицій і історію угод. '
            'Каталог і заявки живуть у своєму коді.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+ на великому прайсі',
        'body': (
            'Тисячі позицій не мають вішати фільтр. '
            '90+ на телефоні й ПК — умова здачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50% — 750 €',
        'body': 'Перед стартом: прототип, UI/UX і базова архітектура бази.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50% — 750 €',
        'body': 'Після тесту заявок, публікації на сервер і передачі доступів.',
    },
]

TITLE = 'Корпоративний каталог із обробкою замовлень'
LEAD = (
    'Імідж бренду і каталог, де клієнт збирає специфікацію '
    'і надсилає заявку на розрахунок — без кошика магазину.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає платформу на стику сайту і обліку заявок: продукція на екрані, замовлення в одному списку.</p>
<p>Стек: <strong>Django (Python) · HTMX · HTML5 · CSS3 · JavaScript · PostgreSQL</strong>. Без WordPress, OpenCart і Tilda.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — тисячі позицій не вішають інтерфейс.</li>
<li><strong>Заявка</strong> — розрахунок і статус, не оплата карткою на вітрині.</li>
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
    help = 'Seed corporate catalog proposal without a demo tenant'

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
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action}: /proposal/{SLUG}/ '
            f'({proposal.modules.count()} modules, '
            f'{proposal.packages.count()} packages, no demo)'
        ))

    def _seed_rows(self):
        proposal, created = Proposal.objects.update_or_create(
            slug=SLUG,
            defaults={
                'client_name': 'Корпоративний каталог',
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
                'kind': Proposal.DemoKind.CORPORATE,
                'corp_catalog': False,
                'is_published': True,
                'order': 14,
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
