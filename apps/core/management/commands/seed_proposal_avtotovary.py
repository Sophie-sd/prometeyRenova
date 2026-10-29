"""
Management command: seed_proposal_avtotovary

КП «Розробка сучасного інтернет-магазину автотоварів під ключ» (PDF 27.10.2026,
українською): інтернет-магазин автотоварів та автохімії під ключ, 800 €, 30 днів.
Оплата 50/50 (400 € + 400 €) або розстрочка 0% (Моно / Приват), до 5 платежів
по 160 €/міс. Kind — shop (предмет договору: інтернет-магазин). Демо — стандартний
демо-магазин (provision_demo_shop), без змін під клієнта.

Відносно PDF: вступ не обіцяє «точний підбір продукції під автомобіль клієнта»
(у модулях немає фільтра за маркою / моделлю / роком) — замість цього сумісність
з авто, як у картці товару з PDF. Гарантія — канон, не абзац із PDF.
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

SLUG = 'shop-avtotovary-ejja'
CLIENT = 'Магазин автотоварів'
DEMO_TENANT_SLUG = 'avtotovary-551096'
ISSUED_ON = date(2026, 10, 27)
ORDER = 46

TITLE = 'Розробка сучасного інтернет-магазину автотоварів під ключ'
LEAD = (
    'Готовий інструмент для продажів у сфері автотоварів та автохімії, орієнтований '
    'на високий середній чек, зручний вибір продукції (в’язкість, допуски, бренди, '
    'сумісність з авто в картці товару) та масштабування вашого бізнесу.'
)
RECS_LEAD = (
    'Технічне завдання (індивідуальні деталі проєкту автотоварів): розробка сучасного '
    'e-commerce порталу для роздрібного продажу автомобільних товарів, деталей та '
    'розхідних матеріалів.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Каталог · фільтри · Нова Пошта'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Категорії · в’язкість · допуски', 'is_accent': False},
    {'order': 1, 'title': 'Search', 'caption': 'Назва · бренд · артикул · HTMX', 'is_accent': True},
    {'order': 2, 'title': 'Card', 'caption': 'Специфікації · сумісність', 'is_accent': False},
    {'order': 3, 'title': 'Checkout', 'caption': 'Нова Пошта · онлайн-оплата', 'is_accent': False},
    {'order': 4, 'title': 'Notify', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Індивідуальний UI/UX дизайн (Auto-стиль)',
        'description': (
            'Сучасний технологічний інтерфейс у динамічній автомобільній естетиці, '
            'адаптований під будь-які смартфони, планшети та ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог товарів та багаторівнева фільтрація',
        'description': (
            'Категоризація (мастила, автохімія, аксесуари, електроніка, світло, '
            'інструменти) з фільтрами за в’язкістю, допусками та брендами.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумний кошик та інтеграція логістики',
        'description': (
            'Миттєве оформлення замовлення, інтеграція з сервісами доставки (Нова Пошта: '
            'відділення, поштомати, кур’єр) та авторозрахунок вартості.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Безпечні онлайн-платежі',
        'description': (
            'Підключення офіційних платіжних шлюзів для зручного прийому оплат картками '
            'Visa/Mastercard, Apple Pay та Google Pay безпосередньо на сайті.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Повнофункціональна панель для легкого керування асортиментом, масового '
            'оновлення цін, залишків і характеристик без допомоги програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та SEO-структура',
        'description': (
            'Повна інтеграція аналітики (GA4, GTM, Meta Pixel), товарного фіду для '
            'Google Shopping та оптимізована структура категорій під Google.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин автотоварів під ключ',
        'scope': (
            'Дизайн, чистий код (Django/HTMX), індивідуальна адмін-панель, фільтрація, '
            'онлайн-оплати, інтеграція доставки, аналітика, повний деплой та '
            'підключення домену.'
        ),
        'duration': '30 днів',
        'price': Decimal('800.00'),
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
            'Відмовляємося від шаблонних конструкторів, які гальмують роботу. Розробляємо '
            'високонавантажені сайти на сучасному та надійному стеку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавична швидкість завантаження тисяч автотоварів та запчастин зі '
            'смартфонів, що підвищує конверсію та покращує позиції в SEO.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Стійкість до навантажень',
        'body': (
            'Повна незалежність від сторонніх платних плагінів, надійна робота з великими '
            'каталогами та стійкість під час рекламних кампаній.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Живий пошук та підбір (HTMX)',
        'body': (
            'Швидкий пошук продукції за назвою, брендом або артикулом/кодом товару з '
            'випадаючими підказками без перезавантаження сторінки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Інформативна картка товару',
        'body': (
            'Специфікації (об’єм каністри, сумісність з авто, таблиця допусків '
            'виробників), наявність на складі, відгуки покупців та супутні товари.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Миттєва обробка замовлень',
        'body': (
            'Автоматичне сповіщення про нові покупки в Telegram менеджеру магазину або '
            'передача у CRM-систему для швидкої відправки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Повне налаштування сервера, SSL-сертифікату безпеки, міграція даних та '
            'підключення вашого домену для стабільної роботи ресурсу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%) — 400 €',
        'body': 'Передплата перед початком розробки.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%) — 400 €',
        'body': 'Після фінального тестування, перед деплоєм та передачею всіх доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів по 160 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 160 € на місяць. Сума ділиться '
            'рівними частинами до 5 місяців без переплат і відсотків. Старт розробки '
            'одразу після погодження.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для продажів у сфері автотоварів та автохімії, орієнтовані на високий середній чек, зручний вибір продукції та масштабування вашого бізнесу.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Переваги чистого коду для e-commerce замість шаблонних конструкторів.</p>
<ul>
<li><strong>Каталог і фільтри</strong> — мастила, автохімія, аксесуари, електроніка, світло, інструменти; фільтри за в’язкістю, допусками та брендами.</li>
<li><strong>Картка товару</strong> — специфікації, сумісність з авто, таблиця допусків виробників, наявність і супутні товари.</li>
<li><strong>Замовлення</strong> — Нова Пошта, онлайн-оплата карткою / Apple Pay / Google Pay, сповіщення в Telegram або CRM.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 5 платежів). Зв’яжіться з нашою командою для узгодження каталогу автотоварів та старту розробки: office@prometeylabs.com.</p>
""".strip()

