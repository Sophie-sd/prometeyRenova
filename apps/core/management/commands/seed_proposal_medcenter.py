"""
Management command: seed_proposal_medcenter

КП «Розробка корпоративного сайту медичного центру під ключ» (PDF 15.10.2026):
корпоративний сайт медичного центру. Демо — стандартний корпоративний сайт
(democorp), без змін.
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

SLUG = 'corporate-medcenter-k1k6'
CLIENT = 'Медичний центр'
DEMO_TENANT_SLUG = 'medcenter-a9c4de'
ISSUED_ON = date(2026, 10, 15)
ORDER = 33

RECS_LEAD = (
    'Корпоративний сайт медичного центру: Django / HTMX, каталог послуг і цін, '
    'профілі лікарів з онлайн-записом, заявки в Telegram/CRM/Email, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Онлайн-запис'},
    {'order': 3, 'title': '25 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Services', 'caption': 'Напрямки · ціни', 'is_accent': False},
    {'order': 1, 'title': 'Doctors', 'caption': 'Профілі · запис', 'is_accent': True},
    {'order': 2, 'title': 'Prices', 'caption': 'Прайс · чек-апи', 'is_accent': False},
    {'order': 3, 'title': 'Admin', 'caption': 'Графіки · статті', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Професійний медичний UI/UX дизайн',
        'description': (
            'Сучасний, чистий інтерфейс у довірчій медичній естетиці, адаптований '
            'під швидкий пошук інформації на смартфонах і ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог послуг, напрямків та цін',
        'description': (
            'Структурований перелік напрямків лікування, діагностики, аналізів із '
            'детальними описами, підготовкою до прийому та прозорим прайсом.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Картки фахівців та онлайн-запис',
        'description': (
            'Профілі лікарів (стаж, спеціалізація, відгуки, сертифікати) та розумна '
            'форма онлайн-запису до лікаря в один клік без перезавантаження.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Миттєві сповіщення адміністраторам',
        'description': (
            'Заявки пацієнтів миттєво дублюються в Telegram, медичну CRM-систему або '
            'на пошту реєстратури для максимальної швидкості реакції.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Легка панель керування для самостійної зміни графіків прийому, додавання '
            'нових лікарів, оновлення прайсів та публікації статей без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та локальне SEO',
        'description': (
            'Інтеграція GA4, Meta Pixel, правильна семантична розмітка під медичні '
            'пошукові запити пацієнтів у вашому регіоні.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Медичний корпоративний сайт під ключ',
        'scope': (
            'Преміальний дизайн, чистий код (Django/HTMX), кастомна адмін-панель, '
            'каталог послуг, профілі лікарів, онлайн-запис, аналітика, деплой та домен.'
        ),
        'duration': '25 днів',
        'price': Decimal('900.00'),
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
            'Відмовляємося від вразливих шаблонів і конструкторів. Створюємо чистий '
            'кодописний стек для стабільної та довговічної роботи медичного порталу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавичне відкриття сторінок послуг і профілів лікарів зі смартфонів, '
            'що підвищує конверсію записів на прийом та покращує позиції в Google (SEO).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Захист даних пацієнтів',
        'body': (
            'Enterprise-рівень безпеки, захист від витоку персональної інформації та '
            'повна незалежність від сторонніх платних модулів чи плагінів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Презентація відділень',
        'body': (
            'Зручний рубрикатор (терапія, хірургія, педіатрія, стоматологія, УЗД, '
            'лабораторна діагностика тощо).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Команда спеціалістів',
        'body': (
            'Персональні картки лікарів з фото, освітою, практичним досвідом та кнопкою '
            'швидкого запису саме до обраного лікаря.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Прозорий прайс-лист',
        'body': (
            'Інтерактивний пошук медичних послуг і комплексних чек-апів за категоріями '
            'без зайвих завантажень.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Безпечне розгортання на надійному сервері, підключення захищеного '
            'SSL-сертифікату та прив’язка офіційного домену.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%): 450 €',
        'body': 'Передплата для старту робіт.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%): 450 €',
        'body': 'Після повного тестування сайту перед запуском.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 5 × 180 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 180 € на місяць. Оплата '
            'розбивається до 5 рівних платежів по 180 €/міс. Початок розробки відразу '
            'після оформлення.'
        ),
    },
]

TITLE = 'Розробка корпоративного сайту медичного центру під ключ'
LEAD = (
    'Сучасний корпоративний ресурс для медичної клініки / діагностичного центру '
    'з акцентом на зручність пацієнтів.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо надійні, висококонверсійні цифрові інструменти для медичної сфери, орієнтовані на залучення пацієнтів, підвищення довіри до лікарів та формування бездоганної репутації клініки.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Без вразливих шаблонів, конструкторів і плагінів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — сторінки послуг і профілів лікарів відкриваються блискавично.</li>
<li><strong>Заявки пацієнтів</strong> — миттєво в Telegram, медичну CRM або на пошту реєстратури.</li>
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
