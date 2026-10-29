"""
Management command: seed_proposal_3ds

КП Студія дизайну 3DS (3ds.dp.ua, PDF 13.10.2026): корпоративний сайт з каталогом
та портфоліо проєктів. Демо — стандартний корпоративний сайт (democorp), без змін.
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

SLUG = 'corporate-3ds-d5t9'
CLIENT = 'Студія дизайну 3DS'
DEMO_TENANT_SLUG = '3ds-9b4e1c'
ISSUED_ON = date(2026, 10, 13)
ORDER = 30

RECS_LEAD = (
    'Корпоративний сайт Студії дизайну 3DS: Django / HTMX, каталог і портфоліо '
    'проєктів із галереями до/після та 3D-турами, заявки в Telegram без перезавантаження, '
    'PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Портфоліо'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Portfolio', 'caption': 'Квартири · будинки', 'is_accent': False},
    {'order': 1, 'title': '3D', 'caption': 'Тури · до/після', 'is_accent': True},
    {'order': 2, 'title': 'Services', 'caption': 'Послуги · ціни', 'is_accent': False},
    {'order': 3, 'title': 'Blog', 'caption': 'Тренди · SEO', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Професійний UI/UX дизайн',
        'description': (
            'Елегантний мінімалістичний інтерфейс преміум-сегмента, оптимізований '
            'під комфортний перегляд рендерів на смартфонах і Retina-дисплеях.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Інтерактивний каталог та портфоліо проєктів',
        'description': (
            'Категоризація (квартири, будинки, офіси, HoReCa, фасади), інтеграція '
            'галерей до/після, планів креслень та блоків 3D-турів.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумна система лідогенерації',
        'description': (
            'Кастомні форми розрахунку вартості проєкту: заявки миттєво, без '
            'перезавантаження сторінки, надходять у Telegram, CRM або на пошту.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Сторінки «Послуги та ціни», «Про студію», «Блог»',
        'description': (
            'Структуровані пакети проєктування (ескізний проєкт, креслення, '
            'авторський нагляд), статті про тренди дизайну для органічного SEO.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Індивідуальна кастомна адмін-панель',
        'description': (
            'Легка панель управління для самостійної публікації нових об’єктів, '
            'рендерів, оновлення прайсів та відгуків без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та аналітика',
        'description': (
            'Інтеграція пікселів соцмереж, налаштування Google Analytics 4 (GA4), '
            'GTM та первинна SEO-оптимізована структура сторінок.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт під ключ',
        'scope': (
            'Преміальний дизайн, чистий код (Django/HTMX), кастомна адмін-панель, '
            'SEO-структура, інтеграція заявок у Telegram/Email, аналітика, '
            'повний деплой та підключення домену 3ds.dp.ua.'
        ),
        'duration': '30 днів',
        'price': Decimal('850.00'),
        'price_high': Decimal('900.00'),
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
            'Відмовляємося від застарілих конструкторів та повільних CMS. '
            'Високонавантажений сайт на сучасному та безпечному стеку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Миттєве відкриття важких рендерів, 3D-візуалізацій та панорам '
            'піднімає конверсію та дає перевагу в SEO.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Безпека Enterprise-рівня',
        'body': (
            'Надійний захист від вразливостей, незалежність від сторонніх '
            'платних модулів та легка інтеграція нових інструментів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Фокус на візуалі',
        'body': (
            'Повнорозмірні якісні галереї інтер’єрів замість застарілої верстки, '
            'з підтримкою вбудовування інтерактивних 3D-турів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Презентація етапів',
        'body': (
            'Наочний процес «Концепція → Деталізація (BIM-креслення) → '
            'Авторський нагляд / Супровід» із прозорим прайсом.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Мобільна оптимізація та запуск',
        'body': (
            'Бездоганний відгук на смартфонах (PageSpeed 90+), SSL і перенесення '
            'робочого домену 3ds.dp.ua без простоїв.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед стартом: прототипування інтерфейсу, UI/UX концепція та архітектура бази даних.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після фінального тестування форм та адмінки, перед публікацією на домені.',
    },
]

TITLE = 'Корпоративний сайт з каталогом для Студії дизайну 3DS під ключ'
LEAD = (
    'Швидкісний цифровий шоурум для студії дизайну інтер’єру та архітектури: '
    'преміальні замовники, естетика візуалізацій, масштабування бренду.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми створюємо швидкісний цифровий шоурум для студії дизайну інтер’єру та архітектури 3DS (3ds.dp.ua), орієнтований на залучення преміальних замовників, високу естетику демонстрації візуалізацій та масштабування бренду.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без шаблонних конструкторів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — рендери, 3D-тури та панорами відкриваються миттєво.</li>
<li><strong>Заявка</strong> — форма розрахунку вартості йде в Telegram, CRM або на пошту без перезавантаження.</li>
</ul>
""".strip()

# Спільний канон сайту: 1 рік (публічна оферта, п. 8.1), не абзац із PDF.
GUARANTEE_HTML = """
<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів, він не потребує постійних ризикованих оновлень, які ламають верстку.</p>
<p>Ми надаємо <strong>пожиттєву гарантію на код</strong>: технічні баги, допущені з нашої вини, виправляємо безкоштовно без обмеження строку, а також <strong>1 рік безкоштовної підтримки</strong> з моменту запуску.</p>
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
