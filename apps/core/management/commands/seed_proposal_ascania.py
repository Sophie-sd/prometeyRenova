"""
Management command: seed_proposal_ascania

КП Ascania FMCG (PDF 12.10.2026): корпоративний B2B-сайт дистрибуції.
Демо — стандартний корпоративний сайт (democorp), не магазин.
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

SLUG = 'corporate-ascania-k4m9'
CLIENT = 'Ascania FMCG'
DEMO_TENANT_SLUG = 'ascania-00bbd1'
ISSUED_ON = date(2026, 10, 12)
ORDER = 27

RECS_LEAD = (
    'Корпоративний сайт Ascania FMCG: Django / HTMX, портфель брендів, '
    'B2B-заявки партнерів без перезавантаження, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'B2B-ліди'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Brands', 'caption': 'Food · Non-Food', 'is_accent': False},
    {'order': 1, 'title': 'B2B', 'caption': 'Мережі · HoReCa', 'is_accent': True},
    {'order': 2, 'title': 'Map', 'caption': 'Логістичні хаби', 'is_accent': False},
    {'order': 3, 'title': 'Press', 'caption': 'Новини · кар’єра', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Преміальний UI/UX дизайн бренду',
        'description': (
            'Сучасний індивідуальний інтерфейс міжнародного рівня, адаптований '
            'під партнерів, мережі та HoReCa на смартфонах і ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Інтерактивний портфель брендів',
        'description': (
            'Зручний B2B-каталог напрямків (Food, Non-Food, ВТМ, свіжі продукти), '
            'сортування за категоріями та брендами-партнерами.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумна система лідогенерації B2B',
        'description': (
            'Кастомні форми партнерства (для постачальників, торгових мереж, HoReCa) '
            'з миттєвою передачею в Telegram, CRM або корпоративну пошту.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Корпоративні блоки та географія',
        'description': (
            'Інтерактивна мапа логістичних хабів і розподільчих центрів, сторінка '
            '30-річної історії холдингу, прес-центр, новини та кар’єра.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Легке оновлення каталогів, новин, прес-релізів, вакансій '
            'та звітів без участі програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова та SEO-готовність',
        'description': (
            'Повна аналітична розмітка (GA4, GTM), індексація ключових B2B-запитів '
            'дистрибуції та готовність до контекстної реклами.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'BASE',
        'scope': (
            'Структурований конверсійний дизайн, генерація B2B-контенту (ШІ Medium), '
            'каталог брендів та форми заявок, базова SEO-оптимізація та аналітика, '
            'локалізована адмін-панель, розгортання під ключ на сервері.'
        ),
        'duration': '30 днів',
        'price': Decimal('900.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'PREMIUM',
        'scope': (
            'Індивідуальний UI/UX дизайн з нуля, преміум копірайтинг та ШІ-медіа, '
            'розширене B2B SEO та перелінковка, мультимовна адмінка + ролі доступу, '
            'миттєві ліди в Telegram/Email/CRM, SEO-статті + 10 відгуків Google Maps, '
            'налаштування та запуск 1 реклами.'
        ),
        'duration': '30 днів',
        'price': Decimal('2000.00'),
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'PLATINUM',
        'scope': (
            'Ексклюзивний дизайн + інтерактивна анімація, локалізація до 10 мов, '
            'кастомна CRM + вбудований ШІ-помічник, автономний ШІ-адміністратор, '
            'персональний B2B Telegram-бот, 6 міс. контент-маркетингу + 60 відгуків, '
            'до 5 рекламних кампаній (3 міс. ведення).'
        ),
        'duration': '30 днів',
        'price': Decimal('3200.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Чистий кодописний стек',
        'body': (
            'Django / Python, HTML5, HTMX, CSS3, JavaScript. '
            'Без застарілих конструкторів і вразливих CMS.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавичне завантаження портфеля брендів '
            'і високі позиції у видачі Google (Enterprise SEO).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Кіберзахист і масштабування',
        'body': (
            'Захист від SQL-ін’єкцій та XSS-атак. Легка інтеграція B2B-кабінетів, '
            'ERP та API логістики в майбутньому.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Презентація масштабів',
        'body': (
            '6 власних дистрибуційних філій, 18 000+ торгових точок '
            'та міжнародний портфель брендів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Сегментація аудиторії',
        'body': (
            'Окремі швидкі точки входу для національного рітейлу, локальних мереж, '
            'партнерів HoReCa та шукачів роботи.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Безпека та деплой',
        'body': (
            'Перенесення на захищений сервер, міграція домену ascania-fmcg.com '
            'та корпоративних поштових систем.'
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
        'body': 'Після фінального тестування та перевірки.',
    },
]

TITLE = 'Корпоративний сайт Ascania FMCG під ключ'
LEAD = (
    'B2B-інструмент для партнерів, масштабування дистрибуції '
    'та преміального іміджу національного лідера імпорту.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми будуємо надійні B2B-інструменти для автоматизації взаємодії з партнерами, масштабування дистрибуції та формування преміального іміджу Ascania FMCG.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без застарілих конструкторів і вразливих CMS.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — портфель брендів відкривається миттєво.</li>
<li><strong>B2B-заявки</strong> — форми партнерства йдуть у Telegram, CRM або на пошту.</li>
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