# Канон гарантії (рішення 16.10): пожиттєва гарантія на код + 1 рік безкоштовної підтримки.
GUARANTEE_HTML = """
<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів, він не потребує постійних ризикованих оновлень, які ламають верстку.</p>
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
    help = (
        'Seed auto goods e-shop proposal (800 €) '
        '+ standard demo-shop (idempotent)'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_shop',
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
        """Стандартний демо-магазин (як у всіх КП) через provision_demo_shop(), без змін під клієнта."""
        from apps.demoshop.models import DemoShop
        from apps.demoshop.services.provision import provision_demo_shop

        shop = DemoShop.objects.filter(proposal=proposal).first()
        if shop is None:
            shop = DemoShop(proposal=proposal, name='Demo Shop', slug=DEMO_TENANT_SLUG)
            shop.save()
        shop = provision_demo_shop(proposal)
        if shop.name != 'Demo Shop':
            shop.name = 'Demo Shop'
            shop.save(update_fields=['name'])
        self.stdout.write(self.style.SUCCESS(
            f'Demo: {shop.get_absolute_url()} (slug={shop.slug})'
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
                'kind': Proposal.DemoKind.SHOP,
                'corp_catalog': False,
                'is_published': True,
                'order': ORDER,
            },
        )
        # Дочірні рядки лише ЦІЄЇ КП перезаписуються (ідемпотентний seed, як у всіх seed_proposal_*).
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
