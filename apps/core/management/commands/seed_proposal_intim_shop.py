"""
Management command: seed_proposal_intim_shop

Idempotent заливка закритого КП «Розробка інтернет-магазину 18+ під ключ»
(PDF 08.10.2026, українською) + стандартний демо-магазин (provision_demo_shop).
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

SLUG = 'shop-intim-p3x7'
DEMO_TENANT_SLUG = 'intim-9d4b1e'
CLIENT_NAME = 'Інтернет-магазин 18+'
ISSUED_ON = date(2026, 10, 8)
ORDER = 29

TITLE = 'Інтернет-магазин товарів 18+ під ключ'
LEAD = (
    'Високошвидкісний, безпечний і конверсійний e-commerce '
    'з акцентом на приватність покупців.'
)
RECS_LEAD = (
    'Інтернет-магазин 18+: Django / HTMX, верифікація віку, анонімна упаковка, '
    'Нова Пошта, онлайн-оплата, PageSpeed 90+.'
)
CTA_LABEL = 'Обговорити проєкт'

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда, де досвідчені розробники та маркетологи працюють як єдиний злагоджений механізм. Ми будуємо готові бізнес-інструменти для продажів, орієнтовані на високий середній чек, бездоганний клієнтський досвід і масштабування.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без шаблонних конструкторів, які гальмують роботу ресурсу.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — швидкі сторінки підвищують конверсію і позиції в Google.</li>
<li><strong>Zero Plugin Lock</strong> — без платних плагінів і щомісячних ліцензій.</li>
<li><strong>Високе навантаження</strong> — стійкість до пікових напливів під час реклами та акцій.</li>
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
    {'order': 2, 'title': '18+ і приватність'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': '18+', 'caption': 'Верифікація віку', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Фільтри · пошук', 'is_accent': True},
    {'order': 2, 'title': 'Cart', 'caption': 'Нова Пошта', 'is_accent': False},
    {'order': 3, 'title': 'Pay', 'caption': 'mono · LiqPay', 'is_accent': False},
    {'order': 4, 'title': 'Telegram', 'caption': 'Сповіщення', 'is_accent': False},
]

MODULES = [
    {'number': 1, 'order': 0, 'title': 'Індивідуальний UI/UX дизайн',
     'description': 'Сучасний інтерфейс, ретельно оптимізований під смартфони (Mobile-First) та ПК.'},
    {'number': 2, 'order': 1, 'title': 'Каталог і картка товару',
     'description': 'Гнучка фільтрація, живий пошук, фотогалереї, характеристики та супутні товари.'},
    {'number': 3, 'order': 2, 'title': 'Розумний кошик та логістика',
     'description': 'Оформлення в 1 екран, інтеграція API «Нова Пошта»: вибір міста, поштомату чи відділення.'},
    {'number': 4, 'order': 3, 'title': 'Безпечні онлайн-платежі',
     'description': 'Банківський еквайринг: Monobank, LiqPay/PrivatBank, Apple Pay / Google Pay.'},
    {'number': 5, 'order': 4, 'title': 'Індивідуальна адмін-панель',
     'description': 'Зручна CMS для керування асортиментом, цінами, залишками та замовленнями без програмістів.'},
    {'number': 6, 'order': 5, 'title': 'Маркетинг, SEO і запуск',
     'description': 'GA4, Meta Pixel, Open Graph, динамічний sitemap.xml, SEO-структура; сервер, SSL, міграція бази і домен.'},
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин під ключ',
        'scope': (
            'Індивідуальний UI/UX дизайн, розробка на Django/HTMX, віковий ценз 18+, '
            'каталог з фільтрами, кошик, API Нової Пошти, онлайн-оплата, адмін-панель, '
            'SEO-база, деплой на сервер і прив’язка домену.'
        ),
        'duration': '30 днів',
        'price': Decimal('800.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {'kind': ProposalSpec.Kind.SPEC, 'order': 0, 'title': 'PageSpeed 90+',
     'body': 'Блискавичне завантаження сторінок максимізує конверсію і дає перевагу в Google SEO.'},
    {'kind': ProposalSpec.Kind.SPEC, 'order': 1, 'title': 'Zero Plugin Lock',
     'body': 'Повна незалежність від платних плагінів, без щомісячних ліцензій і обмежень коробкових CMS.'},
    {'kind': ProposalSpec.Kind.SPEC, 'order': 2, 'title': 'Високе навантаження',
     'body': 'Стійкість до пікових напливів користувачів під час запусків реклами та сезонних акцій.'},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 0, 'title': 'Верифікація віку 18+',
     'body': 'Елегантне модальне вікно підтвердження віку при першому вході, згода зберігається в cookie сесії.'},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 1, 'title': 'Анонімна упаковка',
     'body': 'Чекбокс при оформленні для конфіденційної доставки без дзвінка менеджера.'},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 2, 'title': 'Telegram-сповіщення',
     'body': 'Нові заявки та оплати миттєво надходять у закритий Telegram-чат власника.'},
    {'kind': ProposalSpec.Kind.RECOMMENDATION, 'order': 3, 'title': 'Динамічні варіації',
     'body': 'Зміна кольорів, розмірів і матеріалів у картці без перезавантаження сторінки (HTMX).'},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 0, 'title': '1-й етап: 50% (400 €)',
     'body': 'Перед стартом розробки, проєктуванням інтерфейсу та архітектури бази даних.'},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 1, 'title': '2-й етап: 50% (400 €)',
     'body': 'Після повного тестування, перед деплоєм на сервер і передачею доступів.'},
    {'kind': ProposalSpec.Kind.PAYMENT, 'order': 2, 'title': 'Розстрочка 0%',
     'body': 'Monobank або PrivatBank без комісій: 3 × 267 €, 4 × 200 € або 5 × 160 €.'},
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
    help = 'Seed 18+ shop proposal + standard demo-shop (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без демо-магазину',
        )

    def handle(self, *args, **options):
        from apps.core.management.commands._proposal_seed_guard import seed_must_skip
        if (skip_reason := seed_must_skip(SLUG)):
            self.stdout.write(f'Skip {SLUG}: {skip_reason}')
            return
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
