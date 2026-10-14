"""
Management command: seed_proposal_farmlyga

КП Farmlyga (UAB «Farmlyga», farmlyga.lt, PDF 14.10.2026): корпоративний сайт
фармацевтичної компанії з каталогом препаратів. Демо — стандартний корпоративний
сайт (democorp), без змін.
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

SLUG = 'corporate-farmlyga-5k4n'
CLIENT = 'Farmlyga'
DEMO_TENANT_SLUG = 'farmlyga-c66748'
ISSUED_ON = date(2026, 10, 14)
ORDER = 32

RECS_LEAD = (
    'Корпоративний сайт фармацевтичної компанії Farmlyga: Django / HTMX, каталог '
    'препаратів із PDF-інструкціями, фармаконагляд і B2B-заявки в Telegram/CRM, '
    'мультимовність EN / UA / LT, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Каталог препаратів'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Препарати · добавки', 'is_accent': False},
    {'order': 1, 'title': 'Pharma', 'caption': 'Інструкції · сертифікати', 'is_accent': True},
    {'order': 2, 'title': 'Partners', 'caption': 'Аптеки · дистриб’ютори', 'is_accent': False},
    {'order': 3, 'title': 'News', 'caption': 'GMP · блог', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Професійний UI/UX дизайн (рівень bscgrouplab.sk)',
        'description': (
            'Сучасний, чистий фармацевтичний дизайн у стилі світових лабораторій, '
            'ідеально адаптований під ПК, планшети та смартфони.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог фармацевтичної продукції',
        'description': (
            'Структурований каталог лікарських засобів і дієтичних добавок із '
            'фільтрацією за терапевтичними напрямками, інструкціями та сертифікатами.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумна система лідогенерації та Фармаконагляд',
        'description': (
            'Спеціалізовані форми зв’язку для B2B-партнерів та обов’язкова система '
            'фармаконагляду з миттєвим надсиланням у Telegram/CRM/Email.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Сторінки «Про компанію», «Партнерам», «Новини»',
        'description': (
            'Презентація європейських стандартів GMP, наукових досягнень, '
            'представництв (Литва, Україна) та блог для експертного позиціонування.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Індивідуальна адміністративна панель сайту',
        'description': (
            'Зручна та легка кастомна CMS, яка дозволяє самостійно керувати '
            'препаратами, оновлювати інструкції та новини без допомоги програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та SEO-структура',
        'description': (
            'Повна інтеграція аналітики (GA4, GTM), мета-тегів та семантична '
            'розмітка під медичні та фармакологічні запити.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт під ключ',
        'scope': (
            'Преміальний дизайн (рівень bscgrouplab.sk), чистий код Django/HTMX, '
            'кастомна адмін-панель, каталог препаратів, фармаконагляд, SEO-структура, '
            'аналітика, повний деплой та підключення домену.'
        ),
        'duration': '30 днів',
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
            'Відмовляємося від шаблонних конструкторів, які гальмують роботу та '
            'роблять компанію вразливою до кібератак. Створюємо чистий кодописний стек.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавична швидкість завантаження сторінок препаратів, що покращує '
            'поведінкові фактори користувачів та піднімає сайт у топ Google (SEO).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Enterprise-безпека & Масштаб',
        'body': (
            'Надійний захист від SQL-ін’єкцій, XSS-атак та зламів. Повна незалежність '
            'від вразливих плагінів та можливість інтеграції B2B-кабінету.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Преміальна візуальна подача',
        'body': (
            'Перехід від застарілої табличної верстки до сучасного мінімалістичного '
            'стилю BioScience/Pharma з просторою типографікою та акцентом на наукову надійність.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Фармацевтичний каталог',
        'body': (
            'Зручна картка препарату: склад, фармакологічні властивості, показання, '
            'форма випуску, PDF-інструкції для завантаження лікарями та фармацевтами.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Міжнародне позиціонування',
        'body': (
            'Архітектура з підтримкою мультимовності (EN / UA / LT) для взаємодії з '
            'європейськими та українськими контрагентами.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Безпечне налаштування сервера, SSL-сертифікатів, міграція даних та '
            'підключення домену farmlyga.lt без перерви у доступності.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50% аванс): 475 €',
        'body': (
            'Вноситься як передоплата перед початком розробки, проєктування UI/UX '
            'прототипів та структури каталогу препаратів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50% залишок): 475 €',
        'body': (
            'Вноситься після фінального тестування, перевірки працездатності сайту, '
            'перед деплоєм на сервер та передачею всіх доступів.'
        ),
    },
]

TITLE = 'Розробка корпоративного сайту фармацевтичної компанії Farmlyga під ключ'
LEAD = (
    'Редизайн farmlyga.lt на базі референсу bscgrouplab.sk: інструмент для залучення '
    'B2B-партнерів і преміальний імідж європейського фармвиробника.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для автоматизації бізнесу, залучення великих B2B-партнерів (аптечних мереж, дистриб’юторів, клінік) та формування преміального іміджу європейського фармвиробника UAB «Farmlyga» на ринку.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Без шаблонних конструкторів і вразливих плагінів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — сторінки препаратів відкриваються блискавично.</li>
<li><strong>Заявки та фармаконагляд</strong> — миттєво в Telegram, CRM або на Email.</li>
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
