"""
Management command: seed_proposal_glass

Idempotent заливка КП «Фабрика обробки скла» (PDF 22.09.2026)
+ класичний demo-shop (не вітрина Splenko).
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

SLUG = 'shop-glass-a7f3'

RECS_LEAD = (
    'Інженерні рішення для каталогу скла з калькулятором під ключ — '
    'Django / HTMX / CSS / JS, без конструкторів і без платних плагінів.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'Калькулятор вартості'},
    {'order': 2, 'title': 'До 30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Admin', 'caption': 'Django CMS', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Душові · перила', 'is_accent': False},
    {'order': 2, 'title': 'Configurator', 'caption': 'Скло · фурнітура', 'is_accent': True},
    {'order': 3, 'title': 'PDP', 'caption': '8 / 10 / 12 мм', 'is_accent': False},
    {'order': 4, 'title': 'Leads', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX під скляну індустрію',
        'description': (
            'Індивідуальний адаптивний інтерфейс: прозорість, повітря, акцент '
            'на фото встановлених конструкцій — на смартфоні й на ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог категорій і виробів',
        'description': (
            'Окремі розділи: душові кабіни, скляні перила, офісні й міжкімнатні '
            'перегородки, дзеркала, загартоване скло. Без шаблону «всі товари в одну купу».'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Картка виробу зі схемами',
        'description': (
            'Товщина скла 8 / 10 / 12 мм, тип гартування, варіанти фурнітури, '
            'схеми кріплень і галерея високої роздільності — щоб менеджер не '
            'пояснював те саме в Viber.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Параметричний калькулятор вартості',
        'description': (
            'Висота, ширина, тип скла, товщина, фурнітура. Миттєвий орієнтир ціни, '
            'готова специфікація й заявка в Telegram / CRM відділу продажів — '
            'без Excel і без перезавантаження сторінки.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Кастомна панель керування',
        'description': (
            'Нові позиції, ціна за м², характеристики фурнітури й вивантаження '
            'заявок — у Django-адмінці, без програміста на кожну правку.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'SEO-каркас і пікселі під рекламу',
        'description': (
            'ЧПУ, title/description, Schema.org, sitemap.xml, Google Analytics '
            'і рекламні пікселі. Розширене просування — у пакеті Premium і вище.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Base — каталог і розрахунок',
        'scope': (
            'Дизайн, структура БД, каталог трьох ключових категорій '
            '(душові, перила, перегородки), базовий розрахунок вартості за розмірами, '
            'форми заявок, базова SEO-структура, мобільна версія, адмін-панель, '
            'деплой і домен.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('1000.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Premium — конфігуратор',
        'scope': (
            'Усе з пакету Base плюс покроковий конфігуратор конструкцій: '
            'товщина скла, колір фурнітури, тип скла. Автоматична генерація '
            'PDF-кошторису для замовника й сповіщення в Telegram-бот.'
        ),
        'duration': '35–45 днів',
        'price': Decimal('1800.00'),
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'Platinum — дилери й оплата',
        'scope': (
            'Усе з пакету Premium плюс B2B-кабінети дилерів і монтажників, '
            'інтеграція з 1С / CRM / ERP, онлайн-оплата авансу, розширене SEO.'
        ),
        'duration': '50–60 днів',
        'price': Decimal('4200.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Напрямки виробництва в каталозі',
        'body': (
            'Душові: розпашні, розсувні, трапеції, Walk-in. '
            'Перила: точкові, на профілі, стійкові. '
            'Перегородки: loft, цільноскляні, матовані.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Модуль параметричного калькулятора',
        'body': (
            'Габарити (висота, ширина). Тип скла: прозоре, діамант, тоноване, сатин. '
            'Товщина 8–12 мм. Фурнітура: хром, чорний мат, сатин, золото.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Заявка зі специфікацією',
        'body': (
            'Калькулятор рахує орієнтовну ціну, збирає специфікацію й надсилає '
            'заявку в Telegram / CRM без перезавантаження сторінки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 3,
        'title': 'Базова SEO-структура',
        'body': (
            'ЧПУ, мета, Schema.org, sitemap. Рекламні пікселі й аналітика — '
            'у пакеті запуску. Розширене просування — у Premium і Platinum.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 4,
        'title': 'Деплой і домен',
        'body': (
            'Підключення домену, деплой і сервер входять у пакет запуску під ключ. '
            'Конфіденційність гарантована.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й етап: 50% (Передоплата)',
        'body': (
            'Вноситься перед стартом: проєктування архітектури, формули прорахунку '
            'та дизайн-концепція.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й етап: 50% (Фінальний платіж)',
        'body': (
            'Після тестування калькулятора й демонстрації працездатності, '
            'перед деплоєм на бойовий сервер і передачею доступів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без WordPress / OpenCart / Tilda',
        'body': (
            'Конструктор не тягне інженерний калькулятор: плагін ціни ламається '
            'після оновлення ядра, формули витікають у фронт. '
            'Django тримає прайс і логіку на сервері.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Калькулятор як лід, не як Excel',
        'body': (
            'Менеджер не перераховує м² в таблиці після дзвінка. '
            'Клієнт бачить орієнтир на сайті, специфікація падає в Telegram / CRM. '
            'Інакше відділ продажів знову сидить у листуванні.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Фільтри каталогу на HTMX, не SPA',
        'body': (
            'Тип скла й фурнітура змінюються без перезавантаження й без важкого '
            'JS-бандла. Менше скриптів — стабільніший PageSpeed і простіше '
            'ловити спам на сервері.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Формули ціни — у коді й адмінці, не в плагіні',
        'body': (
            'Ціна за м² і націнка фурнітури правляться в панелі. '
            'Розрахунок іде на сервері: клієнт не бачить сирих коефіцієнтів, '
            'конкурент не знімає прайс із HTML.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 4,
        'title': 'PageSpeed 90+ як критерій здачі',
        'body': (
            'Калькулятор має відповідати одразу. Важкий слайдер конструктора '
            'з’їдає клік з реклами, доки людина ще не ввела розміри. '
            '90+ — умова приймання, не «потім оптимізуємо».'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 5,
        'title': 'Код і доступи — ваші в день здачі',
        'body': (
            'Репозиторій, сервер і Django-адмінка переходять фабриці в день здачі. '
            'Немає оренди CMS і щомісячної підписки на нас, щоб калькулятор працював.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда, де розробники й маркетологи працюють як один механізм. Ми не збираємо «сайт з каталогом» на конструкторі. Будуємо платформу, яка показує виріб, рахує орієнтир вартості й віддає заявку відділу продажів.</p>
<p>Відмовляємося від WordPress, OpenCart і Tilda: вони не тримають інженерний калькулятор і формули ціни. Стек проєкту: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>.</p>
<ul>
<li><strong>Швидкість PageSpeed 90+</strong> — сторінка й калькулятор відповідають без затримки навіть при кількох параметрах скла.</li>
<li><strong>Безпека формул</strong> — прайс за м² і націнки фурнітури живуть на сервері, не в плагіні й не в HTML.</li>
<li><strong>Фільтри HTMX</strong> — категорія, товщина, фурнітура змінюються без повного перезавантаження.</li>
<li><strong>Масштаб під B2B</strong> — пізніше можна додати кабінети дилерів, 1С / CRM / ERP і оплату авансу без переписування ядра.</li>
</ul>
""".strip()

