"""
Management command: seed_proposal_agro_logistics

КП «Розробка корпоративного сайту: Сільськогосподарська продукція та логістика
під ключ» (PDF 16.10.2026): корпоративний сайт агротрейдингової та логістичної
компанії. Демо — стандартний корпоративний сайт (democorp), без змін.
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

SLUG = 'corporate-agro-logistics-x7p3'
CLIENT = 'Агропродукція та логістика'
DEMO_TENANT_SLUG = 'agro-logistics-3e9b71'
ISSUED_ON = date(2026, 10, 16)
ORDER = 34

RECS_LEAD = (
    'Технологічний корпоративний веб-ресурс для трейдингової та логістичної '
    'агрокомпанії: щоденні закупівельні ціни, калькулятор логістики, тендерний блок '
    'для фермерів і перевізників, заявки в Telegram/CRM, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'CPT · EXW · FOB'},
    {'order': 3, 'title': '21–30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Культури · ДСТУ/ISO', 'is_accent': False},
    {'order': 1, 'title': 'Prices', 'caption': 'CPT · EXW · FOB', 'is_accent': True},
    {'order': 2, 'title': 'Logistics', 'caption': 'Авто · залізниця', 'is_accent': False},
    {'order': 3, 'title': 'Admin', 'caption': 'Ціни · тарифи · новини', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Професійний галузевий UI/UX дизайн',
        'description': (
            'Сучасний ергономічний інтерфейс в агростилістиці, адаптований під швидку '
            'взаємодію з постачальниками та покупцями на будь-яких пристроях.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог агропродукції та напрямків логістики',
        'description': (
            'Структурований каталог культур (пшениця, кукурудза, соняшник, соя тощо), '
            'якісних показників за ДСТУ/ISO та маршрутів вантажоперевезень.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумна система лідогенерації та розрахунку',
        'description': (
            'Кастомні форми заявки на закупівлю/продаж врожаю та розрахунок вартості '
            'авто/залізничної агрологістики з миттєвою передачею в Telegram/CRM.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Розділи «Про компанію», «Автопарк/Елеватори», «Новини»',
        'description': (
            'Презентація матеріально-технічної бази (зерновози, вагони-хопери, '
            'перевантажувальні хаби), географії роботи та аналітики агроринку.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Легка система управління для щоденного оновлення закупівельних цін, '
            'коригування тарифів перевезень та публікації новин без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та SEO-структура',
        'description': (
            'Повна інтеграція аналітики (GA4, GTM), мікророзмітки та SEO-структури під '
            'оптові та логістичні пошукові запити.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт під ключ',
        'scope': (
            'Преміальний дизайн, чистий код (Django/HTMX), кастомна адмін-панель, '
            'каталог культур і логістики, лід-форми в CRM/Telegram, аналітика, повний '
            'деплой та домен.'
        ),
        'duration': '21–30 днів',
        'price': Decimal('750.00'),
        'price_high': Decimal('800.00'),
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
            'Відмовляємося від шаблонних конструкторів, які гальмують роботу та роблять '
            'компанію вразливою. Створюємо надійний кодописний стек.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавична швидкість завантаження каталогів зернових, олійних культур і '
            'прайс-листів логістики на смартфонах і ПК для лідерства в Google (SEO).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Enterprise-безпека & Масштаб',
        'body': (
            'Надійний захист від кібератак, повна незалежність від вразливих плагінів та '
            'легке підключення кабінетів постачальників чи систем трекінгу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Актуальний прайс-лист закупівель',
        'body': (
            'Інтерактивний блок щоденних цін на зернові на елеваторах і в портах (CPT, '
            'EXW, FOB) з легким оновленням через адмінку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Калькулятор логістики',
        'body': (
            'Форма попереднього прорахунку доставки врожаю (кількість тонн, '
            'відстань/маршрут, тип рухомого складу).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Тендерний блок та партнерство',
        'body': (
            'Окрема точка входу для фермерів та перевізників із можливістю швидкого '
            'завантаження специфікацій.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Налаштування сервера, SSL-сертифікату безпеки, корпоративної пошти та '
            'прив’язка офіційного домену компанії.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%)',
        'body': 'Передоплата перед стартом проєктування та UI/UX.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%)',
        'body': 'Після тестування перед винесенням на робочий домен.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів від 150 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 150 € на місяць. Оплата ділиться '
            'рівними частинами до 5 місяців. Роботи стартують одразу після погодження.'
        ),
    },
]

TITLE = 'Розробка корпоративного сайту: Сільськогосподарська продукція та логістика під ключ'
LEAD = (
    'Технологічний корпоративний веб-ресурс для трейдингової та логістичної '
    'агрокомпанії: трейдери, фермерські господарства та міжнародні партнери.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо надійні цифрові інструменти для автоматизації агробізнесу, залучення трейдерів, фермерських господарств та міжнародних партнерів, формуючи впізнаваний статусний імідж компанії на ринку.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Без шаблонних конструкторів і вразливих плагінів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — каталоги культур і прайс-листи логістики відкриваються блискавично.</li>
<li><strong>Заявки</strong> — закупівля/продаж врожаю та розрахунок логістики миттєво в Telegram/CRM.</li>
</ul>
""".strip()

# Спільний канон сайту: 1 рік (публічна оферта, п. 8.1), не абзац із PDF.
GUARANTEE_HTML = """
<p>Ми впевнені у якості нашого коду. Оскільки сайт пишеться з нуля без використання сторонніх модулів чи плагінів, він не потребує щомісячних оновлень, які часто ламають звичайні сайти на CMS.</p>
<p>Ми надаємо <strong>1 рік гарантійної підтримки</strong> з моменту повної оплати та передачі доступів: технічні баги, допущені з нашої вини, виправляємо безкоштовно (публічна оферта, п. 8.1).</p>
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
