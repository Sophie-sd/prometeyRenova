"""
Management command: seed_proposal_zootovary

КП «Розробка інтернет-магазину зоотоварів під ключ» (PDF 22.10.2026, українською):
інтернет-магазин зоотоварів під ключ, 800–900 €, 30 днів.
Оплата 50/50 або розстрочка 0% (Моно / Приват), до 5 платежів від 160–180 €/міс.
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

SLUG = 'internet-mahazyn-zootovariv-cxpo'
CLIENT = 'Інтернет-магазин зоотоварів під ключ'
DEMO_TENANT_SLUG = 'zootovary-e456ce'
ISSUED_ON = date(2026, 10, 22)
ORDER = 41

TITLE = 'Розробка інтернет-магазину зоотоварів під ключ'
LEAD = (
    'Готовий інструмент для продажів, орієнтований на високий середній чек, зручний '
    'повторний шопінг для власників домашніх тварин та швидке масштабування вашого '
    'зообізнесу.'
)
RECS_LEAD = (
    'Технічне завдання: розробка сучасного комерційного інтернет-магазину для активних '
    'продажів товарів для домашніх тварин.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Фасування · фільтри · Нова Пошта'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Види тварин · категорії', 'is_accent': False},
    {'order': 1, 'title': 'Product', 'caption': 'Фасування · вік · склад', 'is_accent': False},
    {'order': 2, 'title': 'Cart', 'caption': 'Нова Пошта · кур’єр', 'is_accent': False},
    {'order': 3, 'title': 'Payment', 'caption': 'Картки · Apple Pay · Google Pay', 'is_accent': True},
    {'order': 4, 'title': 'Order', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Індивідуальний Mobile-First UI/UX дизайн',
        'description': (
            'Сучасний, теплий та ергономічний інтерфейс для швидкого вибору товарів '
            'під будь-які смартфони, планшети та ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Професійний каталог та картка товару',
        'description': (
            'Категоризація за видами тварин (собаки, коти, гризуни, птахи, '
            'акваріумістика), фільтри за вагою фасування, віком та складом.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумний кошик та інтеграція логістики',
        'description': (
            'Авторозрахунок вартості доставки, автоматичний вибір відділень та '
            'поштоматів Нової Пошти, кур’єрська доставка в 1 клік.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Безпечні онлайн-платежі',
        'description': (
            'Підключення офіційного еквайрингу для прийому оплат картками, Apple Pay '
            'та Google Pay безпосередньо на сайті.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Зручна кастомна адмін-панель',
        'description': (
            'Легка панель управління для швидкого додавання товарів, фасувань кормів, '
            'зміни цін, залишків та знижок без допомоги програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та SEO-структура',
        'description': (
            'Інтеграція пікселів, тегів аналітики (GA4, GTM), підготовка товарного '
            'фіду для Google Shopping та базова SEO-розмітка категорій.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин зоотоварів під ключ',
        'scope': (
            'Дизайн, чистий код (Django/HTMX), індивідуальна адмін-панель, '
            'онлайн-оплати, інтеграція пошти/сервісів доставки, аналітика, повний '
            'деплой та підключення домену.'
        ),
        'duration': '30 днів',
        'price': Decimal('800.00'),
        'price_high': Decimal('900.00'),
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
            'кодописні рішення з високою віддачею та стійкістю до трафіку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Блискавична швидкість завантаження каталогу кормів та зоотоварів, що '
            'утримує клієнтів зі смартфонів та покращує SEO в Google.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Повна незалежність',
        'body': (
            'Жодних обмежень шаблонів, платних сторонніх плагінів чи щомісячних '
            'платежів за платформи, повна безпека даних клієнтів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Специфікація фасування (HTMX)',
        'body': (
            'Швидкий вибір ваги упаковки корму (наприклад, 400 г, 2 кг, 10 кг, 15 кг) '
            'прямо в картці товару зі зміною ціни без перезавантаження.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Пошук та фільтри',
        'body': (
            'Живий пошук товарів за назвою та брендом, фільтрація за призначенням '
            '(сухий/вологий корм, ласощі, вітаміни, ветаптека, іграшки).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Повідомлення про замовлення',
        'body': (
            'Моментальне надсилання нових покупок у Telegram менеджеру або в '
            'CRM-систему магазину для швидкої комплектації.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та запуск',
        'body': (
            'Налаштування хостингу, захищеного SSL-сертифікату безпеки, підключення '
            'робочого домену та запуск систем аналітики.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%)',
        'body': 'Передплата перед стартом проєктування та UI/UX.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%)',
        'body': 'Після тестування перед винесенням на робочий домен.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів від 160–180 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 160 € на місяць. Сума ділиться '
            'рівними частинами до 5 місяців (від 160–180 €/міс). Роботи стартують '
            'одразу після погодження.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо готові інструменти для продажів, орієнтовані на високий середній чек, зручний повторний шопінг для власників домашніх тварин та швидке масштабування вашого зообізнесу.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Відмовляємося від важких конструкторів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — блискавична швидкість завантаження каталогу кормів та зоотоварів.</li>
<li><strong>Повна незалежність</strong> — жодних платних сторонніх плагінів чи щомісячних платежів за платформи.</li>
<li><strong>Замовлення</strong> — нові покупки моментально в Telegram менеджеру або в CRM.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 5 платежів). Зв’яжіться з нашою командою для узгодження асортименту зоотоварів та старту розробки: office@prometeylabs.com.</p>
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
    help = 'Seed pet-supplies e-shop proposal (800–900 €) + standard demo-shop (idempotent)'

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
