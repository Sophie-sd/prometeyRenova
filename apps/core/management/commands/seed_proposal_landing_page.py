"""
Management command: seed_proposal_landing_page

КП «Комерційна пропозиція — Розробка Landing Page» (PDF 20.10.2026):
висококонверсійний лендінг під ключ, 300 €, 14 днів. Імені клієнта в PDF немає.
Демо — стандартний demo-лендінг (demolanding), без змін. Це не версія сайту клієнта.
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

SLUG = 'landing-page-k8r2'
CLIENT = 'Landing Page під ключ'
DEMO_TENANT_SLUG = 'landing-page-4d7e2a'
ISSUED_ON = date(2026, 10, 20)
ORDER = 35

RECS_LEAD = (
    'Індивідуальний посадковий веб-ресурс, оптимізований під прийом платного '
    'рекламного трафіку та високу конверсію: Django / HTMX, PageSpeed 95+, '
    'заявки в Telegram/CRM без перезавантаження сторінки.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 95+'},
    {'order': 2, 'title': 'Mobile First'},
    {'order': 3, 'title': '14 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Hero', 'caption': 'УТП · CTA', 'is_accent': False},
    {'order': 1, 'title': 'Trust', 'caption': 'Кейси · відгуки', 'is_accent': False},
    {'order': 2, 'title': 'Quiz', 'caption': 'Квіз · калькулятор', 'is_accent': True},
    {'order': 3, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
    {'order': 4, 'title': 'Admin', 'caption': 'Ціни · оффери · банери', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Маркетингова структура та оффер',
        'description': (
            'Професійне проєктування логіки блоків — від сильного УТП до '
            'відпрацювання сумнівів клієнта та закликів до дії (CTA).'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Індивідуальний UI/UX дизайн',
        'description': (
            'Сучасний динамічний інтерфейс, адаптований під вашу аудиторію та '
            'ідеальне відображення на мобільних пристроях і ПК.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Інтерактивні елементи залучення',
        'description': (
            'Кастомні форми зворотного зв’язку, лід-магніти, квіз-опитування або '
            'інтерактивні калькулятори прорахунку вартості.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Миттєва система лідогенерації',
        'description': (
            'Заявки безперебійно та моментально приходять у Telegram, CRM-систему '
            'або на робочу пошту без перезавантаження сторінки.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Індивідуальна адмін-панель',
        'description': (
            'Зручна та легка кастомна CMS, яка дозволяє самостійно змінювати акційні '
            'ціни, тексти офферів та банери без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та аналітика',
        'description': (
            'Повна інтеграція рекламних пікселів Meta, тегів Google Ads, GA4 та точне '
            'налаштування відстеження цільових конверсій.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Висококонверсійний Лендинг під ключ',
        'scope': (
            'Маркетинговий аналіз, кодописна розробка, дизайн, кастомна адмін-панель, '
            'швидкі форми, інтеграція аналітики та месенджерів/CRM, запуск на сервері '
            'та підключення домену.'
        ),
        'duration': '14 днів',
        'price': Decimal('300.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Django / HTML5 / HTMX / JS',
        'body': (
            'Відмовляємося від конструкторів, що сповільнюють завантаження. '
            'Створюємо чистий кодописний стек для високої віддачі від реклами.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 95+',
        'body': (
            'Блискавичне відкриття сторінки утримує користувача та не дає йому закрити '
            'вкладку ще до повного завантаження сайту.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Стійкість до сплесків трафіку',
        'body': (
            'Надійність під час масштабних кампаній у Google Ads та Meta Ads, '
            'відсутність щомісячних платежів за платформи конструкторів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Продаюча структура',
        'body': (
            'Чітке позиціонування продукту/послуги, вигоди, соціальні докази (кейси, '
            'відгуки, сертифікати) та сильний фінальний заклик.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Безшовна взаємодія (HTMX)',
        'body': (
            'Відправка заявок у формах без оновлення сторінки, миттєве сповіщення '
            'користувача про успішне бронювання.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Мобільний пріоритет (Mobile First)',
        'body': (
            'Максимальна зручність взаємодії зі смартфонів, де зосереджено до 85% '
            'рекламного трафіку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Налаштування хостингу, захищеного SSL-сертифіката безпеки, підключення '
            'робочого домену та фінальне тестування аналітики.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (150 €)',
        'body': 'Передоплата перед стартом проєктування та дизайну.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (150 €)',
        'body': 'Після тестів перед передачею доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): 3 × 100 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без комісій — від 100 € на місяць. Сума ділиться на 3 рівні '
            'платежі по 100 €/міс без відсотків. Старт розробки одразу після '
            'підтвердження.'
        ),
    },
]

TITLE = 'Розробка висококонверсійного Landing Page під ключ'
LEAD = (
    'Готовий інструмент для продажів, орієнтований на максимальну конвертацію '
    'кожного кліка з реклами в реальну заявку та масштабування вашого бізнесу.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для продажів, орієнтовані на максимальну конвертацію кожного кліка з реклами в реальну заявку та масштабування вашого бізнесу.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Без конструкторів і без щомісячних платежів за платформи.</p>
<ul>
<li><strong>PageSpeed 95+</strong> — сторінка відкривається блискавично і утримує користувача з реклами.</li>
<li><strong>HTMX</strong> — заявки відправляються без оновлення сторінки та миттєво приходять у Telegram, CRM або на пошту.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%). Зв’яжіться з нами для узгодження структури та запуску розробки: office@prometeylabs.com.</p>
""".strip()

# Канон гарантії (рішення Софії 16.10): пожиттєва гарантія на код + 1 рік безкоштовної підтримки. Не абзац із PDF.
GUARANTEE_HTML = """
<p>Ми впевнені у якості нашого коду. Оскільки сайт пишеться з нуля без використання сторонніх модулів чи плагінів, він не потребує щомісячних оновлень, які часто ламають звичайні сайти.</p>
<p>Ми надаємо <strong>пожиттєву гарантію на код</strong>: технічні баги з нашої вини виправляємо безкоштовно без обмеження строку. Плюс <strong>1 рік безкоштовної підтримки</strong>: якщо щось зламалося, дрібні правки, консультації.</p>
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
    help = 'Seed Landing Page proposal (300 €, 14 днів) + standard demo-landing (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_landing',
        )

    def handle(self, *args, **options):
        from apps.core.management.commands._proposal_seed_guard import seed_must_skip
        if (skip_reason := seed_must_skip(SLUG)):
            self.stdout.write(f'Skip {SLUG}: {skip_reason}')
            return
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
        from apps.demolanding.models import LandingSite
        from apps.demolanding.services.provision import provision_demo_landing

        site = LandingSite.objects.filter(proposal=proposal).first()
        if site is None:
            site = LandingSite(
                proposal=proposal,
                name='Demo Landing',
                slug=DEMO_TENANT_SLUG,
            )
            site.save()
        site = provision_demo_landing(proposal)
        if site.name != 'Demo Landing':
            site.name = 'Demo Landing'
            site.save(update_fields=['name'])
        self.stdout.write(self.style.SUCCESS(
            f'Demo: {site.get_absolute_url()} (slug={site.slug})'
        ))

    def _seed_rows(self):
        proposal, created = Proposal.objects.update_or_create(
            slug=SLUG,
            defaults={
                'client_name': CLIENT,
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
                'issued_on': ISSUED_ON,
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
                'kind': Proposal.DemoKind.LANDING,
                'corp_catalog': False,
                'is_published': True,
                'order': ORDER,
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
