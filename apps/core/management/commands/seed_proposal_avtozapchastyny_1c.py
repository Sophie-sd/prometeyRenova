"""
Management command: seed_proposal_avtozapchastyny_1c

КП «Розробка інтернет-магазину автозапчастин з переїздом з Prom.ua та інтеграцією з 1С»
(PDF 29.10.2026, заявка kp-avtozapchastyny-1c/2026-10-29-005): магазин під ключ 950 €,
30 днів; інтеграція з 1С окремо 150 € (разом 1 100 €). Оплата 50/50 або розстрочка 0%
(Моно / Приват) до 5 платежів: від 190 €/міс, з 1С — 220 €/міс. Kind — shop.
Демо — стандартний демо-магазин (provision_demo_shop), без змін під клієнта.

Покращення відносно PDF (як у КП 002): гарантія за каноном (пожиттєва на код + 1 рік
підтримки), 301-редиректи лише якщо на Prom був власний домен, без обіцянки
«PageSpeed 90+», «історія Prom» уточнюється на брифі (обсяг переносу узгоджуємо).
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

SLUG = 'shop-avtozapchastyny-1c-w7k2'
CLIENT = 'Магазин автозапчастин'
DEMO_TENANT_SLUG = 'avtozapchastyny-1c-b41d07'
ISSUED_ON = date(2026, 10, 29)
ORDER = 51

TITLE = 'Розробка інтернет-магазину автозапчастин з переїздом з Prom.ua та інтеграцією з 1С'
LEAD = (
    'Власний інтернет-магазин автозапчастин замість Prom.ua: зручний пошук за '
    'артикулом і брендом, сумісність з авто в картці товару, актуальні залишки та '
    'ціни з 1С і незалежність від абонплат маркетплейсу.'
)
RECS_LEAD = (
    'Технічне завдання (переїзд з Prom.ua та 1С): розробка e-commerce сайту '
    'автозапчастин із перенесенням каталогу з Prom.ua і, за потреби, двосторонньою '
    'синхронізацією з 1С.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'Міграція з Prom.ua'},
    {'order': 2, 'title': 'Інтеграція з 1С'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Import', 'caption': 'Prom.ua · товари · категорії · фото', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Категорії · бренди · артикули', 'is_accent': False},
    {'order': 2, 'title': 'Search', 'caption': 'Назва · категорія · артикул · HTMX', 'is_accent': True},
    {'order': 3, 'title': '1C Sync', 'caption': 'Залишки · ціни · замовлення', 'is_accent': False},
    {'order': 4, 'title': 'Checkout', 'caption': 'Нова Пошта · онлайн-оплата', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Індивідуальний UI/UX дизайн (автомобільний стиль)',
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
            'Категорії запчастин із фільтрами за брендом, артикулом / OEM-кодом і '
            'характеристиками; сумісність з авто в картці товару.'
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
        'name': 'Інтернет-магазин під ключ + переїзд з Prom.ua',
        'scope': (
            'Дизайн, чистий код (Django/HTMX), індивідуальна адмін-панель, перенесення '
            'товарів, категорій і фото з Prom.ua, онлайн-оплати, доставка, аналітика, '
            'деплой та підключення домену.'
        ),
        'duration': '30 днів',
        'price': Decimal('950.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Магазин + переїзд з Prom.ua + інтеграція з 1С',
        'scope': (
            'Усе з базового пакета плюс інтеграція з 1С (+150 €): синхронізація залишків, '
            'роздрібних і оптових цін та вивантаження замовлень у 1С. Обсяг і версію 1С '
            'підтверджуємо на брифі.'
        ),
        'duration': '30 днів',
        'price': Decimal('1100.00'),
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
            'Відмовляємося від шаблонних конструкторів, які гальмують роботу. Розробляємо '
            'високонавантажені сайти на сучасному та надійному стеку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Швидкість на смартфонах',
        'body': (
            'Легкі сторінки без зайвих плагінів: каталог із тисячами запчастин швидко '
            'відкривається зі смартфона, що допомагає конверсії та SEO.'
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
        'title': 'Перенесення каталогу з Prom.ua',
        'body': (
            'Експорт асортименту з вашого магазину на Prom.ua та імпорт на новий сайт: '
            'товари, категорії, фотографії, описи, характеристики та залишки. Чи '
            'переносимо відгуки, клієнтів та історію замовлень — узгоджуємо на брифі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Збереження пошукової ваги (SEO-перехід)',
        'body': (
            'Мапу 301-редиректів зі старих адрес на нові налаштовуємо, якщо на Prom був '
            'власний домен: так зберігаються позиції та історія індексації в Google. '
            'Адреси на піддомені Prom належать Prom, тому перенаправити їх неможливо.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 4,
        'title': 'Інтеграція з 1С (+150 €)',
        'body': (
            'Синхронізація залишків, роздрібних і оптових цін з 1С та вивантаження '
            'замовлень із сайту в 1С. Версію 1С і хто її обслуговує уточнюємо до старту.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Живий пошук (HTMX)',
        'body': (
            'Швидкий пошук продукції за назвою, категорією або артикулом / OEM-кодом з '
            'миттєвими підказками без перезавантаження сторінки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Безпечне налаштування сервера, SSL-сертифіката, підключення робочого домену '
            'та фінальна перевірка прийому замовлень.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%) — 475 € (з 1С — 550 €)',
        'body': 'Передплата перед початком розробки.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%) — 475 € (з 1С — 550 €)',
        'body': 'Після фінального тестування, перед деплоєм та передачею всіх доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів від 190 €/міс. (з 1С — 220 €/міс.)',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 190 € на місяць (з 1С — 220 €). Сума ділиться '
            'рівними частинами до 5 місяців без переплат і відсотків. Старт розробки '
            'одразу після погодження.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми будуємо готові інструменти для продажів: власний магазин автозапчастин замість Prom.ua, без абонплат маркетплейсу, з даними з вашої 1С.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Чистий код для e-commerce замість шаблонних конструкторів.</p>
<ul>
<li><strong>Переїзд з Prom.ua</strong> — переносимо товари, категорії та фото (а також описи, характеристики й залишки); 301-редиректи — якщо на Prom був власний домен.</li>
<li><strong>Інтеграція з 1С</strong> (+150 €) — синхронізація залишків, роздрібних і оптових цін, вивантаження замовлень.</li>
<li><strong>Каталог і пошук</strong> — пошук за назвою, артикулом / OEM-кодом і брендом; сумісність з авто в картці товару.</li>
<li><strong>Замовлення</strong> — Нова Пошта (відділення, поштомати, кур’єр), онлайн-оплата карткою / Apple Pay / Google Pay.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 5 платежів). Зв’яжіться з нашою командою для узгодження каталогу та старту розробки: office@prometeylabs.com.</p>
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
        'Seed auto parts e-shop + Prom.ua + 1C proposal (950 € / 1100 €) '
        '+ standard demo-shop (idempotent)'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_shop',
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
