"""
Management command: seed_proposal_sanvit

КП «Санвіт-Холдинг» (PDF 30.09.2026): корпоративний сайт з каталогом.
Демо за запитом — стандартний інтернет-магазин, не корпоративний тенант.
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

SLUG = 'corporate-sanvit-a7f3'

RECS_LEAD = (
    'Корпоративний сайт холдингу з B2B-каталогом: '
    'Django / HTMX, заявка без перезавантаження, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'B2B-каталог'},
    {'order': 3, 'title': '21 день'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Hold', 'caption': 'Напрямки', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Гурт · заявки', 'is_accent': True},
    {'order': 2, 'title': 'Lead', 'caption': 'Telegram', 'is_accent': False},
    {'order': 3, 'title': 'CMS', 'caption': 'Прайс · новини', 'is_accent': False},
    {'order': 4, 'title': 'Launch', 'caption': 'Сервер', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Структура холдингу',
        'description': (
            'Напрямки, дочірні бізнеси і виробничо-торговельні потужності '
            'на окремих сторінках, без конструктора.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог товарів і B2B-послуг',
        'description': (
            'Вітрина напрямків постачання і гуртової торгівлі. '
            'Форма швидкого замовлення специфікації, не кошик магазину.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Заявка без перезавантаження',
        'description': (
            'HTMX-форма йде в Telegram керівництва і на пошту '
            'без перезавантаження сторінки.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'CMS для контенту',
        'description': (
            'Прайс, звіти, новини і контакти філій оновлює контент-менеджер, '
            'без програміста.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Базовий сайт',
        'scope': (
            'Погоджений обсяг: до 5–7 сторінок, UI під холдинг, Django і HTMX, '
            'своя CMS, заявки в Telegram і на пошту, базова SEO, аналітика, деплой.'
        ),
        'duration': '21 робочий день',
        'price': Decimal('750.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Преміум пакет',
        'scope': (
            'Усе з Базового плюс B2B-каталог напрямків і товарів, UA/EN, '
            'CRM, карта філій, вакансії і тендери, підтримка 30 днів.'
        ),
        'duration': '30 робочих днів',
        'price': Decimal('1200.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 2,
        'name': 'Платінум пакет',
        'scope': (
            'Усе з Преміум плюс кабінет оптового партнера, синхронізація з 1С / ERP, '
            'калькулятори, SEO-аудит, AI-консультант і SLA на 3 місяці.'
        ),
        'duration': '45–60 робочих днів',
        'price': Decimal('3500.00'),
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
        'title': 'Імідж холдингу, не шаблон',
        'body': (
            'Сторінки напрямків і потужностей збираються під структуру групи, '
            'а не під універсальну тему.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Каталог лишається текстом пакета',
        'body': (
            'B2B-вітрина, CRM, кабінет партнера і AI — у Преміум і Платінум. '
            'У демо їх немає: це стандартний магазин для тесту.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед стартом: прототип, структура сторінок і схема бази.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після робочої версії на стенді, перед передачею доступів.',
    },
]

TITLE = 'Корпоративний сайт холдингу під ключ'
LEAD = (
    'Презентація напрямків, активів і гуртових послуг. '
    'Каталог зі заявкою на специфікацію — без комісії конструктора.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає корпоративний сайт для ТОВ «Санвіт-Холдинг»: напрямки групи, активи і торговельні послуги.</p>
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
    help = 'Seed Sanvit corporate catalog proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('sanvit'),
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
                'client_name': 'Санвіт-Холдинг',
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
                'issued_on': date(2026, 9, 30),
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
                'order': 19,
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
