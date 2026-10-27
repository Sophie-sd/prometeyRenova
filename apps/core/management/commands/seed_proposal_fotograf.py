"""
Management command: seed_proposal_fotograf

КП «Розробка корпоративного сайту з каталогом послуг та портфоліо фотографа під ключ»
(PDF 27.10.2026, українською): корпоративний сайт-портфоліо з каталогом послуг під ключ,
650 €, 30 днів. Оплата 50/50 (325 € + 325 €) або розстрочка 0% (Моно / Приват),
до 5 платежів по 130 €/міс. Kind — corporate (предмет договору: корпоративний сайт
з каталогом), corp_catalog=True. Демо — стандартний корпоративний сайт
(provision_demo_corp), без змін під клієнта.
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

SLUG = 'corporate-fotograf-0763'
CLIENT = 'Фотограф'
DEMO_TENANT_SLUG = 'korporatyvnyi-katalog-c1f5c0'
ISSUED_ON = date(2026, 10, 27)
ORDER = 45

TITLE = 'Розробка корпоративного сайту з каталогом послуг та портфоліо фотографа під ключ'
LEAD = (
    'Авторський сайт-портфоліо з онлайн-каталогом послуг фотографії, який допомагає '
    'презентувати себе, залучати преміальних клієнтів та автоматизувати '
    'онлайн-бронювання зйомок.'
)
RECS_LEAD = (
    'Технічне завдання (індивідуальні деталі проєкту «Фотограф»): розробка стильного '
    'авторського корпоративного сайту-портфоліо з онлайн-каталогом послуг фотографії.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Портфоліо · каталог послуг · бронювання'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Gallery', 'caption': 'Жанри зйомок · Lightbox', 'is_accent': False},
    {'order': 1, 'title': 'Services', 'caption': 'Пакети · ціни · терміни', 'is_accent': False},
    {'order': 2, 'title': 'Booking', 'caption': 'Запит дати зйомки · HTMX', 'is_accent': True},
    {'order': 3, 'title': 'Notify', 'caption': 'Telegram · CRM', 'is_accent': False},
    {'order': 4, 'title': 'Admin', 'caption': 'Фотосети · прайси · банери', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Преміальний мінімалістичний UI/UX дизайн',
        'description': (
            'Естетичний авторський інтерфейс, де головний акцент зосереджено на знімках, '
            'ідеально адаптований під екрани Retina, смартфони та ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Багатовекторний каталог зйомок та послуг',
        'description': (
            'Зручне структурування напрямків (весільна, портретна, комерційна, лукбуки, '
            'репортаж, контент для брендів) з детальними пакетами та цінами.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Інформативна картка послуги та серія робіт',
        'description': (
            'Детальний опис таймінгу зйомки, кількості оброблених фото, локацій, допомоги '
            'в позуванні та кастомні форми швидкого запиту бронювання дати.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Розумна система лідогенерації (HTMX)',
        'description': (
            'Інтерактивна форма бронювання дати зйомки або консультації, заявки з якої '
            'миттєво та без перезавантаження сторінки надходять у Telegram або CRM.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Індивідуальна адміністративна панель сайту',
        'description': (
            'Повнофункціональна та легка кастомна CMS для зручного самостійного '
            'завантаження нових фотосетів, оновлення прайсів і банерів без програмістів.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Маркетингова готовність та SEO-підготовка',
        'description': (
            'Правильна семантична розмітка під пошукові запити в Google, інтеграція '
            'рекламних пікселів Meta та аналітики (GA4/GTM) для виведення в топ.'
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
        'price': Decimal('650.00'),
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
            'Відмовляємося від важких конструкторів. Створюємо кастомну архітектуру на '
            'чистому коді, що забезпечує безшовний та довговічний результат.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Екстремальна швидкість 90+',
        'body': (
            'Блискавичне відкриття повноформатних фотографій високої якості без затримок '
            '(PageSpeed 90+) завдяки автоматичній оптимізації WebP/AVIF.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Enterprise-безпека & Масштаб',
        'body': (
            'Надійний захист бази клієнтів і комерційної інформації. Можливість у '
            'майбутньому легко підключити закриті клієнтські галереї чи продаж контенту.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Інтерактивні галереї без перезавантаження',
        'body': (
            'Швидка фільтрація зйомок за жанрами (Wedding, Love Story, Editorial, '
            'Commercial) з плавним повноекранним переглядом (Lightbox).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Пакетні пропозиції та ціни',
        'body': (
            'Структуроване порівняння тарифів (Minimal, Standard, Premium) із зазначенням '
            'тривалості, кількості ретушованих кадрів та термінів віддачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Швидкий календар зайнятості та контакт',
        'body': (
            'Швидка перевірка вільної дати, прямі кнопки переходу в Instagram, Telegram, '
            'WhatsApp для миттєвої комунікації з клієнтом.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Деплой та міграція',
        'body': (
            'Повне розгортання та оптимізація системи кешування зображень на надійному '
            'сервері, підключення SSL та прив’язка офіційного домену.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%) — 325 €',
        'body': 'Передплата перед початком розробки.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%) — 325 €',
        'body': 'Після фінального тестування перед деплоєм та передачею всіх доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0% (Моно / Приват): до 5 платежів по 130 €/міс.',
        'body': (
            'Доступна безвідсоткова розстрочка 0%: оплата частинами від Monobank та '
            'ПриватБанк без прихованих комісій — від 130 € на місяць. Сума ділиться '
            'рівними частинами до 5 місяців без переплат і відсотків. Старт розробки '
            'відразу після підтвердження.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми не просто створюємо сайти — ми будуємо веб-платформи для авторитетних фахівців, які допомагають презентувати себе, залучати преміальних клієнтів та автоматизувати онлайн-бронювання зйомок.</p>
<p>Стек: <strong>Django · HTML5 · HTMX · JS</strong>. Кастомна архітектура на чистому коді замість важких конструкторів.</p>
<ul>
<li><strong>Екстремальна швидкість 90+</strong> — повноформатні фотографії відкриваються без затримок завдяки автоматичній оптимізації WebP/AVIF.</li>
<li><strong>Enterprise-безпека &amp; Масштаб</strong> — надійний захист бази клієнтів; у майбутньому — закриті клієнтські галереї чи продаж контенту.</li>
<li><strong>Бронювання</strong> — запит на дату зйомки або консультацію миттєво надходить у Telegram / CRM.</li>
</ul>
<p>Офіційний договір, безготівковий розрахунок. Monobank / ПриватБанк (розстрочка 0%, до 5 платежів). Зв’яжіться з нашою командою для узгодження візуальної концепції та старту розробки: office@prometeylabs.com.</p>
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
        'Seed photographer portfolio + services catalog corporate proposal (650 €) '
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
