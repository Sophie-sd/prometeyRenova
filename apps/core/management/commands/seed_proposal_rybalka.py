"""
Management command: seed_proposal_rybalka

КП «Розробка інтернет-магазину товарів для риболовлі під ключ» (PDF 28.10.2026,
заявка kp-rybalka/2026-10-28-008, українською): 950 €, 30 днів. Оплата 50/50
(475 € + 475 €) або розстрочка 0% (Моно / Приват), до 5 платежів по 190 €/міс.
Kind — shop. Демо — стандартний демо-магазин (provision_demo_shop), без змін під клієнта.

Відносно PDF: гарантія — канон (пожиттєва гарантія на код + 1 рік безкоштовної
підтримки); «оптовий продаж» не обіцяємо — оптових цін у функціоналі немає, це опція
для обговорення; «тип риби (хижак / мирна риба)» зведено у фільтри каталогу (у PDF був
лише в пошуку); прямо сказано, хто наповнює каталог і що домен/хостинг оплачує клієнт;
договори еквайрингу й розстрочки клієнт укладає з банком сам; виправлено склеєний текст PDF.
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

SLUG = 'shop-rybalka-rh1k'
CLIENT = 'Магазин товарів для риболовлі'
DEMO_TENANT_SLUG = 'rybalka-8a6235'
ISSUED_ON = date(2026, 10, 28)
ORDER = 48

TITLE = 'Розробка інтернет-магазину товарів для риболовлі під ключ'
LEAD = (
    'Готовий інструмент для продажів снастей і спорядження, орієнтований на високий '
    'середній чек, зручний підбір снастей для любителів і професіоналів риболовлі та '
    'швидке масштабування вашого бізнесу.'
)
RECS_LEAD = (
    'Технічне завдання (індивідуальні деталі проєкту): розробка сучасного e-commerce '
    'сайту для роздрібного продажу рибальських снастей, спорядження та екіпірування.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'Каталог · фільтри · тип риби'},
    {'order': 2, 'title': 'Нова Пошта · онлайн-оплата'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Спінінг · фідер · короп · море · човни · одяг', 'is_accent': False},
    {'order': 1, 'title': 'Filters', 'caption': 'Тест · довжина · лад · плавучість · бренд · тип риби', 'is_accent': False},
    {'order': 2, 'title': 'Search', 'caption': 'Назва · артикул · бренд · HTMX', 'is_accent': True},
    {'order': 3, 'title': 'Card', 'caption': 'Модифікації · ціна · залишки', 'is_accent': False},
    {'order': 4, 'title': 'Checkout', 'caption': 'Нова Пошта · онлайн-оплата · Telegram', 'is_accent': False},
]

MODULES = [
    {
        'number': 1, 'order': 0,
        'title': 'Індивідуальний UI/UX дизайн (Fish & Outdoor)',
        'description': (
            'Сучасний тематичний інтерфейс в аутдор-стилістиці, адаптований під швидкі '
            'покупки зі смартфонів, планшетів і ПК.'
        ),
    },
    {
        'number': 2, 'order': 1,
        'title': 'Каталог та професійна багаторівнева фільтрація',
        'description': (
            'Категорії (спінінг, фідер, коропова й морська риболовля, човни, одяг) з '
            'фільтрами за тестом, довжиною, ладом, плавучістю, брендом і типом риби '
            '(хижак / мирна риба).'
        ),
    },
    {
        'number': 3, 'order': 2,
        'title': 'Розумний кошик та інтеграція логістики',
        'description': (
            'Швидке оформлення замовлення, автоматичний розрахунок вартості доставки, '
            'вибір відділень і поштоматів Нової Пошти та кур’єрської доставки.'
        ),
    },
    {
        'number': 4, 'order': 3,
        'title': 'Безпечні онлайн-платежі',
        'description': (
            'Підключення банківського еквайрингу для прийому карток Visa/Mastercard, '
            'Apple Pay та Google Pay на сайті. Договір еквайрингу ви укладаєте з банком '
            'напряму, ми підключаємо його до сайту.'
        ),
    },
    {
        'number': 5, 'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Повнофункціональна панель для контролю залишків за модифікаціями, швидкого '
            'оновлення цін і додавання акцій без допомоги програмістів.'
        ),
    },
    {
        'number': 6, 'order': 5,
        'title': 'Маркетингова готовність та SEO-структура',
        'description': (
            'Інтеграція аналітики (GA4, GTM, Meta Pixel), товарного фіду для Google '
            'Shopping та структура категорій під пошук Google.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин товарів для риболовлі під ключ',
        'scope': (
            'Дизайн, чистий код (Django/HTMX), кастомна адмін-панель, модифікації '
            'товарів, онлайн-оплати, Нова Пошта, аналітика, деплой і підключення вашого '
            'домену. Наповнення каталогу та оплата домену й хостингу — на стороні клієнта.'
        ),
        'duration': '30 днів',
        'price': Decimal('950.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC, 'order': 0,
        'title': 'Django / HTML5 / HTMX / JS',
        'body': (
            'Відмовляємося від важких конструкторів. Розробляємо оптимізовані сайти на '
            'чистому коді на сучасному та надійному стеку технологій.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC, 'order': 1,
        'title': 'Швидкість на смартфоні',
        'body': (
            'Легкі сторінки без зайвих скриптів: каталог снастей і приманок швидко '
            'відкривається з телефона, що допомагає конверсії та SEO.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC, 'order': 2,
        'title': 'Незалежність від платних модулів',
        'body': (
            'Жодних сторонніх платних плагінів і абонплат за модулі; стабільна робота '
            'з великим каталогом і під час рекламних кампаній.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 0,
        'title': 'Модифікації товару (HTMX)',
        'body': (
            'Швидкий вибір характеристик у картці товару (довжина вудилища, тест, '
            'передаточне число котушки, вага приманки) зі зміною ціни та залишків без '
            'оновлення сторінки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 1,
        'title': 'Живий пошук і підбір',
        'body': (
            'Миттєві підказки за назвою, артикулом або брендом без перезавантаження. '
            'Підбір за типом риби (хижак / мирна риба) — через фільтр каталогу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 2,
        'title': 'Сповіщення в Telegram',
        'body': (
            'Нові замовлення автоматично надходять менеджерам у Telegram для швидкого '
            'резервування товару на складі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 3,
        'title': 'Наповнення каталогу',
        'body': (
            'Ми створюємо структуру категорій, характеристик і фільтрів та показуємо, як '
            'додавати товари. Товари, фото, описи й ціни заводить клієнт через адмін-панель. '
            'Масовий імпорт від постачальників, з 1С або таблиць — окрема опція, обговорюємо '
            'після оцінки ваших файлів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 4,
        'title': 'Оптові продажі — опція для обговорення',
        'body': (
            'Базова версія — роздрібний магазин. Оптові ціни, кабінет оптовика чи мінімальне '
            'замовлення у вартість не входять; якщо продаєте оптом, обговоримо й оцінимо окремо.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 5,
        'title': 'Деплой та запуск',
        'body': (
            'Розгортання на сервері, SSL-сертифікат, підключення вашого домену та запуск '
            'аналітики. Домен і хостинг купує й оплачує клієнт за тарифами провайдера; '
            'ми допомагаємо обрати й усе налаштовуємо.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT, 'order': 0,
        'title': '1-й платіж (50%) — 475 €',
        'body': 'Передплата перед стартом проєктування та UI/UX.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT, 'order': 1,
        'title': '2-й платіж (50%) — 475 €',
        'body': 'Після фінального тестування, перед деплоєм і передачею доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT, 'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів по 190 €/міс.',
        'body': (
            'Оплата частинами від Monobank та ПриватБанк без прихованих комісій — від '
            '190 € на місяць. Сума ділиться рівними частинами до 5 місяців без переплат і '
            'відсотків. Старт розробки одразу після погодження.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для продажів, орієнтовані на високий середній чек, зручний підбір снастей для любителів і професіоналів риболовлі та швидке масштабування вашого бізнесу.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Чистий код замість важких конструкторів.</p>
<ul>
<li><strong>Каталог і фільтри</strong> — спінінг, фідер, коропова й морська риболовля, човни, одяг; фільтри за тестом, довжиною, ладом, плавучістю, брендом і типом риби (хижак / мирна риба).</li>
<li><strong>Картка товару</strong> — модифікації (довжина, тест, передаточне число, вага приманки) зі зміною ціни й залишків без перезавантаження.</li>
<li><strong>Замовлення</strong> — Нова Пошта (відділення, поштомати, кур’єр), онлайн-оплата карткою / Apple Pay / Google Pay, сповіщення менеджерам у Telegram.</li>
<li><strong>Що робить клієнт</strong> — наповнює каталог (товари, фото, описи, ціни) через адмін-панель, оплачує домен і хостинг, укладає з банком договори еквайрингу та розстрочки.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 5 платежів). Зв’яжіться з нашою командою для узгодження каталогу рибальських товарів і старту розробки: office@prometeylabs.com.</p>
""".strip()

# Канон гарантії (рішення 16.10): пожиттєва гарантія на код + 1 рік безкоштовної підтримки.
GUARANTEE_HTML = """
<p>Ми впевнені в якості нашого коду. Сайт пишеться з нуля без сторонніх модулів і вразливих CMS-шаблонів, тому не потребує щомісячних оновлень, які часто ламають звичайні сайти.</p>
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
        'Seed fishing goods e-shop proposal (950 €) '
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
