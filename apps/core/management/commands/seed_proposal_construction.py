"""
Management command: seed_proposal_construction

КП «Комерційна пропозиція — Будівельні послуги» (PDF 20.10.2026):
корпоративний сайт з каталогом будівельних послуг під ключ, 650 €, 25 днів;
реклама 300 €; комплекс «Сайт + Реклама» 950 €. Імені клієнта в PDF немає.
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

SLUG = 'corporate-construction-c3cd'
CLIENT = 'Будівельні послуги'
DEMO_TENANT_SLUG = 'construction-16ba1a'
ISSUED_ON = date(2026, 10, 20)
ORDER = 37

RECS_LEAD = (
    'Сучасний корпоративний ресурс будівельної компанії з фокусом на демонстрацію '
    'експертності та залучення прямих замовлень: каталог послуг і портфоліо, '
    'швидкий запит розрахунку, заявки в Telegram/CRM, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Каталог · портфоліо'},
    {'order': 3, 'title': '25 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Послуги · кошториси', 'is_accent': False},
    {'order': 1, 'title': 'Projects', 'caption': 'До · В процесі · Результат', 'is_accent': False},
    {'order': 2, 'title': 'Estimate', 'caption': 'Калькулятор · креслення', 'is_accent': True},
    {'order': 3, 'title': 'Admin', 'caption': 'Портфоліо · ціни за кв.м', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Професійний UI/UX дизайн',
        'description': (
            'Структурований, інтуїтивний інтерфейс, оптимізований під швидке '
            'сприйняття обсягів робіт і прайсів на смартфонах і ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог послуг та реалізованих проєктів',
        'description': (
            'Багаторівнева структура (будівництво котеджів, покрівельні, монолітні, '
            'оздоблювальні роботи, інженерні мережі) з фото та кошторисами.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Інформативна картка послуги та об’єкта',
        'description': (
            'Технічні специфікації, використовувані матеріали, галерея виконаних етапів '
            'та кастомні форми швидкого запиту розрахунку вартості.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Розумна система лідогенерації',
        'description': (
            'Калькулятор попереднього прорахунку кошторису, заявки з якого миттєво та '
            'без перезавантаження надходять у Telegram або CRM.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Легка система управління для самостійного оновлення портфоліо, зміни '
            'розцінок за кв.м та публікації відгуків без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та SEO-підготовка',
        'description': (
            'Ієрархія тегів, підключення пікселів, тегів GA4/GTM та семантична розмітка '
            'під комерційні будівельні запити Google.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт з каталогом',
        'scope': (
            'Архітектура БД, преміум-дизайн, чистий код (Django/HTMX), кастомна CMS, '
            'форми, аналітика, деплой та домен.'
        ),
        'duration': '25 днів',
        'price': Decimal('650.00'),
        'price_high': None,
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Налаштування та запуск реклами',
        'scope': (
            'Створення рекламного кабінету, налаштування тегів і веб-аналітики, аналіз '
            'ніші та пошукових запитів, запуск кампаній.'
        ),
        'duration': '5–7 днів',
        'price': Decimal('300.00'),
        'price_high': None,
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 2,
        'name': 'Комплекс «Сайт + Реклама»',
        'scope': (
            'Повний цикл створення цифрової платформи для будівельного бізнесу з готовим '
            'потоком цільових заявок з пошуку Google.'
        ),
        'duration': '25 днів',
        'price': Decimal('950.00'),
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
            'Відмовляємося від конструкторів. Створюємо кастомну архітектуру чистого '
            'коду, яка витримує великі навантаження без підвисань.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавичне завантаження сторінок та фотогалерей готових об’єктів '
            'будівництва на смартфонах для максимальної конверсії та SEO.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Enterprise-безпека & Масштаб',
        'body': (
            'Кастомне ядро надійно захищає базу клієнтів. Можливість у майбутньому '
            'легко інтегрувати особисті кабінети чи системи обліку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Каталог послуг та портфоліо',
        'body': (
            'Категоризація напрямків, фотозвіти об’єктів у форматі «До / В процесі / '
            'Результат», опис використаних технологій.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Швидкий запит розрахунку',
        'body': (
            'Зручні форми завантаження проєкту/креслення клієнта для оперативного '
            'прорахунку кошторису інженером.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Соціальні докази',
        'body': (
            'Блок ліцензій, сертифікатів допуску до робіт, гарантійні зобов’язання '
            'компанії за договором та відгуки клієнтів.'
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
        'body': 'Передоплата перед стартом проєктування.',
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
        'title': 'Розстрочка 0% (Моно / Приват): 3 × 217 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 217 € на місяць. Сума за розробку '
            'ділиться на 3 рівні платежі по 217 €/міс без відсотків. Старт робіт '
            'відразу після оформлення.'
        ),
    },
]

TITLE = 'Розробка корпоративного сайту з каталогом будівельних послуг під ключ'
LEAD = (
    'Масштабна веб-платформа для лідерів будівельного ринку: презентація об’єктів, '
    'залучення платоспроможних приватних і B2B-замовників та автоматизація обробки '
    'кошторисних запитів.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо масштабні веб-платформи для лідерів будівельного ринку, які допомагають презентувати об’єкти, залучати платоспроможних приватних і B2B-замовників та автоматизувати обробку кошторисних запитів.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Без конструкторів і сторонніх плагінів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — сторінки та фотогалереї готових об’єктів відкриваються блискавично на смартфонах.</li>
<li><strong>Заявки</strong> — калькулятор кошторису та запити розрахунку миттєво в Telegram або CRM.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, 3 платежі). Зв’яжіться з нашою командою для узгодження каталогу робіт та старту розробки: office@prometeylabs.com.</p>
""".strip()

# Канон гарантії (рішення Софії 16.10): пожиттєва гарантія на код + 1 рік безкоштовної підтримки. Не абзац із PDF.
GUARANTEE_HTML = """
<p>Ми впевнені у якості нашого коду. Ми створюємо незалежні системи на чистому коді, що працюють стабільно роками без потреби купувати чи оновлювати сторонні плагіни, які часто ламають звичайні сайти.</p>
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
