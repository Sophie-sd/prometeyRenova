"""
Management command: seed_proposal_plumber

КП «Комерційна пропозиція: Landing Page послуг сантехніка» (PDF 20.10.2026):
висококонверсійний лендинг послуг сантехніка під ключ, 200 €, 10–14 днів;
реклама 200–250 €, 5–7 днів; комбо «Сайт + Реклама» 400 €, 10–14 днів.
Оплата 50/50 (100 € + 100 €) або розстрочка 0% до 3 платежів по 67 €/міс.
Імені клієнта в PDF немає.
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

SLUG = 'landing-plumber-c376'
CLIENT = 'Лендинг послуг сантехніка під ключ'
DEMO_TENANT_SLUG = 'plumber-711b27'
ISSUED_ON = date(2026, 10, 20)
ORDER = 38

RECS_LEAD = (
    'Розробка сучасного комерційного лендингу, сфокусованого на термінові та планові '
    'виклики сантехніка: Django / HTMX, PageSpeed 95+, форми швидкого виклику та '
    'заявки в Telegram/CRM без перезавантаження сторінки.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 95+'},
    {'order': 2, 'title': 'Mobile First'},
    {'order': 3, 'title': '10–14 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Hero', 'caption': 'Оффер · виїзд за 30–45 хв', 'is_accent': False},
    {'order': 1, 'title': 'Services', 'caption': 'Послуги майстра · прайс', 'is_accent': False},
    {'order': 2, 'title': 'Call', 'caption': 'Виклик · калькулятор вартості', 'is_accent': True},
    {'order': 3, 'title': 'Lead', 'caption': 'Telegram · пошта · CRM', 'is_accent': False},
    {'order': 4, 'title': 'Admin', 'caption': 'Розцінки · контакти · банери', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Маркетингова структура та оффер',
        'description': (
            'Професійне проєктування блоків — від сильного офферу (швидкий виїзд за '
            '30-45 хв) до прайс-листа, гарантій і закликів до дії (CTA).'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Індивідуальний Mobile-First UI/UX дизайн',
        'description': (
            'Чистий, довірчий інтерфейс, оптимізований насамперед під смартфони з '
            'великими кнопками швидкого дзвінка та замовлення майстра.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Інтерактивні форми швидкого виклику',
        'description': (
            'Кастомні форми виклику майстра, експрес-калькулятор вартості робіт за типом '
            'проблеми без перезавантаження сторінки завдяки HTMX.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Миттєва система лідогенерації',
        'description': (
            'Заявки з сайту моментально приходять у Telegram майстру або диспетчеру, '
            'дублюються на пошту або передаються у CRM-систему.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Індивідуальна адмін-панель',
        'description': (
            'Зручна кастомна CMS, яка дозволяє самостійно змінювати розцінки на послуги, '
            'редагувати контакти, графік чи банери без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та аналітика',
        'description': (
            'Інтеграція рекламних пікселів Meta, тегів Google Ads, GA4 та точне '
            'відстеження конверсій (кліки на номер телефону, виклик майстра).'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Лендинг сантехніка «під ключ»',
        'scope': (
            'Маркетинговий аналіз, чистий код (Django/HTMX), дизайн, адмінка, форми, '
            'аналітика, деплой та домен.'
        ),
        'duration': '10–14 днів',
        'price': Decimal('200.00'),
        'price_high': None,
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Налаштування та запуск реклами',
        'scope': (
            'Збір гарячих запитів, мінус-слова, налаштування кабінету Google Ads, '
            'відстеження дзвінків і заявок.'
        ),
        'duration': '5–7 днів',
        'price': Decimal('200.00'),
        'price_high': Decimal('250.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 2,
        'name': 'Комбо: «Сайт + Реклама»',
        'scope': (
            'Повний пакет: високоефективний лендинг + запуск реклами «під ключ» для '
            'стабільного щоденного потоку викликів.'
        ),
        'duration': '10–14 днів',
        'price': Decimal('400.00'),
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
            'Відмовляємося від шаблонних конструкторів, які гальмують роботу сайту. '
            'Розробляємо оптимізовані кодописні рішення на надійному стеку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 95+',
        'body': (
            'Блискавична швидкість завантаження утримує користувача зі смартфона при '
            'аварійній ситуації (протікання, засмічення) без втрати контакту.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Стійкість до сплесків трафіку',
        'body': (
            'Надійність під час активного показу в Google Ads за запитами «виклик '
            'сантехніка», відсутність абонплат за платформи конструкторів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Каталог послуг майстра',
        'body': (
            'Усунення протікань і засмічень, монтаж труб/бойлерів, встановлення ванн, '
            'унітазів, змішувачів, опалення.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Елементи довіри',
        'body': (
            'Фіксований прайс без прихованих платежів, гарантія на монтаж до 12-24 міс., '
            'відгуки реальних замовників з фото.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Миттєвий зв’язок у 1 клік',
        'body': (
            'Закріплена кнопка прямого дзвінка та переходу у Viber/Telegram на мобільних '
            'пристроях.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Налаштування хостингу, захищеного SSL-сертифікату безпеки, підключення '
            'робочого домену та фінальна перевірка форм.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%, 100 €)',
        'body': 'Передплата перед стартом проєктування.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%, 100 €)',
        'body': 'Після тестування перед передачею сайту.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 3 платежів, від 67 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 67 € на місяць. Сума ділиться на '
            '3 рівні платежі по 67 €/міс без відсотків. Старт розробки відразу після '
            'підтвердження.'
        ),
    },
]

TITLE = 'Розробка висококонверсійного лендингу послуг сантехніка під ключ'
LEAD = (
    'Готовий інструмент для продажів, орієнтований на максимальну конвертацію кожного '
    'кліка з реклами в реальний терміновий виклик майстра, високий чек на монтажні '
    'роботи та масштабування вашого бізнесу.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для продажів, орієнтовані на максимальну конвертацію кожного кліка з реклами в реальний терміновий виклик майстра, високий чек на монтажні роботи та масштабування вашого бізнесу.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Без шаблонних конструкторів і без абонплат за платформи конструкторів.</p>
<ul>
<li><strong>PageSpeed 95+</strong> — блискавичне завантаження утримує користувача зі смартфона при аварійній ситуації (протікання, засмічення) без втрати контакту.</li>
<li><strong>Комплексне рішення «Сайт + Налаштування реклами» — 400 €</strong>: розробка лендингу + налаштування та запуск пошукової реклами Google Ads. Готовий інструмент для швидкого отримання замовлень з першого дня.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 3 платежів). Зв’яжіться з нашою командою для узгодження списку послуг та запуску розробки: office@prometeylabs.com.</p>
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
    help = 'Seed plumber landing proposal (200 €, 10–14 днів) + standard demo-landing (idempotent)'

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
