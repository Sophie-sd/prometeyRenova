"""
Management command: seed_proposal_ecom

Idempotent заливка КП «Інтернет-магазин під ключ» (PDF 23.09.2026)
+ класичний demo-shop. Це не версія сайту клієнта.
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

SLUG = 'shop-ecom-a7f3'

RECS_LEAD = (
    'Інженерні рішення для інтернет-магазину під ключ — '
    'Django / HTMX / CSS / JS, без конструкторів і без платних плагінів.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Нова Пошта'},
    {'order': 3, 'title': 'До 30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Admin', 'caption': 'Ціни · залишки', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Фільтри · пошук', 'is_accent': False},
    {'order': 2, 'title': 'Cart', 'caption': '1–2 кроки', 'is_accent': True},
    {'order': 3, 'title': 'Delivery', 'caption': 'НП · Укрпошта', 'is_accent': False},
    {'order': 4, 'title': 'Pay', 'caption': 'LiqPay · Mono', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Індивідуальний UI/UX',
        'description': (
            'Адаптивний інтерфейс для телефона, планшета і ПК. '
            'Фокус на простому шляху до покупки.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог і картка товару',
        'description': (
            'Багаторівневі фільтри, моментальний пошук, опції, фотогалерея '
            'і складські модифікації.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Кошик і доставка',
        'description': (
            'Чекаут за 1–2 кроки. Нова Пошта й Укрпошта з розрахунком ціни доставки.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Оплата на сайті',
        'description': 'Картка через LiqPay, WayForPay або Monobank.',
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Адмін-панель',
        'description': (
            'Асортимент, залишки, ціни і замовлення без звернення до розробника.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'SEO і аналітика',
        'description': (
            'Мікророзмітка, Meta Pixel, Google Analytics 4, конверсії і sitemap.'
        ),
    },
    {
        'number': 7,
        'order': 6,
        'title': 'Деплой і домен',
        'description': (
            'Сервер, SSL, прив’язка домену і перевірка, що сайт тримає навантаження.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Базовий',
        'scope': (
            'Індивідуальний дизайн, бекенд на Django, каталог і кошик, '
            'онлайн-оплата, доставка, адмінка, базовий SEO і аналітика, деплой.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('100.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Преміум',
        'scope': (
            'Усе з Базового плюс рекламні кампанії Google Ads і Meta Ads, '
            'глибша GA4 і події, сповіщення в Telegram, лід-магніти '
            'і пріоритетна технічна підтримка.'
        ),
        'duration': '30–40 днів',
        'price': Decimal('1500.00'),
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'Платінум',
        'scope': (
            'Усе з Преміум плюс CRM, особистий кабінет покупця з бонусами, '
            'AI-чат, омніканальний запуск, навантажувальне тестування '
            'і 3 місяці супроводу.'
        ),
        'duration': '45–60 днів',
        'price': Decimal('4000.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 3,
        'name': 'Перенесення реклами',
        'scope': 'Перенесення діючих рекламних кампаній на новий сайт.',
        'duration': '',
        'price': Decimal('100.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Магазин під зростання чека',
        'body': (
            'Каталог, картка, кошик і оплата зібрані так, щоб покупку '
            'було просто повторити. Без конструктора і без абонплати за модулі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Доставка з ціною в чекауті',
        'body': (
            'Нова Пошта й Укрпошта. Вартість доставки рахується на оформленні, '
            'не після дзвінка менеджера.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без шаблонної CMS',
        'body': (
            'Важкий конструктор гальмує картку і вимагає платної підтримки модулів. '
            'Django тримає ціну, залишок і замовлення у своєму коді.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+ до реклами',
        'body': (
            'Повільна вітрина піднімає ціну кліка. 90+ — умова здачі, '
            'не оптимізація після запуску кампаній.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед початком проєктування і технічної реалізації.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': (
            'Після фінального тестування і демонстрації, перед деплоєм '
            'на робочий сервер і передачею доступів.'
        ),
    },
]

TITLE = 'Розробка інтернет-магазину під ключ'
LEAD = (
    'Швидкий онлайн-магазин для зростання середнього чека і повторних покупок: '
    'каталог, кошик, оплата і доставка.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> будує інструмент продажів: конверсія, середній чек і повторні покупки без конструктора.</p>
<p>Стек: <strong>Python / Django · HTMX · HTML5 · CSS3 · JavaScript · PostgreSQL</strong>. Без шаблонних CMS, які гальмують завантаження і вимагають платної підтримки модулів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — швидша сторінка піднімає конверсію і дає перевагу в SEO.</li>
<li><strong>Автономність</strong> — немає абонплати за платні плагіни і рамки готового шаблону.</li>
<li><strong>Піковий трафік</strong> — сайт лишається швидким під час рекламних кампаній.</li>
</ul>
""".strip()

GUARANTEE_HTML = """
<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів, він не потребує постійних ризикованих оновлень, які ламають верстку.</p>
<p>Ми надаємо <strong>пожиттєву гарантію</strong> на працездатність нашого коду протягом усього періоду життя ресурсу.</p>
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
    help = 'Seed generic e-commerce proposal + classic demo-shop (idempotent)'

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
        from apps.demoshop.models import DemoShop
        from apps.demoshop.services.provision import provision_demo_shop

        shop = DemoShop.objects.filter(proposal=proposal).first()
        if shop is None:
            shop = DemoShop(
                proposal=proposal,
                name='Demo Shop',
                slug=DemoShop.generate_slug('ecom'),
            )
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
                'client_name': 'Інтернет-магазин під ключ',
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
                'issued_on': date(2026, 9, 23),
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
                'order': 5,
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
