"""
Management command: seed_proposal_devisu

КП DEVISU (PDF 07.10.2026): корпоративний сайт консалтингу.
Демо — стандартний корпоративний сайт із каталогом заявок, не магазин.
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

SLUG = 'corporate-devisu-a7f3'

RECS_LEAD = (
    'Корпоративний сайт DEVISU: Django / HTMX, '
    'чотири напрями консалтингу, заявка без перезавантаження, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'UA / EN'},
    {'order': 3, 'title': '25 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Audit', 'caption': 'МСФЗ · податки', 'is_accent': False},
    {'order': 1, 'title': 'Value', 'caption': 'Майно · активи', 'is_accent': True},
    {'order': 2, 'title': 'Law', 'caption': 'Супровід', 'is_accent': False},
    {'order': 3, 'title': 'Consult', 'caption': 'Фінанси', 'is_accent': False},
    {'order': 4, 'title': 'Lead', 'caption': 'Telegram', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX під послуги',
        'description': (
            'Діловий інтерфейс для преміальної презентації аудиту, оцінки і права '
            'на телефоні та ПК.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Презентація послуг',
        'description': (
            'Сторінки напрямів, форми залучення і динамічні блоки, '
            'щоб утримати корпоративного клієнта.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Лідогенерація',
        'description': (
            'HTMX-форма йде в Telegram, CRM або на пошту '
            'без перезавантаження сторінки.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Кейси, блог і аналітика',
        'description': (
            'Про компанію, портфоліо проєктів і публікації '
            'для позиціонування експертів.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Кастомна CMS',
        'description': (
            'Тексти, звіти, сертифікати і новини оновлює контент-менеджер, '
            'без програміста.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'SEO і запуск',
        'description': (
            'Базова SEO, аналітика, деплой на сервер, SSL і підключення домену.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Сайт з базовим дизайном',
        'scope': (
            'Діловий UI/UX, адаптив, каталог 4 напрямів, блог, кастомна CMS, '
            'форми лідогенерації, SEO-база та деплой.'
        ),
        'duration': '25 днів',
        'price': Decimal('600.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Сайт з авторським дизайном',
        'scope': (
            'Авторський UI/UX, інтерактивні блоки, анімація, типографіка під фірмовий стиль '
            'і всі технічні опції базового пакета.'
        ),
        'duration': '25 днів',
        'price': Decimal('800.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'PageSpeed 90+',
        'body': (
            'Сторінка без зайвого коду конструктора. '
            '90+ на телефоні й ПК — умова здачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Безпека ядра',
        'body': (
            'Django закриває SQL-ін’єкції, CSRF і XSS. '
            'Адмінка окремо від публічних сторінок.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Свій код',
        'body': (
            'Без Tilda, Wix і WordPress. '
            'Немає абонплати за плагіни і ризику, що їх вимкнуть.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Чотири напрями',
        'body': (
            'Аудит (МСФЗ, податковий), оцінка майна, правовий супровід '
            'і фінансовий консалтинг — окремі кластери, не одна сторінка.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Реєстр експертів',
        'body': (
            'Профілі аудиторів, сертифікати палати, членство в асоціаціях '
            'і блок партнерів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'UA / EN і калькулятор',
        'body': (
            'Архітектура для міжнародних клієнтів, розділ аналітики '
            'і швидкий розрахунок запиту з передачею ліда в Telegram або CRM.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед стартом: проєктування, прототип і дизайн.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після перевірки на стенді, перед деплоєм і передачею доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка 0%',
        'body': (
            'monobank або ПриватБанк, до 5 платежів. '
            'Базовий: 200 / 150 / 120 €. Авторський: 267 / 200 / 160 €.'
        ),
    },
]

TITLE = 'Корпоративний сайт консалтингової компанії під ключ'
LEAD = (
    'Аудит, оцінка, право і фінансовий консалтинг. '
    'Каталог напрямів і заявка без комісії конструктора.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає корпоративний сайт для DEVISU: аудит, оцінка майна, право і фінансовий консалтинг.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без Tilda, Wix і WordPress.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — сторінка відкривається без зайвого коду.</li>
<li><strong>Заявка</strong> — форма йде в Telegram і на пошту без перезавантаження.</li>
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
    help = 'Seed DEVISU corporate proposal + classic demo-corp (idempotent)'

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
        from apps.democorp.models import CorpSite
        from apps.democorp.services.provision import provision_demo_corp
        from apps.demoshop.models import DemoShop

        DemoShop.objects.filter(proposal=proposal).delete()
        site = CorpSite.objects.filter(proposal=proposal).first()
        if site is None:
            site = CorpSite(
                proposal=proposal,
                name='Demo Site',
                slug=CorpSite.generate_slug('devisu'),
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
                'client_name': 'DEVISU',
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
                'issued_on': date(2026, 10, 7),
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
                'order': 23,
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
