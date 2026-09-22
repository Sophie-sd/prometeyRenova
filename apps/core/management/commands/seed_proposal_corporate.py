"""
Management command: seed_proposal_corporate

Idempotent заливка КП Liber (контент з PDF 22.09.2026) + класичне demo-corp.
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

SLUG = 'corporate-liber-a7f3'

RECS_LEAD = (
    'Інженерні рішення для корпоративного сайту під ключ — Django / HTMX / CSS / JS, '
    'без конструкторів і без залежності від платних плагінів.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'До 30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Admin', 'caption': 'Django CMS', 'is_accent': False},
    {'order': 1, 'title': 'Home', 'caption': '', 'is_accent': False},
    {'order': 2, 'title': 'Services', 'caption': '', 'is_accent': True},
    {'order': 3, 'title': 'About', 'caption': 'Кейси / блог', 'is_accent': False},
    {'order': 4, 'title': 'Leads', 'caption': 'Telegram · CRM', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Преміальний UI/UX дизайн',
        'description': (
            'Індивідуальний адаптивний інтерфейс, вивірений для бездоганного '
            'відображення на смартфонах, планшетах і ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Презентація послуг та інтерактив',
        'description': (
            'Логічна архітектура сторінок, динамічні блоки вигод та інтерактивні '
            'елементи максимального утримання уваги.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Розумна лідогенерація',
        'description': (
            'Форми зворотного зв’язку на базі HTMX — миттєва відправка заявок '
            'у Telegram, CRM або на Email без перезавантаження сторінки.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Розділи авторитету',
        'description': (
            'Сторінки «Про компанію», «Портфоліо/Кейси», «Блог та новини» '
            'для формування довіри та публікації експертного контенту.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Кастомна панель керування',
        'description': (
            'Легка Django-адмінка: тексти, банери й контакти оновлюєте самі, '
            'без програміста на кожну правку.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Перехід зі старого сайту без втрати SEO та контенту',
        'description': (
            'Переносимо тексти й фото з liber.com.ua, ставимо 301 зі старих URL, '
            'зберігаємо ЧПУ де можливо, оновлюємо title/description і перевіряємо '
            'індексацію в Search Console після запуску.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Base — корпоративний сайт',
        'scope': (
            'Запуск під ключ: індивідуальний UI/UX усіх сторінок, '
            'стек Django / HTMX / CSS / JS, кастомна адмін-панель, '
            'миттєве сповіщення про ліди в Telegram/Email, '
            'базова внутрішня SEO-структура, підключення домену та деплой, '
            'перенесення контенту зі старого сайту та 301-редіректи без втрати SEO.'
        ),
        'duration': 'до 30 днів',
        'price': Decimal('1150.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Premium — маркетинговий старт',
        'scope': (
            'Усе з пакету Base плюс рекламний кабінет '
            '(Google Ads / Meta), семантичне ядро та SEO-просування, '
            'аналітика, пікселі й конверсійні цілі, 3 місяці ведення реклами '
            'та SEO, щомісячний аудит вартості ліда.'
        ),
        'duration': 'до 30 днів + 3 місяці супроводу',
        'price': Decimal('2000.00'),
        'currency': '€',
        'is_recommended': True,
    },
    {
        'order': 2,
        'name': 'Ведення реклами',
        'scope': (
            'Оптимізація та супровід рекламних кампаній, A/B тестування '
            'оголошень, контроль бюджету та щомісячна звітність.'
        ),
        'duration': 'щомісяця після запуску',
        'price': Decimal('200.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 3,
        'name': 'Реклама + SEO + підтримка',
        'scope': (
            'Ведення реклами + нарощування посилальної маси та SEO-трафіку '
            '+ технічний моніторинг стабільності сайту та контентна підтримка.'
        ),
        'duration': 'щомісяця після запуску',
        'price': Decimal('500.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Деплой і домен',
        'body': (
            'Підключення домену, деплой та налаштування сервера входять '
            'у пакет запуску під ключ.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Базова SEO-структура',
        'body': (
            'Внутрішня SEO-структура під Google: ЧПУ, мета, коректна ієрархія '
            'сторінок. Розширене просування — у пакеті Premium.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Міграція зі старого сайту',
        'body': (
            'Контент і структуру liber.com.ua переносимо на новий стек. '
            '301 зі старих URL, збереження ЧПУ де можливо, оновлені '
            'title/description, перевірка індексації в Search Console після запуску. '
            'Позиції в Google не обнуляємо «сайтом з нуля».'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 3,
        'title': 'Ліди в Telegram / Email',
        'body': (
            'Форми на HTMX надсилають заявки без перезавантаження сторінки '
            'у Telegram, CRM або на Email.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 4,
        'title': 'Термін реалізації',
        'body': 'Розробка корпоративного сайту — до 30 днів. Конфіденційність гарантована.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й етап: 50% (Передоплата)',
        'body': (
            'Вноситься перед стартом розробки після затвердження ТЗ, '
            'початку прототипування та дизайн-концепції сайту.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й етап: 50% (Фінальний платіж)',
        'body': (
            'Вноситься після фінального тестування, демонстрації '
            'працездатності, перед деплоєм та передачею всіх доступів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без конструкторів WordPress / Tilda',
        'body': (
            'Чистий код на Django, а не шаблон з платними плагінами. '
            'Сайт належить вам: немає підписок на конструктор і зайвого коду, '
            'який ламається після оновлень ядра CMS.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Ліди через HTMX, не через важкий JS-бандл',
        'body': (
            'Заявка йде без перезавантаження сторінки й без SPA-фреймворка. '
            'Менше скриптів — стабільніший PageSpeed і простіше ловити спам на сервері.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'Контент правите в Django-адмінці',
        'body': (
            'Тексти, банери й контакти — у кастомній панелі, не в коді. '
            'Інакше кожна зміна «два слова на головній» стає задачею розробника.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'Міграція URL — 301, не новий індекс з нуля',
        'body': (
            'Кожна проіндексована сторінка старого Liber отримує постійний редірект '
            'на відповідну нову. Інакше Google бачить 404, контент «зникає», '
            'і рекламний трафік сідає на порожні посадкові.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 4,
        'title': 'PageSpeed 90+ як критерій здачі',
        'body': (
            'Без зайвих скриптів конструктора сторінки відкриваються швидко — '
            'це і поведінкові фактори, і пріоритет у Google, і умова приймання.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 5,
        'title': 'Код і доступи — ваші в день здачі',
        'body': (
            'Репозиторій, сервер і Django-адмінка переходять Liber у день здачі. '
            'Немає оренди CMS і щомісячної підписки на нас, щоб сайт працював: '
            'система належить вам.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний злагоджений механізм. Ми не просто створюємо сайти — ми будуємо готові бізнес-інструменти для автоматизації процесів, залучення великих клієнтів та формування стійкого лідерського статусу вашого бренду в інтернеті.</p>
<p>Ми принципово відмовляємося від конструкторів (типу WordPress/Tilda), що перевантажують сайт зайвим кодом і роблять бізнес вразливим до зломів. Чисті кодописні рішення на перевіреній enterprise-архітектурі: <strong>Django (Python) · HTML5 · HTMX · CSS3 · Modern JavaScript</strong>.</p>
<ul>
<li><strong>Швидкість PageSpeed 90+</strong> — блискавичне відкриття сторінок без зайвих скриптів покращує поведінкові фактори й забезпечує пріоритетне ранжування в Google.</li>
<li><strong>Безпека Enterprise-рівня</strong> — вбудований захист Django від SQL-ін'єкцій, XSS, витоків даних та спам-ботів.</li>
<li><strong>Повна незалежність</strong> — немає платних плагінів, сторонніх передплат і обмежень шаблонів: система належить виключно вам.</li>
<li><strong>Безмежна масштабованість</strong> — кабінети користувачів, модулі оплати та складні інтеграції можна додати пізніше без переробки ядра.</li>
</ul>
""".strip()

