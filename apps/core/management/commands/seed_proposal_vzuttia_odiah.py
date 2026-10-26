"""
Management command: seed_proposal_vzuttia_odiah

КП «Розробка інтернет-магазину взуття та одягу під ключ» (PDF 26.10.2026, українською):
інтернет-магазин під ключ 950 € / 30 днів; налаштування та запуск реклами 300 € (паралельно);
комплекс «Магазин + Реклама» 1 250 € / 30 днів.
Оплата 50/50 або розстрочка 0% (Моно / Приват), до 5 платежів
(від 190 €/міс за магазин або 250 €/міс за комплекс).
Демо — стандартний демо-магазин (provision_demo_shop), без змін під клієнта.
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

SLUG = 'internet-mahazyn-vzuttia-odiahu-37pz'
CLIENT = 'Інтернет-магазин взуття та одягу під ключ'
DEMO_TENANT_SLUG = 'vzuttia-odiah-a6e09c'
ISSUED_ON = date(2026, 10, 26)
ORDER = 43

TITLE = 'Розробка інтернет-магазину взуття та одягу під ключ'
LEAD = (
    'Готові інструменти для fashion-продажів, орієнтовані на високий середній чек, '
    'швидкий вибір розмірів та кольорів, повторні покупки та масштабування вашого бренду.'
)
RECS_LEAD = (
    'Технічне завдання: створення сучасного e-commerce простору для роздрібного або '
    'брендового продажу одягу, взуття та аксесуарів.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Розміри · кольори · Нова Пошта'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Розмір · колір · сезон', 'is_accent': False},
    {'order': 1, 'title': 'Product', 'caption': 'Розмірна сітка · фото', 'is_accent': False},
    {'order': 2, 'title': 'Cart', 'caption': 'Нова Пошта · адресна доставка', 'is_accent': False},
    {'order': 3, 'title': 'Payment', 'caption': 'Visa/Mastercard · Apple Pay · Google Pay', 'is_accent': True},
    {'order': 4, 'title': 'Order', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Індивідуальний UI/UX дизайн (Fashion-естетика)',
        'description': (
            'Сучасний візуальний інтерфейс, оптимізований під мобільний шопінг '
            '(Mobile-First), презентацію колекцій та лукбуків.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог та інтерактивна картка товару',
        'description': (
            'Живий пошук, фільтрація за розмірами, кольорами, сезоном, статтю та '
            'матеріалом. Вибір розмірної сітки без перезавантаження.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумний кошик та логістика',
        'description': (
            'Швидке оформлення замовлення (в 1 сторінку), автоматична інтеграція з '
            'Новою Поштою (відділення/поштомати) та адресною доставкою.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Безпечні онлайн-платежі',
        'description': (
            'Підключення офіційного еквайрингу для прийому карт Visa/Mastercard, '
            'Apple Pay та Google Pay безпосередньо на сайті.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Панель управління для простого контролю залишків по розмірах, зміни цін, '
            'створення промокодів і додавання товарів без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та реклама',
        'description': (
            'Інтеграція Meta Pixel, Google Tag Manager, GA4, товарного фіду під '
            'Google Shopping та динамічного ремаркетингу.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин під ключ',
        'scope': (
            'Дизайн, чистий код (Django/HTMX), кастомна адмінка, варіативні розміри, '
            'онлайн-оплати, Нова Пошта, аналітика, деплой.'
        ),
        'duration': '30 днів',
        'price': Decimal('950.00'),
        'price_high': None,
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Налаштування та запуск реклами',
        'scope': (
            'Аудит ніші, підключення рекламних кабінетів, Google Shopping фід, реклама '
            'в Meta (Instagram/Facebook) + ремаркетинг.'
        ),
        'duration': 'Паралельно',
        'price': Decimal('300.00'),
        'price_high': None,
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 2,
        'name': 'Комплекс «Магазин + Реклама»',
        'scope': (
            'Повний запуск бізнесу: технологічний магазин одягу та взуття з готовим '
            'налаштованим потоком продажів з перших днів.'
        ),
        'duration': '30 днів',
        'price': Decimal('1250.00'),
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
            'Відмовляємося від важких конструкторів. Розробляємо оптимізовані '
            'кодописні сайти на сучасному та надійному стеку технологій.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавична швидкість завантаження лукбуків та каталогу зі смартфонів, '
            'що підвищує конверсію в замовлення та покращує SEO.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Стійкість до трафіку',
        'body': (
            'Повна незалежність від плагінів, відсутність збоїв під час сезонних '
            'розпродажів (Black Friday) та рекламних кампаній у соцмережах.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Варіативність товарів (HTMX)',
        'body': (
            'Швидкий вибір кольору та доступного розміру в картці товару з моментальним '
            'оновленням фото та залишків без оновлення сторінки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Таблиця розмірів та гід покупця',
        'body': (
            'Інтерактивне модальне вікно підбору розміру одягу та довжини устілки для '
            'мінімізації відсотка повернень.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Сповіщення про замовлення',
        'body': (
            'Моментальна передача нових замовлень у Telegram менеджеру або в '
            'CRM-систему для швидкої обробки клієнта.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Безпечне розгортання на надійному сервері, підключення SSL-сертифікату '
            'безпеки та прив’язка офіційного домену.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%)',
        'body': 'Передплата перед початком проєктування.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%)',
        'body': 'Після тестування перед передачею всіх доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': (
            'Розстрочка 0% (Моно / Приват): до 5 платежів від 190 €/міс (магазин) '
            'або 250 €/міс (комплекс).'
        ),
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 190 € або 250 € на місяць. Сума '
            'ділиться на 5 рівних платежів (від 190 €/міс за магазин або 250 €/міс за '
            'комплекс). Роботи стартують одразу.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для fashion-продажів, орієнтовані на високий середній чек, швидкий вибір розмірів та кольорів, повторні покупки та масштабування вашого бренду.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Відмовляємося від важких конструкторів.</p>
<ul>
<li><strong>Google PageSpeed 90+</strong> — блискавична швидкість завантаження лукбуків та каталогу зі смартфонів.</li>
<li><strong>Стійкість до трафіку</strong> — повна незалежність від плагінів, відсутність збоїв під час сезонних розпродажів (Black Friday) та рекламних кампаній у соцмережах.</li>
<li><strong>Замовлення</strong> — моментальна передача нових замовлень у Telegram менеджеру або в CRM-систему.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 5 платежів). Зв’яжіться з нашою командою для узгодження каталогу та старту розробки: office@prometeylabs.com.</p>
""".strip()

# Канон гарантії (рішення 16.10): пожиттєва гарантія на код + 1 рік безкоштовної підтримки.
GUARANTEE_HTML = """
<p>Ми впевнені у якості нашого коду. Оскільки сайт пишеться з нуля без використання сторонніх модулів чи вразливих CMS-плагінів, він не потребує щомісячних оновлень, які часто ламають звичайні сайти.</p>
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
        'Seed shoes & clothing e-shop proposal (950 € / ads 300 € / combo 1 250 €) '
        '+ standard demo-shop (idempotent)'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без демо-магазину',
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
        """Стандартний демо-магазин (як у всіх КП) через provision_demo_shop()."""
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
