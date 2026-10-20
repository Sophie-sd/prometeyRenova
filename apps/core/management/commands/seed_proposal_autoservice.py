"""
Management command: seed_proposal_autoservice

КП «Комерційна пропозиція — Landing Page для автосервісу» (PDF 20.10.2026):
висококонверсійний лендинг автосервісу під ключ, 250 €, 10 днів; реклама 350–500 €;
комбо «Сайт + Реклама» 500 € при замовленні до 25.10.2026. Імені клієнта в PDF немає.
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

SLUG = 'landing-autoservice-2587'
CLIENT = 'Лендинг автосервісу під ключ'
DEMO_TENANT_SLUG = 'autoservice-9b4fa3'
ISSUED_ON = date(2026, 10, 20)
ORDER = 36

RECS_LEAD = (
    'Сучасний конверсійний лендинг для залучення клієнтів на послуги з технічного '
    'обслуговування авто: Django / HTMX, PageSpeed 95+, запис на СТО та заявки в '
    'Telegram/CRM без перезавантаження сторінки.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 95+'},
    {'order': 2, 'title': 'Mobile First'},
    {'order': 3, 'title': '10 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Hero', 'caption': 'Діагностика · ТО · ремонт', 'is_accent': False},
    {'order': 1, 'title': 'Services', 'caption': 'Напрямки СТО · прайс', 'is_accent': False},
    {'order': 2, 'title': 'Booking', 'caption': 'Запис · квіз · прорахунок', 'is_accent': True},
    {'order': 3, 'title': 'Lead', 'caption': 'Telegram · CRM · пошта', 'is_accent': False},
    {'order': 4, 'title': 'Admin', 'caption': 'Акційні ціни · оффери', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Маркетингова структура та оффер',
        'description': (
            'Професійне проєктування блоків — від сильного головного офферу '
            '(діагностика, ТО, ремонт) до закриття заперечень та закликів (CTA).'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Індивідуальний UI/UX дизайн',
        'description': (
            'Сучасний динамічний інтерфейс в автостилістиці, адаптований під '
            'автовласників та ідеальне відображення на мобільних телефонах і ПК.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Інтерактивні форми швидкого запису',
        'description': (
            'Кастомні форми запису на СТО, квіз-підбір необхідного ремонту або швидкий '
            'прорахунок вартості за маркою авто без перезавантаження сторінки.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Миттєва система лідогенерації',
        'description': (
            'Заявки безперебійно та моментально надходять у Telegram '
            'майстру-приймальнику, в CRM-систему автосервісу або на робочу пошту.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Індивідуальна адмін-панель',
        'description': (
            'Зручна та легка кастомна CMS, яка дозволяє самостійно змінювати акційні '
            'ціни на заміну мастила чи шиномонтаж без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та аналітика',
        'description': (
            'Повна інтеграція Google Tag Manager, GA4, Meta Pixel та налаштування '
            'точного відстеження цільових конверсій (дзвінки, заявки, маршрути).'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Лендинг автосервісу «під ключ»',
        'scope': (
            'Маркетинговий аналіз, чистий код Django/HTMX, дизайн, адмінка, '
            'аналітика, деплой на сервер.'
        ),
        'duration': '10 днів',
        'price': Decimal('250.00'),
        'price_high': None,
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Налаштування та запуск реклами',
        'scope': (
            'Семантика, мінус-слова, Google Ads / Meta Ads, налаштування кабінетів, '
            'супровід навчання алгоритмів.'
        ),
        'duration': '5–7 днів',
        'price': Decimal('350.00'),
        'price_high': Decimal('500.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 2,
        'name': 'Комбо: «Сайт + Реклама»',
        'scope': (
            'Повний комплекс розробки лендингу + налаштування та запуск реклами '
            '(при замовленні до 25.10.2026). Економія від 100 до 250 €!'
        ),
        'duration': '10 днів',
        'price': Decimal('500.00'),
        'price_high': None,
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
            'Відмовляємося від конструкторів, що гальмують роботу. Створюємо чистий '
            'кодописний стек для миттєвого завантаження та високої віддачі від реклами.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 95+',
        'body': (
            'Блискавична швидкість відкриття сторінки утримує автовласника зі смартфона '
            'та не дає йому закрити сайт ще до завантаження прайсу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Стійкість до навантажень',
        'body': (
            'Надійність під час масштабних кампаній у Google Ads та Meta Ads, '
            'відсутність щомісячних платежів за сторонні конструктори та вразливі плагіни.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Презентація послуг СТО',
        'body': (
            'Блок напрямків: комп’ютерна діагностика, ремонт ходової, заміна мастил/ГРМ, '
            'автоелектрика, кондиціонери.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Швидка дія (Mobile First)',
        'body': (
            'Клікабельний телефон для дзвінка в 1 клік, кнопка запису на конкретний час '
            'та схема проїзду по карті.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Формування довіри',
        'body': (
            'Сертифікати майстрів, гарантія на встановлені запчастини та виконані '
            'роботи, прозорий прайс-лист.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Налаштування хостингу, SSL-сертифікату безпеки, підключення робочого домену '
            'та фінальна перевірка аналітики.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%)',
        'body': 'Передплата перед початком проєктування.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%)',
        'body': 'Після тестування перед передачею сайту.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 3 платежів, від 83 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 83 € на місяць. Сума ділиться на '
            '3 рівні платежі (наприклад, по 83 €/міс за лендинг). Старт розробки '
            'відразу після підтвердження.'
        ),
    },
]

TITLE = 'Розробка висококонверсійного лендингу автосервісу під ключ'
LEAD = (
    'Готовий інструмент для продажів, орієнтований на максимальну конвертацію '
    'кожного кліка з реклами у реальний запис автовласника на сервіс та '
    'масштабування вашого автобізнесу.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для продажів, орієнтовані на максимальну конвертацію кожного кліка з реклами у реальний запис автовласника на сервіс та масштабування вашого автобізнесу.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Без конструкторів і без щомісячних платежів за сторонні платформи.</p>
<ul>
<li><strong>PageSpeed 95+</strong> — сторінка відкривається блискавично і утримує автовласника зі смартфона ще до завантаження прайсу.</li>
<li><strong>Комбо «Сайт + Реклама» — 500 €</strong> при замовленні до 25.10.2026. Економія від 100 до 250 €.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 3 платежів). Зв’яжіться з нашою командою для узгодження офферів та старту розробки: office@prometeylabs.com.</p>
""".strip()

# Канон гарантії (рішення Софії 16.10): пожиттєва гарантія на код + 1 рік безкоштовної підтримки. Не абзац із PDF.
GUARANTEE_HTML = """
<p>Ми впевнені у якості нашого коду. Оскільки сайт пишеться з нуля без використання сторонніх модулів чи вразливих CMS-плагінів, він не потребує щомісячних оновлень, які часто ламають звичайні сайти.</p>
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
    help = 'Seed autoservice landing proposal (250 €, 10 днів) + standard demo-landing (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_landing',
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
