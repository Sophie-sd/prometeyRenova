"""
Management command: seed_proposal_profremservice

КП «Розробка корпоративного сайту з каталогом для profremservice.com.ua під ключ»
(PDF 26.10.2026, українською): корпоративний сайт з каталогом під ключ, 700 – 720 €, 30 днів.
Оплата 50/50 або розстрочка 0% (Моно / Приват), до 5 платежів від 140–144 €/міс.
Kind — corporate (предмет договору: корпоративний сайт з каталогом), corp_catalog=True.
Демо — стандартний корпоративний сайт (provision_demo_corp), без змін під клієнта.
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

SLUG = 'corporate-profremservice-mnte'
CLIENT = 'profremservice.com.ua'
DEMO_TENANT_SLUG = 'korporatyvnyi-katalog-ffdad5'
ISSUED_ON = date(2026, 10, 26)
ORDER = 44

TITLE = 'Розробка корпоративного сайту з каталогом для profremservice.com.ua під ключ'
LEAD = (
    'Масштабна веб-платформа для лідерів ринку ремонту техніки, яка допомагає '
    'презентувати себе, залучати клієнтів зі смартфонів та автоматизувати обробку '
    'заявок на ремонт побутової, цифрової та промислової електроніки.'
)
RECS_LEAD = (
    'Технічне завдання: модернізація та перезапуск корпоративного сайту сервісного '
    'центру ремонту техніки profremservice.com.ua.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Каталог послуг · бренди · заявки'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Catalog', 'caption': 'Категорії техніки · бренди', 'is_accent': False},
    {'order': 1, 'title': 'Service', 'caption': 'Несправності · ціни · терміни', 'is_accent': False},
    {'order': 2, 'title': 'Lead', 'caption': 'Виклик майстра · HTMX', 'is_accent': True},
    {'order': 3, 'title': 'Notify', 'caption': 'Telegram · CRM', 'is_accent': False},
    {'order': 4, 'title': 'Admin', 'caption': 'Прайси · філії · акції', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Професійний UI/UX дизайн',
        'description': (
            'Структурований, інтуїтивно зрозумілий інтерфейс у стилі надійного '
            'технологічного сервісу, адаптований під смартфони та ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Багатовекторний каталог послуг з ремонту',
        'description': (
            'Категоризація напрямків (ремонт побутової техніки, кавомашин, електроніки, '
            'плат, телевізорів) з брендами, симптомами несправностей і цінами.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Інформативна картка послуги',
        'description': (
            'Детальний опис типових несправностей, орієнтовна вартість робіт, терміни '
            'діагностики, гарантії та форми швидкого виклику майстра.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Розумна система лідогенерації (HTMX)',
        'description': (
            'Кастомні форми виклику майстра додому або запису в майстерню, заявки з '
            'яких миттєво та без перезавантаження надходять у Telegram / CRM.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Індивідуальна адміністративна панель сайту',
        'description': (
            'Повнофункціональна кастомна CMS для зміни прайсів, додавання нових '
            'категорій техніки, контактів філій та акцій без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та SEO-підготовка',
        'description': (
            'Правильна ієрархія тегів під локальне SEO в Києві, інтеграція рекламних '
            'пікселів і аналітики (GA4/GTM) для максимальної віддачі реклами.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Корпоративний сайт з каталогом під ключ',
        'scope': (
            'Проєктування архітектури БД, преміум-дизайн, Frontend та Backend розробка, '
            'кастомна CMS, інтеграція аналітики, SEO-підготовка, повний деплой на '
            'сервер та підключення домену.'
        ),
        'duration': '30 днів',
        'price': Decimal('700.00'),
        'price_high': Decimal('720.00'),
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
            'Відмовляємося від шаблонних конструкторів, які гальмують роботу під час '
            'піків реклами. Створюємо кастомну архітектуру на чистому стеку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Екстремальна швидкість 90+',
        'body': (
            'Блискавичне відкриття сторінок послуг ремонту (PageSpeed 90+), що покращує '
            'поведінкові фактори клієнтів та піднімає позиції в Google (SEO).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Enterprise-безпека & Масштаб',
        'body': (
            'Кастомне ядро захищає базу замовлень. Можливість у майбутньому легко '
            'інтегрувати особисті кабінети клієнтів чи статус замовлення за квитанцією.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Каталог категорій та брендів',
        'body': (
            'Швидкий перехід до потрібного пристрою (пральні машини, бойлери, '
            'холодильники, плати управління) з переліком брендів (Bosch, Samsung, LG тощо).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Швидкий зв’язок у 1 клік',
        'body': (
            'Прямий дзвінок диспетчеру, кнопки запису в Telegram і Viber, а також форма '
            'експрес-заявки з вибором району Києва.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Формування довіри',
        'body': (
            'Відкриті прайс-листи без прихованих платежів, гарантійні зобов’язання на '
            'замінені деталі, відгуки клієнтів та карта майстерні.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та міграція',
        'body': (
            'Перенесення потрібного контенту, збереження SEO-ваги поточного домену, '
            'налаштування SSL та запуск на хостингу.'
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
        'body': 'Після тестування перед деплоєм на робочий домен.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів від 140–144 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 140–144 € на місяць. Сума ділиться '
            'рівними частинами до 5 місяців без переплат і відсотків. Початок робіт одразу.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо масштабні веб-платформи для лідерів ринку ремонту техніки, які допомагають компаніям презентувати себе, залучати клієнтів зі смартфонів та автоматизувати обробку заявок на ремонт побутової, цифрової та промислової електроніки.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Кастомна архітектура на чистому стеку замість шаблонних конструкторів.</p>
<ul>
<li><strong>Екстремальна швидкість 90+</strong> — блискавичне відкриття сторінок послуг ремонту (PageSpeed 90+).</li>
<li><strong>Enterprise-безпека &amp; Масштаб</strong> — кастомне ядро захищає базу замовлень.</li>
<li><strong>Заявки</strong> — виклик майстра додому або запис у майстерню миттєво в Telegram / CRM.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 5 платежів). Зв’яжіться з нашою командою для узгодження структури сайту та старту розробки: office@prometeylabs.com.</p>
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
        'Seed profremservice.com.ua corporate catalog proposal (700 – 720 €) '
        '+ standard demo-corp (idempotent)'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_corp',
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
        """Стандартний демо корпоративного сайту (як у всіх corporate КП) через provision_demo_corp()."""
        from apps.democorp.models import CorpSite
        from apps.democorp.services.provision import provision_demo_corp
        from apps.demoshop.models import DemoShop

        DemoShop.objects.filter(proposal=proposal).delete()
        site = CorpSite.objects.filter(proposal=proposal).first()
        if site is None:
            site = CorpSite(
                proposal=proposal,
                name='Demo Site',
                slug=DEMO_TENANT_SLUG,
            )
            site.save()
        site = provision_demo_corp(proposal)
        if site.name != 'Demo Site':
            site.name = 'Demo Site'
            site.save(update_fields=['name'])
        self.stdout.write(self.style.SUCCESS(
            f'Demo: {site.get_absolute_url()} (slug={site.slug})'
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
                'kind': Proposal.DemoKind.CORPORATE,
                'corp_catalog': True,
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
