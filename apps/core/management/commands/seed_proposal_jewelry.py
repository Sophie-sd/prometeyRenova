"""
Management command: seed_proposal_jewelry

Idempotent заливка КП «Ювелірний інтернет-магазин» (PDF 08.10.2026)
+ класичний demo-shop. Це не версія сайту клієнта, а стандартне демо.
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

SLUG = 'shop-jewelry-9d2b'

RECS_LEAD = (
    'Ювелірний магазин на Django / HTMX: чистий код без CMS, PageSpeed 90+ '
    'і стабільність до навантажень у період розпродажів.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Нова Пошта'},
    {'order': 3, 'title': 'Розстрочка 0%'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Проба · метал', 'is_accent': False},
    {'order': 1, 'title': 'Card', 'caption': 'Розмір · камінь', 'is_accent': True},
    {'order': 2, 'title': 'Cart', 'caption': '1 екран · НП', 'is_accent': False},
    {'order': 3, 'title': 'Pay', 'caption': 'Apple / Google Pay', 'is_accent': False},
    {'order': 4, 'title': 'Admin', 'caption': 'Ціни · залишки', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Ексклюзивний UI/UX дизайн під прикраси',
        'description': (
            'Елегантний мінімалістичний інтерфейс преміум-сегмента з фокусом '
            'на фотографії золота, срібла та коштовного каміння.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог та картка виробу',
        'description': (
            'Фільтри за пробою, металом, розміром каблучки, вставкою каменю; '
            'таблиця розмірів, макро-галерея та швидкий живий пошук.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумний кошик та поштова логістика',
        'description': (
            'Зручне оформлення в 1 екран, авторозрахунок вартості доставки, '
            'автоматичний вибір відділень та поштоматів Нової Пошти.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Безпечні онлайн-платежі',
        'description': (
            'Інтеграція безпечного еквайрингу (LiqPay, Monobank, WayForPay) '
            'для прямої оплати банківськими картками та Apple Pay / Google Pay.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Індивідуальна система управління: легке редагування цін, залишків, '
            'фотографій та статусів замовлень без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова та аналітична готовність',
        'description': (
            'Підключення Google Analytics 4 (E-commerce), Meta Pixel, '
            'Google Merchant фідів та базова SEO-оптимізація під пошук.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'BASE',
        'scope': (
            'Базовий стандарт. Базовий структурований UI/UX; ШІ-генерація медіа '
            '& контенту (Medium); каталог, кошик, платіжні системи та доставка; '
            'базова SEO-підготовка мета-тегів; локалізована адмін-панель (1 мова); '
            'розгортання під ключ на сервері. '
            'Оплата: 50% аванс / 50% реліз або розстрочка 0% до 5 платежів '
            '(від 240 €/міс, Моно / Приват).'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('1200.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'PREMIUM',
        'scope': (
            'Бізнес масштаб — оптимальний вибір. Індивідуальний авторський дизайн '
            'з нуля; преміум-контент: ШІ-медіа + копірайтинг; розширене SEO та '
            'внутрішня перелінковка; мультимовна розширена адмін-панель; миттєві '
            'сповіщення замовлень у Telegram/Email; 10 органічних відгуків у Google '
            'Maps; налаштування & запуск рекламного кабінету. '
            'Оплата: 50% аванс / 50% реліз або розстрочка 0% до 8 платежів '
            '(від 312 €/міс, Моно / Приват).'
        ),
        'duration': '30 днів',
        'price': Decimal('2500.00'),
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'PLATINUM',
        'scope': (
            'Абсолютне домінування. Преміальний дизайн + складна інтерактивна '
            'анімація; локалізація та переклад до 10 мов; кастомна CRM із '
            'вбудованим ШІ-асистентом; автономний ШІ-адміністратор магазину; '
            'персональний Telegram-бот для клієнтів; 6 місяців SEO-супроводу та '
            'статей; 60 відгуків Google + 3 міс. ведення реклами. '
            'Оплата: 50% аванс / 50% реліз або розстрочка 0% до 12 платежів '
            '(від 350 €/міс, Моно / Приват).'
        ),
        'duration': '30–45 днів',
        'price': Decimal('4200.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Картка прикраси',
        'body': (
            'Фільтри за пробою, металом, розміром каблучки і вставкою каменю. '
            'Таблиця розмірів і макро-галерея на одній картці.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Оформлення в 1 екран',
        'body': (
            'Авторозрахунок вартості доставки, автоматичний вибір відділень '
            'та поштоматів Нової Пошти.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Оплата без переходів',
        'body': (
            'LiqPay, Monobank, WayForPay: банківські картки, Apple Pay і Google Pay. '
            'GA4 E-commerce, Meta Pixel і Google Merchant фіди.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Чистий код (No-CMS)',
        'body': (
            'Django / Python, HTML5, CSS3, JavaScript та HTMX. '
            'Жодних повільних шаблонів WordPress/OpenCart чи конструкторів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавичне відкриття карток прикрас на смартфонах і ПК. '
            'Максимальний рейтинг для пошукового просування в Google.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Стабільність до навантажень',
        'body': (
            'Повна незалежність від платних вразливих плагінів і стійкість '
            'бази даних до пікового трафіку в період розпродажів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед стартом робіт.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Під час релізу проєкту.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0%',
        'body': (
            'Monobank / ПриватБанк: BASE — до 5 платежів, PREMIUM — до 8, '
            'PLATINUM — до 12. Також оплата на р/р.'
        ),
    },
]

TITLE = 'Розробка інтернет-магазину ювелірних прикрас «під ключ»'
LEAD = (
    'Надійний високоестетичний інструмент для онлайн-продажів ювелірних виробів: '
    'високий середній чек, бездоганна швидкість і масштабування бізнесу.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда, де досвідчені розробники та маркетологи працюють як єдиний злагоджений механізм. Ми будуємо інструмент для онлайн-продажів ювелірних виробів, орієнтований на високий середній чек, швидкість і масштабування.</p>
<p>Стек: <strong>Django (Python) · HTML5 · CSS3 · JavaScript · HTMX</strong>. Без WordPress, OpenCart і конструкторів.</p>
<ul>
<li><strong>Google PageSpeed 90+</strong> — картки прикрас відкриваються блискавично на смартфонах і ПК.</li>
<li><strong>Стабільність до навантажень</strong> — база даних тримає піковий трафік у період розпродажів.</li>
</ul>
<p>Оплата: р/р, Monobank / ПриватБанк (розстрочка 0%). Підтримка й консультація: office@prometeylabs.com.</p>
""".strip()

