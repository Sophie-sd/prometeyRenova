"""
Management command: seed_proposal_corporate_turnkey

КП «Розробка корпоративного сайту під ключ: 3 пакети масштабування бізнесу»
(PDF 23.10.2026, українською): BASE 900 € (до 25–30 днів), PREMIUM 1 600 €
(до 30 днів, популярний вибір), PLATINUM 3 500 € (до 30–40 днів).
Оплата 50% передоплата / 50% фінальний платіж. Імені клієнта / ніші в PDF немає.
Демо — стандартний корпоративний сайт (democorp), без змін.
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

SLUG = 'corporate-pid-klyuch-58wg'
CLIENT = 'Корпоративний сайт під ключ'
DEMO_TENANT_SLUG = 'korporatyvnyi-8ca906'
ISSUED_ON = date(2026, 10, 23)
ORDER = 42

TITLE = 'Розробка корпоративного сайту під ключ: 3 пакети масштабування бізнесу'
LEAD = (
    'Готові інструменти для автоматизації процесів, залучення великих B2B/B2C '
    'клієнтів та формування стійкого преміального іміджу вашого бренду в цифровому '
    'просторі.'
)
# Зведена матриця можливостей з PDF — рядки нижче (RECOMMENDATION), по одному на параметр.
RECS_LEAD = (
    'Зведена матриця можливостей пакетів BASE (900 €), PREMIUM (1 600 €) та '
    'PLATINUM (3 500 €).'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'BASE · PREMIUM · PLATINUM'},
    {'order': 3, 'title': 'до 25–40 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Design', 'caption': 'UI/UX · адаптив', 'is_accent': False},
    {'order': 1, 'title': 'Services', 'caption': 'Послуги · інтерактивні блоки', 'is_accent': False},
    {'order': 2, 'title': 'Lead', 'caption': 'HTMX · Telegram · CRM · Email', 'is_accent': True},
    {'order': 3, 'title': 'Admin', 'caption': 'Django CMS · тексти · банери', 'is_accent': False},
    {'order': 4, 'title': 'Launch', 'caption': 'GA4 · GTM · пікселі · домен', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Преміальний UI/UX дизайн',
        'description': (
            'Індивідуальний адаптивний інтерфейс, оптимізований для бездоганного '
            'відображення на смартфонах, планшетах та ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Презентація послуг та інтерактивні блоки',
        'description': (
            'Логічна архітектура сторінок, динамічні блоки вигод та інтерактивні '
            'елементи для максимального утримання клієнта.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумна система лідогенерації (HTMX)',
        'description': (
            'Кастомні форми зворотного зв’язку, заявки з яких миттєво та без '
            'перезавантаження сторінки надходять у Telegram, CRM або на Email.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Розділи формування авторитету',
        'description': (
            'Сторінки «Про компанію», «Портфоліо/Кейси», «Блог та новини» для '
            'формування довіри та публікації експертного контенту.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Кастомна панель керування (CMS)',
        'description': (
            'Легка та зручна Django-адмінка, що дозволяє самостійно оновлювати тексти, '
            'міняти банери чи контакти без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та деплой',
        'description': (
            'Повна інтеграція рекламних пікселів, систем аналітики (GA4/GTM), '
            'розгортання на сервері та підключення вашого домену.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'BASE · Базовий стандарт',
        'scope': (
            'Корпоративний сайт на чистому коді Django; сучасний адаптивний UI/UX '
            'дизайн; генерація контенту ШІ (Medium рівень); повна внутрішня '
            'SEO-підготовка мета-тегів; вбудована зручна адмін-панель (1 мова); збір '
            'та обробка заявок з форм; деплой на сервер та прив’язка домену.'
        ),
        'duration': 'до 25–30 днів',
        'price': Decimal('900.00'),
        'price_high': None,
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'PREMIUM · Бізнес масштаб',
        'scope': (
            'Все, що входить у пакет BASE; індивідуальний UI/UX дизайн з нуля під '
            'нішу; ШІ-медіа Premium + ручний копірайтинг; розширене семантичне SEO + '
            'перелінковка; налаштування та запуск реклами (Google/Meta); миттєві '
            'сповіщення лідів у Telegram / Email; мультимовна адмінка + 10 відгуків '
            'у Google Maps.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('1600.00'),
        'price_high': None,
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'PLATINUM · Абсолютне домінування',
        'scope': (
            'Все з пакетів BASE та PREMIUM; ексклюзивний UI/UX + преміальна анімація; '
            'ШІ-екосистема: AI-помічник + автономний агент; персональна CRM-система + '
            'власний Telegram-бот; локалізація сайту до 10 мовних версій; 6 місяців '
            'SEO-супроводу + 60 відгуків Google; до 5 рекламних кампаній + 3 міс. '
            'ведення.'
        ),
        'duration': 'до 30–40 днів',
        'price': Decimal('3500.00'),
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
            'Принципово відмовляємося від конструкторів (WordPress, Tilda). Створюємо '
            'чисті кодописні рішення на надійній Enterprise-архітектурі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Швидкість PageSpeed 90+',
        'body': (
            'Блискавичне відкриття сторінок без зайвих скриптів покращує поведінкові '
            'фактори й забезпечує пріоритетне ранжування в Google (SEO).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Enterprise-безпека & Масштаб',
        'body': (
            'Вбудований захист від SQL-ін’єкцій, XSS-атак та зламів. Можливість '
            'підключення AI-асистентів та особистих кабінетів без переробки ядра.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Архітектура та PageSpeed 90+',
        'body': (
            'BASE: чистий код Django/HTMX · PREMIUM: чистий код Django/HTMX · '
            'PLATINUM: чистий код Django/HTMX.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Рівень SEO-оптимізації',
        'body': (
            'BASE: внутрішнє SEO мета-тегів · PREMIUM: розширена семантика + статті · '
            'PLATINUM: глобальне SEO + 6 міс. супровід.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Реклама та просування',
        'body': (
            'BASE: — · PREMIUM: 1 кабінет / кампанія (старт) · '
            'PLATINUM: до 5 кампаній + 3 міс. ведення.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Інтеграція ШІ та автоматизація',
        'body': (
            'BASE: ШІ-контент (Medium) · PREMIUM: ШІ-контент (Premium) · '
            'PLATINUM: ШІ-асистент + CRM + ТГ-бот.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 4,
        'title': 'Адмін-панель та мови',
        'body': (
            'BASE: 1 основна мова · PREMIUM: мультимовна + ролі доступу · '
            'PLATINUM: ШІ-адмінка (до 10 мов).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 5,
        'title': 'Термін розробки',
        'body': (
            'BASE: до 25–30 днів · PREMIUM: до 30 днів · PLATINUM: до 30–40 днів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й етап: 50% (Передоплата)',
        'body': (
            'Вноситься перед стартом розробки після затвердження ТЗ, початку '
            'прототипування та дизайн-концепції.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й етап: 50% (Фінальний платіж)',
        'body': (
            'Вноситься після фінального тестування, демонстрації працездатності, перед '
            'деплоєм та передачею всіх доступів.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний злагоджений механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для автоматизації процесів, залучення великих B2B/B2C клієнтів та формування стійкого преміального іміджу вашого бренду в цифровому просторі.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Принципово відмовляємося від конструкторів (WordPress, Tilda).</p>
<ul>
<li><strong>PageSpeed 90+</strong> — блискавичне відкриття сторінок без зайвих скриптів і пріоритетне ранжування в Google.</li>
<li><strong>Enterprise-безпека</strong> — захист від SQL-ін’єкцій, XSS-атак та зламів; AI-асистенти та особисті кабінети без переробки ядра.</li>
<li><strong>3 офіційні пакети</strong> — BASE 900 €, PREMIUM 1 600 €, PLATINUM 3 500 €.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Оберіть оптимальний пакет або зв’яжіться з нашою командою для старту: office@prometeylabs.com.</p>
""".strip()

# Канон гарантії (рішення 16.10): пожиттєва гарантія на код + 1 рік безкоштовної підтримки.
GUARANTEE_HTML = """
<p>Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів чи конструкторів, він не потребує ризикованих оновлень, які ламають верстку.</p>
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
    help = 'Seed turnkey corporate site proposal (3 packages) + classic demo-corp (idempotent)'

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
