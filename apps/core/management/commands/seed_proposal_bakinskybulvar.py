"""
Management command: seed_proposal_bakinskybulvar

КП «Розробка корпоративного сайту з каталогом для bakinskybulvar.com під ключ»
(PDF 22.10.2026): корпоративний сайт з каталогом під ключ, 800 €, 14 днів.
Оплата 50/50 (400 € + 400 €) або розстрочка 0% (Моно / Приват), до 5 платежів по 160 €/міс.
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

SLUG = 'corporate-bakinskybulvar-a22z'
CLIENT = 'bakinskybulvar.com'
DEMO_TENANT_SLUG = 'bakinskybulvar-144a03'
ISSUED_ON = date(2026, 10, 22)
ORDER = 40

TITLE = 'Розробка корпоративного сайту з каталогом для bakinskybulvar.com під ключ'
LEAD = (
    'Масштабна веб-платформа, яка допомагає презентувати заклад, залучати гостей, '
    'показувати меню й банкетні зали та автоматизувати обробку замовлень і бронювань.'
)
RECS_LEAD = (
    'Технічне завдання для bakinskybulvar.com: інтерактивний каталог меню, презентація '
    'локацій, бронювання та івенти із заявками в Telegram, деплой і міграція контенту.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Меню · зали · бронювання'},
    {'order': 3, 'title': '14 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Menu', 'caption': 'Кухні · категорії', 'is_accent': False},
    {'order': 1, 'title': 'Dish', 'caption': 'Склад · вага · ккал', 'is_accent': False},
    {'order': 2, 'title': 'Halls', 'caption': 'Зали · тераса · котеджі', 'is_accent': False},
    {'order': 3, 'title': 'Booking', 'caption': 'Стіл · бенкет · доставка', 'is_accent': True},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Професійний преміальний UI/UX дизайн',
        'description': (
            'Сучасний інтерфейс у ресторанній естетиці з акцентом на атмосферу закладу '
            'та комфортний перегляд зі смартфонів і ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Багатовекторний каталог меню та послуг',
        'description': (
            'Розділи меню (мангал, гаряче, десерти, бар), банкетне обслуговування, '
            'котеджі та номери — зручна навігація за категоріями.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Інформативна картка страви та зали',
        'description': (
            'Інгредієнти, вага, калорійність, фотогалереї, форми швидкого запиту та '
            'бронювання столів.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Розумна система лідогенерації (HTMX)',
        'description': (
            'Бронювання столика, замовлення бенкету чи доставки — заявки моментально '
            'надходять у Telegram/CRM.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Індивідуальна адміністративна панель',
        'description': (
            'Кастомна CMS: самостійне оновлення сезонного меню, цін, фото залів, '
            'банерів та подій без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та SEO-підготовка',
        'description': (
            'Мапа редиректів, правильна ієрархія тегів, пікселі, інтеграція GA4 / GTM.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт з каталогом під ключ',
        'scope': (
            'Проєктування БД, преміум-дизайн, Frontend і Backend, кастомна CMS, '
            'аналітика, SEO-підготовка, деплой і домен.'
        ),
        'duration': '14 днів',
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
            'Кастомна архітектура замість конструкторів: швидке, надійне рішення на '
            'чистому коді.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'body': (
            'Екстремальна швидкість: меню, галереї залів і сторінки бронювання '
            'відкриваються миттєво на смартфонах.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Безпека Enterprise-рівня',
        'body': (
            'Надійний захист даних гостей і замовлень, незалежність від сторонніх '
            'плагінів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Інтерактивний каталог меню',
        'body': (
            'Фільтрація страв азербайджанської та європейської кухонь без оновлення '
            'сторінки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Презентація локацій',
        'body': (
            'Сторінки основних і банкетних залів, літньої тераси та котеджного '
            'містечка з галереями.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Бронювання та івенти',
        'body': (
            'Форми резервування столу, прорахунку весіль, корпоративів і дитячих свят '
            'з передачею заявок у Telegram адміністраторам.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та міграція',
        'body': (
            'Перенесення контенту, розгортання на сервері та підключення домену '
            'bakinskybulvar.com.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%): 400 €',
        'body': 'Передплата перед стартом проєктування.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%): 400 €',
        'body': 'Після фінального тестування перед деплоєм і передачею доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів по 160 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0% від Monobank та ПриватБанк — від '
            '160 € на місяць, до 5 платежів без переплат. Старт робіт одразу після '
            'оформлення.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми будуємо масштабні веб-платформи для лідерів ринку, які допомагають компаніям презентувати себе, залучати гостей, презентувати меню й банкетні зали та автоматизувати обробку замовлень і бронювань.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Кастомна архітектура замість конструкторів.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — екстремальна швидкість завантаження меню та галерей.</li>
<li><strong>Безпека Enterprise-рівня</strong> — захист даних гостей і замовлень.</li>
<li><strong>Заявки</strong> — бронювання столика, бенкету чи доставки миттєво в Telegram або CRM.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 5 платежів). Зв’яжіться з нашою командою для узгодження структури та запуску розробки: office@prometeylabs.com.</p>
""".strip()

# Канон гарантії: пожиттєва гарантія на код + 1 рік безкоштовної підтримки.
GUARANTEE_HTML = """
<p>Ми впевнені у якості нашого коду. Оскільки система пишеться на чистому коді без сторонніх плагінів, вона не потребує ризикованих оновлень, які часто ламають звичайні сайти.</p>
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
    help = 'Seed bakinskybulvar.com corporate catalog proposal + standard demo-shop (idempotent)'

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