# Спільний канон сайту: 1 рік (публічна оферта, п. 8.1), не абзац із PDF.
GUARANTEE_HTML = """
<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів, він не потребує постійних ризикованих оновлень, які ламають верстку.</p>
<p>Ми надаємо <strong>1 рік гарантійної підтримки</strong> з моменту повної оплати та передачі доступів: технічні баги, допущені з нашої вини, виправляємо безкоштовно (публічна оферта, п. 8.1).</p>
""".strip()


# Ручний RU для верхнього рівня сторінки (решта — translate_ua_to_ru).
TITLE_RU = 'Разработка интернет-магазина ювелирных украшений «под ключ»'
LEAD_RU = (
    'Надёжный эстетичный инструмент для онлайн-продаж ювелирных изделий: '
    'высокий средний чек, безупречная скорость и масштабирование бизнеса.'
)
RECS_LEAD_RU = (
    'Ювелирный магазин на Django / HTMX: чистый код без CMS, PageSpeed 90+ '
    'и стабильность под нагрузкой в период распродаж.'
)
INTRO_HTML_RU = """
<p><strong>PrometeyLabs</strong> — команда, где опытные разработчики и маркетологи работают как единый слаженный механизм. Мы строим инструмент для онлайн-продаж ювелирных изделий, ориентированный на высокий средний чек, скорость и масштабирование.</p>
<p>Стек: <strong>Django (Python) · HTML5 · CSS3 · JavaScript · HTMX</strong>. Без WordPress, OpenCart и конструкторов.</p>
<ul>
<li><strong>Google PageSpeed 90+</strong> — карточки украшений открываются мгновенно на смартфонах и ПК.</li>
<li><strong>Стабильность под нагрузкой</strong> — база данных выдерживает пиковый трафик в период распродаж.</li>
</ul>
<p>Оплата: р/с, Monobank / ПриватБанк (рассрочка 0%). Поддержка и консультация: office@prometeylabs.com.</p>
""".strip()
GUARANTEE_HTML_RU = """
<p>Мы уверены в качестве нашей инженерной базы. Поскольку сайт создаётся на чистом коде без нестабильных сторонних плагинов, он не требует постоянных рискованных обновлений, которые ломают вёрстку.</p>
<p>Мы предоставляем <strong>1 год гарантийной поддержки</strong> с момента полной оплаты и передачи доступов: технические баги, допущенные по нашей вине, исправляем бесплатно (публичная оферта, п. 8.1).</p>
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
    help = 'Seed jewelry shop proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('jewelry'),
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
                'client_name': 'Ювелірний інтернет-магазин',
                'title': TITLE,
                'title_ru': TITLE_RU,
                'title_en': '',
                'title_cs': '',
                'lead': LEAD,
                'lead_ru': LEAD_RU,
                'lead_en': '',
                'lead_cs': '',
                'recommendations_lead': RECS_LEAD,
                'recommendations_lead_ru': RECS_LEAD_RU,
                'recommendations_lead_en': '',
                'recommendations_lead_cs': '',
                'issued_on': date(2026, 10, 8),
                'intro_html': INTRO_HTML,
                'intro_html_ru': INTRO_HTML_RU,
                'intro_html_en': '',
                'intro_html_cs': '',
                'guarantee_html': GUARANTEE_HTML,
                'guarantee_html_ru': GUARANTEE_HTML_RU,
                'guarantee_html_en': '',
                'guarantee_html_cs': '',
                'cta_label': 'Обговорити проєкт',
                'cta_label_ru': 'Обсудить проект',
                'cta_label_en': '',
                'cta_label_cs': '',
                'kind': Proposal.DemoKind.SHOP,
                'corp_catalog': False,
                'is_published': True,
                'order': 24,
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
