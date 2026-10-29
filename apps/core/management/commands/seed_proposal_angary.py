"""
Management command: seed_proposal_angary

КП «Розробка корпоративного сайту з проектування та будівництва ангарів під ключ»
(PDF 21.10.2026): корпоративний сайт під ключ, 450 – 500 €, 14 днів.
Оплата 50/50 або розстрочка 0% (Моно / Приват), 3 платежі від 150–166 €/міс.
Імені клієнта в PDF немає. Демо — стандартний корпоративний сайт (democorp), без змін.
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

SLUG = 'corporate-angary-clg5'
CLIENT = 'Ангари'
DEMO_TENANT_SLUG = 'angary-67ae97'
ISSUED_ON = date(2026, 10, 21)
ORDER = 39

RECS_LEAD = (
    'Технологічний корпоративний ресурс під ключ для залучення прямих комерційних '
    'замовлень на будівництво ангарів: типи конструкцій, калькулятор швидкого '
    'прорахунку, соціальні докази, заявки в Telegram/CRM, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Каталог · портфоліо'},
    {'order': 3, 'title': '14 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Типи ангарів · ціни за м²', 'is_accent': False},
    {'order': 1, 'title': 'Projects', 'caption': 'Об’єкти · географія', 'is_accent': False},
    {'order': 2, 'title': 'Estimate', 'caption': 'Габарити · утеплення', 'is_accent': True},
    {'order': 3, 'title': 'Admin', 'caption': 'Портфоліо · ціни за м²', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Професійний промисловий UI/UX дизайн',
        'description': (
            'Сучасний структурований інтерфейс з акцентом на масштаб об’єктів, '
            'технічні схеми та комфортний перегляд зі смартфонів і ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог типів ангарів та послуг',
        'description': (
            'Розділи за призначенням (агросектор, склади, виробництва, СТО), типами '
            'конструкцій (ЛСТК, чорний метал, тент), строками та цінами за м².'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумна система лідогенерації та розрахунку',
        'description': (
            'Інтерактивна форма запиту кошторису за параметрами (довжина, ширина, '
            'висота, утеплення), заявки з якої миттєво йдуть у Telegram/CRM.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Портфоліо збудованих об’єктів та географія',
        'description': (
            'Кейси з детальними фотозвітами, термінами зведення, характеристиками та '
            'картою реалізованих проєктів по регіонах.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Легка система управління для самостійного додавання нових об’єктів у '
            'портфоліо, оновлення вартості за м² та статей без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та аналітика',
        'description': (
            'Повна інтеграція Google Analytics 4, Meta Pixel, правильна розмітка для '
            'контекстної реклами та комерційного SEO-просування.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт під ключ',
        'scope': (
            'Преміальний дизайн, чистий код (Django/HTMX), кастомна адмін-панель, '
            'каталог рішень, портфоліо об’єктів, форми в Telegram/CRM, аналітика, '
            'деплой та домен.'
        ),
        'duration': '14 днів',
        'price': Decimal('450.00'),
        'price_high': Decimal('500.00'),
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
            'Відмовляємося від шаблонних конструкторів, що сповільнюють роботу. '
            'Створюємо кастомне рішення на чистому та надійному стеку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавичне завантаження сторінок проєктів та детальних '
            'креслень/фотогалерей об’єктів, що забезпечує лідерство в пошуку '
            'Google (SEO).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Enterprise-безпека & Масштаб',
        'body': (
            'Надійний захист бази клієнтів і кошторисів від кібератак, повна '
            'незалежність від сторонніх платних модулів та необмежене масштабування.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Презентація технологій та типів конструкцій',
        'body': (
            'Прямостінні, шатрові, арочні ангари, зерносховища, склади з '
            'сендвіч-панелей.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Калькулятор швидкого прорахунку',
        'body': (
            'Зручний крок для замовника (вибір габаритів будівлі, типу фундаменту, '
            'воріт) з кнопкою «Отримати кошторис».'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Соціальні докази та довіра',
        'body': (
            'Демонстрація власного виробництва металоконструкцій, сертифікати '
            'відповідності, договірні гарантії міцності.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Налаштування хостингу, SSL-сертифікату безпеки, підключення робочого домену '
            'та фінальна перевірка систем збору заявок.'
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
        'body': 'Після тестування перед передачею всіх доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): 3 платежі від 150–166 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 150 € на місяць. Оплата ділиться '
            'на 3 рівні платежі (від 150–166 €/міс) без переплат. Старт робіт відразу '
            'після оформлення.'
        ),
    },
]

TITLE = 'Розробка корпоративного сайту з проектування та будівництва ангарів під ключ'
LEAD = (
    'Готовий інструмент для презентації масштабних будівельних рішень (каркасні, '
    'прямостінні, арочні ангари, зерносховища, логістичні комплекси), залучення '
    'платоспроможних B2B-клієнтів та формування статусного іміджу компанії на ринку.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для автоматизації бізнесу, презентації масштабних будівельних рішень (каркасні, прямостінні, арочні ангари, зерносховища, логістичні комплекси), залучення платоспроможних B2B-клієнтів та формування статусного іміджу компанії на ринку.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Без шаблонних конструкторів і сторонніх платних модулів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — сторінки проєктів, креслення та фотогалереї об’єктів завантажуються блискавично.</li>
<li><strong>Заявки</strong> — запит кошторису за параметрами ангара миттєво в Telegram або CRM.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, 3 платежі). Зв’яжіться з нашою командою для узгодження структури та запуску розробки: office@prometeylabs.com.</p>
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
    help = f'Seed {CLIENT} corporate proposal + classic demo-corp (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_corp',
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
        from apps.democorp.models import CorpSite
        from apps.democorp.services.provision import provision_demo_corp
        from apps.demoshop.models import DemoShop

        DemoShop.objects.filter(proposal=proposal).delete()
        site = CorpSite.objects.filter(proposal=proposal).first()
        if site is None:
            site = CorpSite(
                proposal=proposal,
                name='Demo Site',
                slug=DEMO_TENANT_SLUG,
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
                'kind': Proposal.DemoKind.CORPORATE,
                'corp_catalog': True,
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
