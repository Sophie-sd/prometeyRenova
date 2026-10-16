"""
Management command: seed_proposal_metal_furniture

Idempotent заливка КП «Металеві меблі» (11.10.2026, українською)
+ B2B demo-shop (quote mode, no prices/cart). Це не версія сайту клієнта, а стандартне демо.
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

SLUG = 'kovovy-nabytek-7c1e'
DEMO_TENANT_SLUG = 'metal-furniture-demo-7c1e'

TITLE = 'Webová platforma pro kovový nábytek'
TITLE_RU = 'Веб-платформа для металевих меблів'
LEAD = (
    'Spolehlivý B2B katalog kovových výrobků: rychlost, přehledná navigace '
    'a bezpečný systém poptávek pro firemní zákazníky.'
)
LEAD_RU = (
    'Надійний B2B-каталог виробів з металу: швидкість, зрозуміла навігація '
    'та безпечна система запитів ціни для корпоративних клієнтів.'
)

RECS_LEAD = (
    'Katalog kovového nábytku na Django / HTMX: čistý kód bez CMS, '
    'PageSpeed 90+ a stabilita pod zátěží.'
)
RECS_LEAD_RU = (
    'Каталог металевих меблів на Django / HTMX: чистий код без CMS, '
    'PageSpeed 90+ і стабільність під навантаженнями.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'B2B-каталог'},
    {'order': 3, 'title': 'Запит ціни'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Каталог', 'caption': 'Матеріал · тип', 'is_accent': False},
    {'order': 1, 'title': 'Фільтр', 'caption': 'Сталь · нержавійка', 'is_accent': True},
    {'order': 2, 'title': 'Картка', 'caption': 'Фото · опис', 'is_accent': False},
    {'order': 3, 'title': 'Запит', 'caption': 'Запит ціни', 'is_accent': False},
    {'order': 4, 'title': 'Адмінка', 'caption': 'Товари · запити', 'is_accent': False},
]

# Етапи (довідково, загалом 20–28 робочих днів)
STAGES_UK = [
    ('Підготовка', '2–3 дні', 'Переглядаємо матеріали, уточнюємо обсяг (мови, оплата, запити) і готуємо структуру сайту.'),
    ('Дизайн', '4–6 днів', 'Макети ключових сторінок для комп’ютера й телефона. Ви коментуєте й затверджуєте.'),
    ('Розробка сайту й адмінки', '8–10 днів', 'Будуємо сайт і адмінку за затвердженим макетом.'),
    ('Перенесення контенту', '3–4 дні', 'Імпорт товарів, фото й текстів, налаштування перенаправлень зі старих адрес.'),
    ('Тестування', '2–3 дні', 'Перевірка на тестовій адресі на комп’ютері й телефоні. Ви все пробуєте самі.'),
    ('Запуск', '1–2 дні', 'Перемикання домену, перевірка після запуску і передача адмінки.'),
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Profesionální UI/UX design pro B2B',
        'title_ru': 'Професійний UI/UX дизайн для B2B',
        'description': (
            'Průmyslový redakční design zaměřený na firemní zákazníky: '
            'jasná struktura katalogu a rychlý přístup k informacím.'
        ),
        'description_ru': (
            'Промисловий редакційний дизайн, орієнтований на корпоративних клієнтів: '
            'чітка структура каталогу та швидкий доступ до інформації.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Strukturovaný katalog s filtry',
        'title_ru': 'Структурований каталог з фільтрами',
        'description': (
            'Kategorie produktů (lavice, stoly, regály, skříně, vozíky, zdravotnický nábytek), '
            'filtry podle materiálu (ocel, nerez, hliník, dřevo+ocel) a rychlé vyhledávání.'
        ),
        'description_ru': (
            'Категорії продуктів (лавки, столи, стелажі, шафи, візки, медичні меблі), '
            'фільтри за матеріалом (сталь, нержавійка, алюміній, дерево+сталь) та швидкий пошук.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Detailní karta produktu',
        'title_ru': 'Детальна картка продукту',
        'description': (
            'Galerie fotografií, technické specifikace, popis použití '
            'a tlačítko «Poptat cenu» místo přímých cen pro individuální přístup.'
        ),
        'description_ru': (
            'Галерея фотографій, технічні специфікації, опис використання '
            'та кнопка «Запитати ціну» замість прямих цін для індивідуального підходу.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Systém poptávky ceny',
        'title_ru': 'Система запиту ціни',
        'description': (
            'Formulář poptávky s výběrem produktů, uvedením množství a kontaktních údajů. '
            'Poptávky přicházejí na e-mail a ukládají se do systému.'
        ),
        'description_ru': (
            'Форма запиту з вибором продуктів, вказанням кількості та контактних даних. '
            'Запити надходять на e-mail і зберігаються в системі.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Pohodlná administrace',
        'title_ru': 'Зручна адміністрація',
        'description': (
            'Individuální systém správy: snadné editování produktů, cen, fotografií, '
            'kategorií a zobrazení poptávek zákazníků bez programátorů.'
        ),
        'description_ru': (
            'Індивідуальна система управління: легке редагування продуктів, цін, фотографій, '
            'категорій та перегляд запитів клієнтів без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'SEO a analytika',
        'title_ru': 'SEO та аналітика',
        'description': (
            'Základní SEO optimalizace meta tagů, strukturovaná data pro Google, '
            'mapa webu a připojení Google Analytics 4.'
        ),
        'description_ru': (
            'Базова SEO оптимізація мета-тегів, структуровані дані для Google, '
            'карта сайту та підключення Google Analytics 4.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'BASE',
        'name_ru': 'BASE',
        'scope': (
            'Katalog s poptávkou ceny; nový design z Figmy; pohodlná administrace; '
            'import všech produktů, fotografií a textů; přesměrování starých adres (301); '
            'základy SEO; nastavení hostingu s HTTPS; 1 rok záruka na kód.'
        ),
        'scope_ru': (
            'Каталог із запитом ціни; новий дизайн з Figma; зручна адміністрація; '
            'імпорт усіх продуктів, фотографій та текстів; перенаправлення старих адрес (301); '
            'основи SEO; налаштування хостингу з HTTPS; пожиттєва гарантія на код і 1 рік безкоштовної підтримки.'
        ),
        'duration': '20–22 pracovních dnů',
        'duration_ru': '20–22 робочих дні',
        'price': Decimal('1600.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'PREMIUM',
        'name_ru': 'PREMIUM',
        'scope': (
            'Vše z balíčku BASE; košík s online platbou a dopravou; údaje o produktech '
            'pro Google a rozšířené SEO; poptávky a objednávky do e-mailu nebo CRM; '
            'nastavení analytiky návštěvnosti.'
        ),
        'scope_ru': (
            'Усе з пакета BASE; кошик з онлайн-оплатою та доставкою; дані про продукти '
            'для Google та розширене SEO; запити та замовлення на e-mail або в CRM; '
            'налаштування аналітики відвідуваності.'
        ),
        'duration': '22–25 pracovních dnů',
        'duration_ru': '22–25 робочих днів',
        'price': Decimal('2200.00'),
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'PLATINUM',
        'name_ru': 'PLATINUM',
        'scope': (
            'Vše z balíčku PREMIUM; druhá jazyková verze webu; nastavení reklamního '
            'účtu Google Ads; rozšířená optimalizace rychlosti a zabezpečení; '
            'přednostní podpora v měsíci spuštění.'
        ),
        'scope_ru': (
            'Усе з пакета PREMIUM; друга мовна версія сайту; налаштування рекламного '
            'акаунта Google Ads; розширена оптимізація швидкості та захисту; '
            'пріоритетна підтримка в місяць запуску.'
        ),
        'duration': '25–28 pracovních dnů',
        'duration_ru': '25–28 робочих днів',
        'price': Decimal('2800.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Katalog s filtry',
        'title_ru': 'Каталог з фільтрами',
        'body': (
            'Kategorie: lavice, stoly, regály, skříně, vozíky, zdravotnický nábytek. '
            'Filtry: ocel, nerez, hliník, kombinované materiály (dřevo+ocel). '
            'Rychlé vyhledávání podle názvu.'
        ),
        'body_ru': (
            'Категорії: лавки, столи, стелажі, шафи, візки, медичні меблі. '
            'Фільтри: сталь, нержавійка, алюміній, комбіновані матеріали (дерево+сталь). '
            'Швидкий пошук по назві.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Poptávka ceny místo košíku',
        'title_ru': 'Запит ціни замість кошика',
        'body': (
            'Zákazník vybere produkty, uvede množství a zanechá kontakt. '
            'Poptávka přijde na e-mail a uloží se do administrace.'
        ),
        'body_ru': (
            'Клієнт обирає товари, вказує кількість та залишає контакти. '
            'Запит надходить на e-mail та зберігається в адмін-панелі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Přenos ze současného webu',
        'title_ru': 'Перенесення з нинішнього сайту',
        'body': (
            'Automatický import všech 162 produktů, 15 kategorií a ~372 fotografií. '
            '301 přesměrování ze starých adres na nové pro zachování pozic v Google.'
        ),
        'body_ru': (
            'Автоматичний імпорт усіх 162 товарів, 15 категорій та ~372 фото. '
            '301-редиректи зі старих адрес на нові для збереження позицій у Google.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Čistý kód (No-CMS)',
        'title_ru': 'Чистий код (No-CMS)',
        'body': (
            'Django / Python, HTML5, CSS3, JavaScript a HTMX. '
            'Žádné pomalé šablony WordPress/WooCommerce ani konstruktory.'
        ),
        'body_ru': (
            'Django / Python, HTML5, CSS3, JavaScript та HTMX. '
            'Жодних повільних шаблонів WordPress/WooCommerce чи конструкторів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Google PageSpeed 90+',
        'title_ru': 'Google PageSpeed 90+',
        'body': (
            'Bleskové otevírání stránek na smartphonech i PC. '
            'Maximální hodnocení pro vyhledávačové umístění v Google.'
        ),
        'body_ru': (
            'Блискавичне відкриття сторінок на смартфонах і ПК. '
            'Максимальний рейтинг для пошукового просування в Google.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Stabilita pod zátěží',
        'title_ru': 'Стабільність до навантажень',
        'body': (
            'Plná nezávislost na placených zranitelných pluginech a odolnost '
            'databáze proti špičkovému provozu od firemních zákazníků.'
        ),
        'body_ru': (
            'Повна незалежність від платних вразливих плагінів і стійкість '
            'бази даних до пікового трафіку від корпоративних клієнтів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1. platba: 50%',
        'title_ru': '1-й платіж: 50%',
        'body': 'Záloha před zahájením prací.',
        'body_ru': 'Аванс перед стартом робіт.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2. platba: 50%',
        'title_ru': '2-й платіж: 50%',
        'body': 'Při spuštění projektu.',
        'body_ru': 'Під час релізу проєкту.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Bankovní převod',
        'title_ru': 'Банківський переказ',
        'body': 'Platba na bankovní účet (IBAN). Faktura s DPH.',
        'body_ru': 'Оплата на банківський рахунок (IBAN). Рахунок з ПДВ.',
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — tým zkušených vývojářů, kteří budují spolehlivé nástroje pro B2B prodej. Vytváříme webovou platformu pro katalog kovového nábytku, orientovanou na firemní zákazníky, rychlost a pohodlné poptávky.</p>
<p>Stack: <strong>Django (Python) · HTML5 · CSS3 · JavaScript · HTMX</strong>. Bez WordPress, WooCommerce a konstruktorů.</p>
<ul>
<li><strong>Google PageSpeed 90+</strong> — stránky se otevírají bleskově na smartphonech i PC.</li>
<li><strong>Stabilita pod zátěží</strong> — databáze zvládá špičkový provoz od firemních odběratelů.</li>
<li><strong>Automatický přenos</strong> — všech 162 produktů, kategorie a fotografie se přenesou automaticky ze současného webu.</li>
</ul>
<p>Platba: bankovní převod (IBAN). Podpora a konzultace: office@prometeylabs.com.</p>
""".strip()

