"""
Management command: seed_proposal_cosmetics_shop

Idempotent заливка закритого КП «Інтернет-магазин косметики та догляду під ключ»
(PDF 13.10.2026, українською) + стандартний демо-магазин (provision_demo_shop).
Це не версія сайту клієнта, а стандартне демо.
"""
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

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

SLUG = 'shop-cosmetics-k6v2'
DEMO_TENANT_SLUG = 'cosmetics-4e8a2d'
CLIENT_NAME = 'Інтернет-магазин косметики'
ISSUED_ON = date(2026, 10, 13)
ORDER = 31

TITLE = 'Інтернет-магазин косметики та догляду під ключ'
LEAD = (
    'Естетичний, «живий» і швидкісний б’юті-магазин: зростання конверсії, '
    'високий середній чек і презентація продукції на рівні топових брендів.'
)
RECS_LEAD = (
    'Інтернет-магазин косметики: Django / HTMX, фільтри за типом шкіри та брендом, '
    'INCI-склад, Нова Пошта, Apple Pay / Google Pay, PageSpeed 90+.'
)
CTA_LABEL = 'Обговорити проєкт'

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми створюємо естетичний, «живий» та швидкісний цифровий простір для інтернет-магазину косметики, орієнтований на зростання конверсії, високий середній чек і презентацію б’юті-продукції на рівні топових світових брендів.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без важких конструкторів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — картки товарів, фотогалереї та текстури відкриваються миттєво на смартфонах.</li>
<li><strong>Повна незалежність</strong> — стійкість до сплесків трафіку під час промо-акцій, без платних плагінів.</li>
<li><strong>HTMX</strong> — фільтри та додавання в кошик без перезавантаження сторінки.</li>
</ul>
""".strip()

# Спільний канон сайту: 1 рік (публічна оферта, п. 8.1), не абзац із PDF.
GUARANTEE_HTML = """
<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів, він не потребує постійних ризикованих оновлень, які ламають верстку.</p>
<p>Ми надаємо <strong>пожиттєву гарантію на код</strong>: технічні баги, допущені з нашої вини, виправляємо безкоштовно без обмеження строку, а також <strong>1 рік безкоштовної підтримки</strong> з моменту запуску.</p>
""".strip()

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Б’юті e-commerce'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Тип шкіри · бренд', 'is_accent': False},
    {'order': 1, 'title': 'Product', 'caption': 'Об’єм · INCI', 'is_accent': True},
    {'order': 2, 'title': 'Cart', 'caption': 'Нова Пошта', 'is_accent': False},
    {'order': 3, 'title': 'Pay', 'caption': 'Apple · Google Pay', 'is_accent': False},
    {'order': 4, 'title': 'Upsell', 'caption': 'Ритуал догляду', 'is_accent': False},
]

MODULES = [
    {'number': 1, 'order': 0, 'title': 'Трендовий, «живий» UI/UX дизайн',
     'description': 'Сучасний повітряний інтерфейс з акцентом на естетику косметики, мікроанімації та зручність покупки на смартфонах.'},
    {'number': 2, 'order': 1, 'title': 'Каталог та картка косметичного засобу',
     'description': 'Фільтри за типами шкіри/волосся, призначенням, брендами; вибір об’єму (мл), опис INCI-складу, спосіб застосування та фото до/після.'},
    {'number': 3, 'order': 2, 'title': 'Розумний кошик та поштова логістика',
     'description': 'Зручний односторінковий чекаут, індикатор безкоштовної доставки від певної суми та інтеграція відділень Нової Пошти.'},
    {'number': 4, 'order': 3, 'title': 'Безпечні онлайн-платежі',
     'description': 'Офіційний банківський еквайринг (Apple Pay, Google Pay, картки) для миттєвої безшовної оплати.'},
    {'number': 5, 'order': 4, 'title': 'Зручна кастомна адмін-панель',
     'description': 'Швидке додавання новинок, керування залишками, зміна акційних банерів та промокодів самостійно без програмістів.'},
    {'number': 6, 'order': 5, 'title': 'Маркетингова та аналітична готовність',
     'description': 'GA4 E-commerce, Meta Pixel, товарні фіди для Google Shopping та базова SEO-розмітка.'},
]

PACKAGES = [
    {
        'order': 0,
        'name': 'BASE — Базовий стандарт',
        'scope': (
            'Сучасний адаптивний б’юті-дизайн, генерація контенту (ШІ Medium), каталог, '
            'кошик, оплата та доставка, базова SEO-підготовка мета-тегів, локалізована '
            'адмін-панель (1 мова), аналітика, розгортання під ключ на сервері.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('1100.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'PREMIUM — Бізнес масштаб',
        'scope': (
            'Індивідуальний UI/UX концепт з нуля, преміум-контент: ШІ-медіа + копірайтинг, '
            'розширене SEO та внутрішня перелінковка, мультимовна адмінка + ролі доступу, '
            'сповіщення замовлень у Telegram/Email, SEO-статті + 10 відгуків Google Maps, '
            'налаштування та запуск 1 реклами.'
        ),
        'duration': '30 днів',
        'price': Decimal('2500.00'),
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'PLATINUM — Абсолютне домінування',
        'scope': (
            'Ексклюзивний дизайн + інтерактивна анімація, мультимовність: локалізація до 10 мов, '
            'кастомна CRM + вбудований ШІ-асистент, автономний ШІ-адміністратор магазину, '
            'персональний клієнтський Telegram-бот, 6 міс. контент-маркетингу + 60 відгуків, '
            'до 5 рекламних кампаній (3 міс. ведення).'
        ),
        'duration': '30–40 днів',
        'price': Decimal('4300.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {'kind': ProposalSpec.Kind.SPEC, 'order': 0, 'title': 'Django / HTML5 / HTMX / JS',
     'body': 'Відмовляємося від важких конструкторів. Швидкі кодописні сайти на сучасному та надійному стеку.'},
    {'kind': ProposalSpec.Kind.SPEC, 'order': 1, 'title': 'Google PageSpeed 90+',
     'body': 'Блискавичне відкриття карток товарів, фотогалерей та текстур кремів на смартфонах. Прямий ріст SEO-ранжування.'},
    {'kind': ProposalSpec.Kind.SPEC, 'order': 2, 'title': 'Повна незалежність',
     'body': 'Стійкість до сплесків трафіку під час промо-акцій, без платних плагінів, високий захист персональних даних.'},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 0, 'title': 'Сучасний visual & динаміка',
     'body': 'Інтерактивні банери, бейджі «Хіт», «New», «Eco-Friendly» та відео-огляди.'},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 1, 'title': 'Інструменти допродажів',
     'body': 'Блоки «З цим товаром купують» і «Повний ритуал догляду» для збільшення середнього чека.'},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 2, 'title': 'Швидкість відгуку',
     'body': 'Моментальне застосування фільтрів і додавання в кошик без перезавантаження завдяки HTMX.'},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 3, 'title': 'Деплой та запуск',
     'body': 'Безпечне перенесення бази товарів, збереження URL-структури для SEO, SSL і підключення домену.'},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 0, 'title': '1-й платіж: 50%',
     'body': 'Аванс перед стартом розробки.'},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 1, 'title': '2-й платіж: 50%',
     'body': 'Після фінального тестування та перевірки, перед деплоєм.'},
]


def _langs(payload: dict, text_keys: tuple[str, ...]) -> dict:
    """Усі мовні версії = український текст."""
    out = dict(payload)
    for key in text_keys:
        for lang in ('ru', 'en', 'cs'):
            out[f'{key}_{lang}'] = out.get(key, '')
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
    help = 'Seed cosmetics shop proposal + standard demo-shop (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без демо-магазину',
        )

    def handle(self, *args, **options):
        for model in (
            Proposal, ProposalModule, ProposalPackage,
            ProposalSpec, ProposalHighlight, ProposalArchNode,
        ):
            ensure_leftover_not_null_defaults(model)
        with transaction.atomic():
            proposal, created = self._seed_rows()
        if not options['no_demo']:
            self._provision_demo(proposal)
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action}: /proposal/{proposal.slug}/ '
            f'({proposal.modules.count()} modules, {proposal.packages.count()} packages)'
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
        text = {
            'title': TITLE,
            'lead': LEAD,
            'recommendations_lead': RECS_LEAD,
            'intro_html': INTRO_HTML,
            'guarantee_html': GUARANTEE_HTML,
            'cta_label': CTA_LABEL,
        }
        defaults = {
            'client_name': CLIENT_NAME,
            'issued_on': ISSUED_ON,
            'kind': Proposal.DemoKind.SHOP,
            'corp_catalog': False,
            'is_published': True,
            'order': ORDER,
        }
        for key, value in text.items():
            defaults[key] = value
            for lang in ('ru', 'en', 'cs'):
                defaults[f'{key}_{lang}'] = value
        proposal, created = Proposal.objects.update_or_create(slug=SLUG, defaults=defaults)

        proposal.modules.all().delete()
        for row in MODULES:
            create_with_leftovers(
                ProposalModule, proposal=proposal, **_langs(row, ('title', 'description')),
            )
        proposal.packages.all().delete()
        for row in PACKAGES:
            create_with_leftovers(
                ProposalPackage, proposal=proposal,
                **_langs(row, ('name', 'scope', 'duration')),
            )
        proposal.specs.all().delete()
        for row in SPECS:
            create_with_leftovers(
                ProposalSpec, proposal=proposal, **_langs(row, ('title', 'body')),
            )
        proposal.highlights.all().delete()
        for row in HIGHLIGHTS:
            create_with_leftovers(
                ProposalHighlight, proposal=proposal, **_langs(row, ('title',)),
            )
        proposal.arch_nodes.all().delete()
        for row in ARCH_NODES:
            create_with_leftovers(
                ProposalArchNode, proposal=proposal, **_langs(row, ('title', 'caption')),
            )
        _attach_hero(proposal)
        return proposal, created