GUARANTEE_HTML = """
<p>Система на чистому коді без сторонніх плагінів. Немає щомісячних оновлень ядра CMS, які ламають калькулятор і верстку картки виробу.</p>
<p>Ми надаємо <strong>пожиттєву гарантію</strong> на працездатність нашого коду протягом усього періоду життя ресурсу.</p>
""".strip()

TITLE = 'Комерційна пропозиція на розробку сайту з каталогом і калькулятором'
LEAD = (
    'Корпоративний сайт фабрики обробки скла: каталог конструкцій, '
    'онлайн-конфігуратор і калькулятор вартості під ключ'
)


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
    help = (
        'Seed glass-factory commercial proposal + classic demo-shop (idempotent)'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_shop (для швидких тестів контенту)',
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
            f'{proposal.packages.count()} packages, '
            f'{proposal.specs.count()} specs, '
            f'{proposal.highlights.count()} highlights, '
            f'{proposal.arch_nodes.count()} arch nodes)'
        ))

    def _provision_demo(self, proposal: Proposal) -> None:
        from apps.demoshop.models import DemoShop
        from apps.demoshop.services.provision import provision_demo_shop

        shop = DemoShop.objects.filter(proposal=proposal).first()
        if shop is None:
            shop = DemoShop(
                proposal=proposal,
                name='Demo Shop',
                slug=DemoShop.generate_slug('glass-factory'),
            )
            shop.save()
        else:
            fields = []
            if shop.name != 'Demo Shop':
                shop.name = 'Demo Shop'
                fields.append('name')
            if any(ord(ch) > 127 for ch in shop.slug):
                shop.slug = DemoShop.generate_slug('glass-factory')
                fields.append('slug')
                if shop.owner_user_id:
                    user = shop.owner_user
                    user.username = f'shop-{shop.slug}'[:150]
                    user.save(update_fields=['username'])
                    shop.demo_login = user.username
                    fields.append('demo_login')
            if fields:
                shop.save(update_fields=fields)

        shop = provision_demo_shop(proposal)
        self.stdout.write(self.style.SUCCESS(
            f'Demo: {shop.get_absolute_url()} '
            f'(slug={shop.slug}, login={shop.demo_login})'
        ))

    def _seed_rows(self):
        proposal, created = Proposal.objects.update_or_create(
            slug=SLUG,
            defaults={
                'client_name': 'Фабрика обробки скла',
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
                'issued_on': date(2026, 9, 22),
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
                'kind': Proposal.DemoKind.SHOP,
                'corp_catalog': False,
                'is_published': True,
                'order': 2,
            },
        )

        proposal.modules.all().delete()
        for data in MODULES:
            create_with_leftovers(
                ProposalModule,
                proposal=proposal,
                **_with_ru(data, ('title', 'description')),
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
                ProposalSpec,
                proposal=proposal,
                **_with_ru(data, ('title', 'body')),
            )

        proposal.highlights.all().delete()
        for data in HIGHLIGHTS:
            create_with_leftovers(
                ProposalHighlight,
                proposal=proposal,
                **_with_ru(data, ('title',)),
            )

        proposal.arch_nodes.all().delete()
        for data in ARCH_NODES:
            create_with_leftovers(
                ProposalArchNode,
                proposal=proposal,
                **_with_ru(data, ('title', 'caption')),
            )

        _attach_hero(proposal)
        return proposal, created