INTRO_HTML_RU = """
<p><strong>PrometeyLabs</strong> — команда досвідчених розробників, які будують надійні інструменти для B2B-продажів. Ми створюємо веб-платформу для каталогу металевих меблів, орієнтовану на корпоративних клієнтів, швидкість та зручність запитів.</p>
<p>Стек: <strong>Django (Python) · HTML5 · CSS3 · JavaScript · HTMX</strong>. Без WordPress, WooCommerce і конструкторів.</p>
<ul>
<li><strong>Google PageSpeed 90+</strong> — сторінки відкриваються блискавично на смартфонах і ПК.</li>
<li><strong>Стабільність до навантажень</strong> — база даних тримає піковий трафік від корпоративних замовників.</li>
<li><strong>Автоматичне перенесення</strong> — всі 162 товари, категорії та фото переносяться автоматично з нинішнього сайту.</li>
</ul>
<p>Оплата: банківський переказ (IBAN). Підтримка й консультація: office@prometeylabs.com.</p>
""".strip()

GUARANTEE_HTML = """
<p>Jsme si jisti kvalitou našeho inženýrského základu. Protože web je vytvořen na čistém kódu bez nestabilních externích pluginů, nevyžaduje neustálé rizikové aktualizace, které ničí layout.</p>
<p>Poskytujeme <strong>1 rok záruky na kód</strong> od okamžiku úplné platby a předání přístupů: technické chyby způsobené naší vinou opravíme zdarma (veřejná nabídka, bod 8.1).</p>
""".strip()

