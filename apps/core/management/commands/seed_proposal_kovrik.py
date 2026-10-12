"""
Management command: seed_proposal_kovrik

КП Kovrik.ua (PDF 12.10.2026): корпоративний сайт з каталогом автокилимків.
Демо — стандартний корпоративний сайт із каталогом (democorp), не магазин.
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

SLUG = 'corporate-kovrik-r8w2'
CLIENT = 'Kovrik.ua'
DEMO_TENANT_SLUG = 'kovrik-5c7e2a'
ISSUED_ON = date(2026, 10, 12)
ORDER = 28

RECS_LEAD = (
    'Корпоративний сайт Kovrik.ua: Django / HTMX, каталог EVA і ворсових килимків, '
    'заявка в Telegram без перезавантаження, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Каталог'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Марка · модель', 'is_accent': False},
    {'order': 1, 'title': 'EVA', 'caption': 'Колір · кант', 'is_accent': True},
    {'order': 2, 'title': 'B2B', 'caption': 'Опт · дроп', 'is_accent': False},
    {'order': 3, 'title': 'Brand', 'caption': 'Виробництво', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Професійний UI/UX дизайн',
        'description': (
            'Сучасний ергономічний інтерфейс, адаптований під демонстрацію '
            'виробів на будь-яких мобільних пристроях і ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог продукції та зразків',
        'description': (
            'Структурований каталог автокилимків за марками, моделями, типами '
            'матеріалу, окантовки та варіантами комплектації.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумна система лідогенерації',
        'description': (
            'Кастомні форми швидкого замовлення та підбору: заявки без '
            'перезавантаження надходять у Telegram або CRM.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Про бренд, виробництво, відгуки',
        'description': (
            'Презентація матеріалів (EVA, ворс), переваг власного цеху, '
            'сертифікатів та фото готових робіт в авто клієнтів.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна індивідуальна адмін-панель',
        'description': (
            'Швидке додавання моделей, оновлення прайсів, фотографій '
            'та акцій без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова та аналітична готовність',
        'description': (
            'Google Analytics 4, Meta Pixel і правильна мета-розмітка '
            'для швидкої індексації в пошукових системах.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Базовий сайт з каталогом',
        'scope': (
            'Сучасний адаптивний корпоративний дизайн, каталог моделей килимків '
            'та фотогалерея, форми швидкої заявки в Telegram/Email, кастомна '
            'панель адміністрування, базова SEO-оптимізація та аналітика, '
            'повний деплой і запуск на хостингу замовника.'
        ),
        'duration': '30 днів',
        'price': Decimal('450.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Сайт з люксовим дизайном Figma',
        'scope': (
            'Ексклюзивний авторський UI/UX дизайн у Figma з нуля, індивідуальне '
            'опрацювання текстур, деталей та палітри, інтерактивні елементи і '
            'плавна анімація, розширена структура каталогу та посадкові блоки, '
            'пріоритетна підтримка й оптимізація швидкості, запуск під ключ '
            'із налаштуванням домену kovrik.ua.'
        ),
        'duration': '30 днів',
        'price': Decimal('600.00'),
        'currency': '€',
        'is_recommended': True,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Django / HTML5 / HTMX / JS',
        'body': (
            'Без шаблонних конструкторів, які гальмують роботу. '
            'Швидкісний кодописний сайт на сучасному стеку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавичне відкриття сторінок і каталогів продукції '
            'покращує поведінкові фактори та SEO.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Безпека та масштабованість',
        'body': (
            'Захист без сторонніх вразливих CMS-плагінів. '
            'Можливість масштабування в повноцінний маркетплейс.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Каталог матеріалів та кольорів',
        'body': (
            'Візуальний вибір ромбоподібних і стільникових EVA-структур, '
            'кольору основи та канта.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Швидкий підбір під авто',
        'body': (
            'Фільтр за маркою авто або універсальні варіанти килимків '
            'для дому та офісу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'B2B та роздріб',
        'body': (
            'Окремий блок умов для оптовиків, дропшиперів і автосервісів '
            'із формою завантаження оптового прайсу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед стартом: проєктування, прототип і дизайн.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після фінального тестування, перед деплоєм.',
    },
]

TITLE = 'Корпоративний сайт з каталогом для Kovrik.ua під ключ'
LEAD = (
    'Презентація EVA, ворсових і гумових килимків, '
    'залучення гуртових і роздрібних клієнтів.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми будуємо інструменти для презентації продукції (EVA-килимки, ворсові та гумові вироби), залучення гуртових і роздрібних клієнтів та статусного іміджу бренду Kovrik.ua.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без шаблонних конструкторів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — каталог відкривається миттєво.</li>
<li><strong>Заявка</strong> — форма підбору йде в Telegram або CRM без перезавантаження.</li>
</ul>
""".strip()

# Спільний канон сайту: 1 рік (публічна оферта, п. 8.1), не абзац із PDF.
GUARANTEE_HTML = """
<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів, він не потребує постійних ризикованих оновлень, які ламають верстку.</p>
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