GUARANTEE_HTML = """
<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється на чистому коді без нестабільних сторонніх плагінів, він не потребує постійних ризикованих оновлень, які ламають верстку.</p>
<p>Ми надаємо <strong>пожиттєву гарантію</strong> на працездатність нашого коду протягом усього періоду життя ресурсу.</p>
""".strip()

TITLE = 'Комерційна пропозиція на розробку корпоративного сайту'
LEAD = (
    'Створення надійного, високонавантаженого цифрового інструменту '
    'для формування преміального іміджу та залучення клієнтів'
)


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
    help = 'Seed Liber corporate-website commercial proposal + classic demo-corp (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_corp (для швидких тестів контенту)',
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
            f'{proposal.packages.count()} packages, '
            f'{proposal.specs.count()} specs, '
            f'{proposal.highlights.count()} highlights, '
            f'{proposal.arch_nodes.count()} arch nodes)'
        ))

    def _provision_demo(self, proposal: Proposal) -> None:
        from apps.democorp.services.provision import provision_demo_corp

        site = provision_demo_corp(proposal)
        self.stdout.write(self.style.SUCCESS(
            f'Demo: {site.get_absolute_url()} '
            f'(slug={site.slug}, catalog={site.has_catalog}, login={site.demo_login})'
        ))

    def _seed_rows(self):
        proposal, created = Proposal.objects.update_or_create(
            slug=SLUG,
            defaults={
                'client_name': 'Liber',
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
                'issued_on': date(2026, 9, 22),
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
                'corp_catalog': False,
                'is_published': True,
                'order': 1,
            },
        )

        proposal.modules.all().delete()
        for data in MODULES:
            create_with_leftovers(
                ProposalModule,
                proposal=proposal,
                **_with_ru(data, ('title', 'description')),
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
                ProposalSpec,
                proposal=proposal,
                **_with_ru(data, ('title', 'body')),
            )

        proposal.highlights.all().delete()
        for data in HIGHLIGHTS:
            create_with_leftovers(
                ProposalHighlight,
                proposal=proposal,
                **_with_ru(data, ('title',)),
            )

        proposal.arch_nodes.all().delete()
        for data in ARCH_NODES:
            create_with_leftovers(
                ProposalArchNode,
                proposal=proposal,
                **_with_ru(data, ('title', 'caption')),
            )

        _attach_hero(proposal)
        return proposal, created