GUARANTEE_HTML_RU = """
<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів, він не потребує постійних ризикованих оновлень, які ламають верстку.</p>
<p>Ми надаємо <strong>пожиттєву гарантію на код</strong>: технічні баги, допущені з нашої вини, виправляємо безкоштовно без обмеження строку, а також <strong>1 рік безкоштовної підтримки</strong> з моменту запуску.</p>
""".strip()


# --- Ukrainian-primary: усі мовні версії показують український текст ---
TITLE, LEAD, RECS_LEAD = TITLE_RU, LEAD_RU, RECS_LEAD_RU
INTRO_HTML, GUARANTEE_HTML = INTRO_HTML_RU, GUARANTEE_HTML_RU
for _row in (*MODULES, *PACKAGES, *SPECS):
    for _k in [k for k in _row if k.endswith('_ru')]:
        _row[_k[:-3]] = _row[_k]


def _with_langs(payload: dict, text_keys: tuple[str, ...]) -> dict:
    out = dict(payload)
    for key in text_keys:
        ru_key = f'{key}_ru'
        cs_key = f'{key}_cs'
        en_key = f'{key}_en'
        # _ru gets Ukrainian (already provided in payload)
        # _cs and _en get Czech from base field
        out[cs_key] = out.get(key, '')
        out[en_key] = out.get(key, '')
        out[ru_key] = out.get(key, '')
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
    help = 'Seed metal furniture proposal + B2B demo-shop (idempotent)'

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
            f'{action}: /proposal/{proposal.slug}/ '
            f'({proposal.modules.count()} modules, '
            f'{proposal.packages.count()} packages)'
        ))

    def _provision_demo(self, proposal: Proposal) -> None:
        """Стандартний демо-магазин (як у всіх КП) через provision_demo_shop()."""
        from apps.demoshop.models import DemoShop
        from apps.demoshop.services.provision import provision_demo_shop

        shop = DemoShop.objects.filter(proposal=proposal).first()
        # Legacy custom B2B demo -> drop it and recreate as standard shop (same URL)
        if shop is not None and (shop.furniture_mode or shop.quote_mode):
            owner = shop.owner_user
            shop.delete()
            if owner is not None:
                owner.delete()
            shop = None
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
                'client_name': 'Металеві меблі',
                'title': TITLE,
                'title_ru': TITLE_RU,
                'title_en': TITLE,
                'title_cs': TITLE,
                'lead': LEAD,
                'lead_ru': LEAD_RU,
                'lead_en': LEAD,
                'lead_cs': LEAD,
                'recommendations_lead': RECS_LEAD,
                'recommendations_lead_ru': RECS_LEAD_RU,
                'recommendations_lead_en': RECS_LEAD,
                'recommendations_lead_cs': RECS_LEAD,
                'issued_on': date(2026, 10, 11),
                'intro_html': INTRO_HTML,
                'intro_html_ru': INTRO_HTML_RU,
                'intro_html_en': INTRO_HTML,
                'intro_html_cs': INTRO_HTML,
                'guarantee_html': GUARANTEE_HTML,
                'guarantee_html_ru': GUARANTEE_HTML_RU,
                'guarantee_html_en': GUARANTEE_HTML,
                'guarantee_html_cs': GUARANTEE_HTML,
                'cta_label': 'Обговорити проєкт',
                'cta_label_ru': 'Обговорити проєкт',
                'cta_label_en': 'Обговорити проєкт',
                'cta_label_cs': 'Обговорити проєкт',
                'kind': Proposal.DemoKind.SHOP,
                'corp_catalog': False,
                'is_published': True,
                'order': 25,
            },
        )
        proposal.modules.all().delete()
        for data in MODULES:
            create_with_leftovers(
                ProposalModule, proposal=proposal, **_with_langs(data, ('title', 'description')),
            )
        proposal.packages.all().delete()
        for data in PACKAGES:
            create_with_leftovers(
                ProposalPackage,
                proposal=proposal,
                **_with_langs(data, ('name', 'scope', 'duration')),
            )
        proposal.specs.all().delete()
        for data in SPECS:
            create_with_leftovers(
                ProposalSpec, proposal=proposal, **_with_langs(data, ('title', 'body')),
            )
        proposal.highlights.all().delete()
        for data in HIGHLIGHTS:
            create_with_leftovers(
                ProposalHighlight, proposal=proposal, **_with_langs(data, ('title',)),
            )
        proposal.arch_nodes.all().delete()
        for data in ARCH_NODES:
            create_with_leftovers(
                ProposalArchNode, proposal=proposal, **_with_langs(data, ('title', 'caption')),
            )
        _attach_hero(proposal)
        return proposal, created
