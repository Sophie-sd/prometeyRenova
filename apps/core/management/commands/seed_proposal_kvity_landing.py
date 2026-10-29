"""
Management command: seed_proposal_kvity_landing

КП №1 із пари «Квіти» (троянди, лаванда, саджанці), заявка kp-kvity/2026-10-29-001:
ЛЕНДИНГ під ключ — окрема ціна 250 € (канон сайту: лендінг 250–400 € за 3–7 днів), 7 днів.
БЕЗ адмін-панелі (адмінка з CMS — лише в КП інтернет-магазину shop-kvity-r7l2).
Демо — стандартний demo-лендінг (provision_demo_landing), без змін під клієнта.
На сторінці КП — дві кнопки демо «Лендинг» / «Інтернет-магазин» (Proposal.DEMO_PAIRS).
"""
import sys
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.core.management.commands._kvity_common import seed_rows
from apps.core.proposal_models import Proposal, ProposalSpec

SLUG = 'landing-kvity-t4m9'
CLIENT = 'Квіти: троянди, лаванда, саджанці (лендинг)'
DEMO_TENANT_SLUG = 'kvity-landing-3c91e2'
ISSUED_ON = date(2026, 10, 29)
ORDER = 49
KIND = Proposal.DemoKind.LANDING

TITLE = 'Лендинг для продажу квітів (троянди, лаванда, саджанці) під ключ'
LEAD = (
    'Одна продаюча сторінка під рекламу: показує троянди, лаванду й саджанці та '
    'перетворює кліки з Google і Meta на заявки, які одразу приходять вам у Telegram.'
)
RECS_LEAD = (
    'Технічне завдання (індивідуальні деталі проєкту): посадкова сторінка для прийому '
    'заявок на букети, композиції та посадковий матеріал. Без кошика, онлайн-оплати й адмін-панелі.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'Заявки в Telegram'},
    {'order': 2, 'title': 'Mobile First'},
    {'order': 3, 'title': '7 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Hero', 'caption': 'Оффер · CTA', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Троянди · лаванда · саджанці', 'is_accent': False},
    {'order': 2, 'title': 'Quiz', 'caption': 'Підбір букета · кількість', 'is_accent': True},
    {'order': 3, 'title': 'Trust', 'caption': 'Фото · відгуки', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Заявка → Telegram · пошта', 'is_accent': False},
]

MODULES = [
    {'number': 1, 'order': 0, 'title': 'Маркетингова структура та оффер',
     'description': ('Блоки від головного офферу (свіжі троянди, букети з лавандою, саджанці) '
                     'до відпрацювання заперечень і закликів до дії (CTA).')},
    {'number': 2, 'order': 1, 'title': 'Floral UI/UX дизайн',
     'description': ('Естетичний ніжний інтерфейс під вашу аудиторію, ідеальне відображення на '
                     'смартфонах і ПК.')},
    {'number': 3, 'order': 2, 'title': 'Квіз-підбір і калькулятор кількості',
     'description': ('Форма швидкої заявки, квіз «букет за приводом» і калькулятор кількості квітів '
                     'без перезавантаження сторінки (HTMX). Результат — заявка, а не оплата.')},
    {'number': 4, 'order': 3, 'title': 'Миттєві заявки в Telegram',
     'description': ('Заявки з лендингу одразу приходять у Telegram флористам і на пошту, щоб '
                     'менеджер передзвонив і узгодив букет, дату й доставку.')},
    {'number': 5, 'order': 4, 'title': 'Аналітика й готовність до реклами',
     'description': ('Meta Pixel, Google Tag Manager, GA4 і відстеження конверсій: дзвінки, '
                     'заявки, переходи в месенджери.')},
]

PACKAGES = [
    {'order': 0, 'name': 'Лендинг «Квіти» під ключ',
     'scope': ('Структура й тексти блоків, дизайн, чистий код (Django/HTMX), квіз і форми заявок, '
               'Telegram-сповіщення, аналітика, деплой і підключення вашого домену. Без адмін-панелі, '
               'кошика й онлайн-оплати. Домен і хостинг оплачує клієнт.'),
     'duration': '7 днів', 'price': Decimal('250.00'), 'currency': '€', 'is_recommended': False},
]

SPECS = [
    {'kind': ProposalSpec.Kind.SPEC, 'order': 0, 'title': 'Django / HTML5 / HTMX / JS',
     'body': 'Без важких конструкторів: легкий чистий код, який швидко відкривається зі смартфона.'},
    {'kind': ProposalSpec.Kind.SPEC, 'order': 1, 'title': 'Швидкість на смартфоні',
     'body': 'Оптимізовані фото троянд і лаванди відкриваються швидко, людина не закриває сторінку.'},
    {'kind': ProposalSpec.Kind.SPEC, 'order': 2, 'title': 'Без адмін-панелі',
     'body': ('Лендинг здається готовим, без CMS. Дрібні зміни текстів, цін і фото робимо ми в межах '
              '1 року безкоштовної підтримки. Потрібна власна адмінка й каталог — це КП інтернет-магазину.')},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 0, 'title': 'Асортимент на сторінці',
     'body': ('Сортові троянди (голландські, піоноподібні), лавандові композиції й сухоцвіти, мікс-букети, '
              'посадковий матеріал і саджанці — блоками з фото й ціною «від».')},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 1, 'title': 'Як працює замовлення',
     'body': ('На лендингу немає кошика й онлайн-оплати: клієнт обирає букет або проходить квіз і '
              'залишає заявку. Менеджер передзвонює, узгоджує дату, час і доставку.')},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 2, 'title': 'Довіра',
     'body': ('Фото свіжого зрізу, відгуки клієнтів, умови свіжості й доставки — з ваших матеріалів '
              '(фото й відгуки надає клієнт).')},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 3, 'title': 'Реклама — окрема послуга',
     'body': ('Налаштування Google Ads / Meta Ads у ціну лендингу не входить: окремо 400 €, 7–10 днів. '
              'Рекламний бюджет клієнт платить напряму рекламним кабінетам.')},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 4, 'title': 'Деплой та запуск',
     'body': ('Хостинг, SSL, підключення домену, перевірка форм і сповіщень. Домен і хостинг купує й '
              'оплачує клієнт; ми допомагаємо обрати й усе налаштовуємо.')},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 0, 'title': '1-й платіж (50%) — 125 €',
     'body': 'Передплата перед стартом робіт.'},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 1, 'title': '2-й платіж (50%) — 125 €',
     'body': 'Після тестування, перед передачею доступів.'},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 2,
     'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів по 50 €/міс.',
     'body': ('Оплата частинами від Monobank та ПриватБанк без відсотків. Договір розстрочки клієнт '
              'оформлює з банком сам.')},
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда розробників і маркетологів. Це КП саме на <strong>лендинг</strong>: одна продаюча сторінка для збору заявок на троянди, лаванду й саджанці з реклами.</p>
<ul>
<li><strong>Що отримуєте</strong> — оффер, каталог-блоки з фото, квіз-підбір букета, форми заявок, Telegram-сповіщення, аналітика.</li>
<li><strong>Чого немає в лендингу</strong> — адмін-панелі (CMS), кошика й онлайн-оплати. Це є в окремому КП на інтернет-магазин.</li>
<li><strong>Ціна окремо</strong> — лендинг 250 €, 7 днів. Реклама — окремо, 400 €.</li>
<li><strong>Що робить клієнт</strong> — надає фото, ціни й відгуки, оплачує домен, хостинг і рекламний бюджет.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. office@prometeylabs.com</p>
""".strip()


class Command(BaseCommand):
    help = 'Seed flowers LANDING proposal (250 €, без адмінки) + standard demo-landing (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('--no-demo', action='store_true', help='Тільки КП, без демо')

    def handle(self, *args, **options):
        from apps.core.management.commands._proposal_seed_guard import seed_must_skip
        if (skip_reason := seed_must_skip(SLUG)):
            self.stdout.write(f'Skip {SLUG}: {skip_reason}')
            return
        proposal, created = seed_rows(sys.modules[__name__])
        if not options['no_demo']:
            self._provision_demo(proposal)
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Updated'}: /proposal/{SLUG}/"))

    def _provision_demo(self, proposal):
        """Стандартний demo-лендінг (як у всіх КП), без змін під клієнта."""
        from apps.demolanding.models import LandingSite
        from apps.demolanding.services.provision import provision_demo_landing

        if not LandingSite.objects.filter(proposal=proposal).exists():
            LandingSite(proposal=proposal, name='Demo Landing', slug=DEMO_TENANT_SLUG).save()
        site = provision_demo_landing(proposal)
        if site.name != 'Demo Landing':
            site.name = 'Demo Landing'
            site.save(update_fields=['name'])
        self.stdout.write(self.style.SUCCESS(f'Demo: {site.get_absolute_url()} (slug={site.slug})'))
