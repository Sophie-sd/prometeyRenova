"""
Management command: seed_proposal_advocate

Idempotent заливка КП «Адвокатський лендінг» (PDF 24.09.2026)
+ класичний demo-landing. Це не версія сайту клієнта.
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

SLUG = 'landing-advocate-a7f3'

RECS_LEAD = (
    'Лендінг адвоката з військового права на Django / HTMX: '
    'затримання в ТЦК, повістка, ВЛК, заявка в Telegram.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 95+'},
    {'order': 2, 'title': 'Заявка в Telegram'},
    {'order': 3, 'title': 'До 12 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Hero', 'caption': 'Ліцензія · запис', 'is_accent': False},
    {'order': 1, 'title': 'Practices', 'caption': 'ТЦК · ВЛК', 'is_accent': True},
    {'order': 2, 'title': 'Quiz', 'caption': 'Ситуація · файли', 'is_accent': False},
    {'order': 3, 'title': 'Trust', 'caption': 'Кейси · відгуки', 'is_accent': False},
    {'order': 4, 'title': 'Admin', 'caption': 'Прайс · справи', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Офер і докази',
        'description': (
            'Військове право на першому екрані: ліцензія, досвід і запис, '
            'коли людину затримали в ТЦК або вручили повістку.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Адаптивний стиль',
        'description': (
            'Стриманий інтерфейс для юридичної практики. '
            'Телефон, планшет і ПК без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Заявки в Telegram і на пошту',
        'description': (
            'Консультація і контакт доходять адвокату одразу. '
            'Форма не перезавантажує сторінку.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Адмінка прайсу і справ',
        'description': (
            'Тексти, ціни, нові справи і відгуки без програміста на кожну правку.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Аналітика конверсій',
        'description': (
            'GA4, Google Tag Manager і Meta Pixel: кліки, дзвінки і відправлені форми.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Деплой і домен',
        'description': 'Сервер, SSL, DNS і запуск.'
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Базовий',
        'scope': (
            'Лендінг на Django і HTMX, каталог послуг, форми заявок, '
            'сповіщення в Telegram або CRM, адмінка, аналітика, запуск на сервері.'
        ),
        'duration': 'до 12 днів',
        'price': Decimal('400.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Сайт + ADS',
        'scope': (
            'Усе з Базового плюс Google Ads під військове право: '
            'пошук і контекст, мінус-слова, трекінг дзвінків.'
        ),
        'duration': 'до 12 днів',
        'price': Decimal('600.00'),
        'currency': '€',
        'is_recommended': True,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Головний екран',
        'body': (
            'Адвокат з військового права, ліцензія і терміновий запис. '
            'Людина з ТЦК або з повісткою бачить, куди писати, не шукаючи меню.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Каталог ситуацій',
        'body': (
            'Затримання і доставлення в ТЦК, повістка, оновлення даних і розшук, '
            'ВЛК та оскарження висновку, відстрочка, мобілізація. '
            'Картка з вартістю, без перезавантаження сторінки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Форма ситуації',
        'body': (
            'Короткий опис і файли: повістка, постанова, висновок ВЛК. '
            'Заявка йде адвокату в Telegram, а не лишається в формі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 3,
        'title': 'Довіра і конфіденційність',
        'body': (
            'Сертифікати, відгуки довірителів і явні правила конфіденційності. '
            'Без вигаданих «виграних справ» у тексті сторінки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'PageSpeed 95+ для реклами',
        'body': (
            'Клік з Google Ads не має чекати конструктор. '
            'Швидкий перший екран тримає вартість переходу нижче.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Без чужої CMS',
        'body': (
            'Немає щомісячної підписки на конструктор і чужих плагінів. '
            'Для практики це ще й менше дірок навколо клієнтських даних.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Аванс перед проєктуванням і дизайном.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': 'Після тесту і узгодження, перед передачею доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка Базового: 4 × 100 €',
        'body': 'Чотири рівні частини без комісії, замість схеми 50/50.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 3,
        'title': 'Розстрочка «Сайт + ADS»: 4 × 150 €',
        'body': 'Чотири рівні частини без комісії, замість схеми 50/50.',
    },
]

TITLE = 'Лендінг адвоката з військового права'
LEAD = (
    'Запис, коли людину затримали в ТЦК, вручили повістку '
    'або треба оскаржити ВЛК: ситуація на екрані і заявка адвокату.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає лендінг під одну практику — військове право. Людина в стресі має побачити свою ситуацію і залишити заявку, не гортаючи загальний каталог послуг.</p>
<p>Стек: <strong>Django (Python) · HTML5 · CSS3 · HTMX · JavaScript · PostgreSQL</strong>. Без конструктора і без щомісячної підписки на CMS.</p>
<ul>
<li><strong>PageSpeed 95+</strong> — клік з реклами відкривається одразу, поки людина ще на зв’язку.</li>
<li><strong>HTMX</strong> — картки ТЦК, повістки і ВЛК та форма працюють без повного перезавантаження.</li>
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
    help = 'Seed advocate landing proposal + classic demo-landing (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без provision_demo_landing',
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
        from apps.demolanding.models import LandingSite
        from apps.demolanding.services.provision import provision_demo_landing

        site = LandingSite.objects.filter(proposal=proposal).first()
        if site is None:
            site = LandingSite(
                proposal=proposal,
                name='Demo Landing',
                slug=LandingSite.generate_slug('advocate'),
            )
            site.save()
        site = provision_demo_landing(proposal)
        if site.name != 'Demo Landing':
            site.name = 'Demo Landing'
            site.save(update_fields=['name'])
        self.stdout.write(self.style.SUCCESS(
            f'Demo: {site.get_absolute_url()} (slug={site.slug})'
        ))

    def _seed_rows(self):
        proposal, created = Proposal.objects.update_or_create(
            slug=SLUG,
            defaults={
                'client_name': 'Військове право',
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
                'issued_on': date(2026, 9, 24),
                'intro_html': INTRO_HTML,
                'intro_html_ru': translate_ua_to_ru(INTRO_HTML),
                'intro_html_en': '',
                'intro_html_cs': '',
                'guarantee_html': GUARANTEE_HTML,
                'guarantee_html_ru': translate_ua_to_ru(GUARANTEE_HTML),
                'guarantee_html_en': '',
                'guarantee_html_cs': '',
                'cta_label': 'Почати проєкт',
                'cta_label_ru': translate_ua_to_ru('Почати проєкт'),
                'cta_label_en': '',
                'cta_label_cs': '',
                'kind': Proposal.DemoKind.LANDING,
                'corp_catalog': False,
                'is_published': True,
                'order': 9,
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
