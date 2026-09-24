"""
Management command: seed_proposal_sanitary

Idempotent заливка КП «Санітарна обробка» (PDF 24.09.2026)
+ класичний demo-corp. Це не версія сайту клієнта.
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

SLUG = 'corporate-sanitary-a7f3'

RECS_LEAD = (
    'Корпоративний сайт служби санітарної обробки: Django / HTMX, '
    'заявка без перезавантаження, PageSpeed 90+.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Заявка зі смартфона'},
    {'order': 3, 'title': 'До 20 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Home', 'caption': 'Виклик фахівця', 'is_accent': False},
    {'order': 1, 'title': 'Services', 'caption': 'Дезінфекція · гризуни', 'is_accent': True},
    {'order': 2, 'title': 'Trust', 'caption': 'Ліцензії · відгуки', 'is_accent': False},
    {'order': 3, 'title': 'Leads', 'caption': 'Форма · Telegram', 'is_accent': False},
    {'order': 4, 'title': 'Admin', 'caption': 'Ціни · статті', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX під смартфон і ПК',
        'description': (
            'Інтерфейс для преміальної подачі послуг. '
            'Телефон, планшет і десктоп, без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Сторінки послуг',
        'description': (
            'Дезінфекція, дезінсекція, дератизація, пліснява і запахи. '
            'Процес робіт і безпека для людей і тварин — на своїй сторінці.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Заявка без перезавантаження',
        'description': (
            'Форма виклику фахівця на HTMX. Сповіщення в Telegram, CRM або на пошту.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Довіра: ліцензії, кейси, блог',
        'description': (
            'Блоки про компанію, сертифікати, об’єкти і статті. '
            'Ціни, договори і відгуки — на сайті, не в месенджері.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Адмінка цін і послуг',
        'description': (
            'Ціни, статті і тексти послуг без розробника на кожну правку.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Реклама і запуск',
        'description': (
            'Google Analytics 4, Meta Pixel, базова SEO-структура, '
            'сервер, SSL і домен.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Односторінковий лендінг',
        'scope': (
            'Одна конверсійна сторінка під контекст: блоки послуг і переваг, '
            'форма виклику дезінфектора, базова SEO-розмітка.'
        ),
        'duration': 'до 10 днів',
        'price': Decimal('350.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'Корпоративний сайт',
        'scope': (
            'Багато сторінок для B2B і B2C, адмінка Django, блог для органіки, '
            'каталог препаратів, сповіщення в Telegram або CRM, деплой на сервер.'
        ),
        'duration': 'до 20 днів',
        'price': Decimal('500.00'),
        'currency': '€',
        'is_recommended': True,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Напрямки обробки',
        'body': (
            'Комахи, гризуни, пліснява, запахи. На кожному напрямку — '
            'як проходить робота і чим це безпечно для людей і тварин.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Виклик фахівця',
        'body': (
            'Коротка форма. Заявка одразу йде в Telegram, '
            'щоб диспетчер відповів, поки клієнт ще на сайті.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Сертифікати, ціни, відгуки',
        'body': (
            'Ліцензії, договори, гарантія на роботи, прайс і відгуки. '
            'Клієнт бачить це до дзвінка, не після.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Заявка з телефона в аварії',
        'body': (
            'Екстрений виклик майже завжди зі смартфона. '
            'Сторінка має відкритись і відправити форму без очікування.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Без WordPress і Tilda',
        'body': (
            'Конструктор гальмує рекламу і тримає сайт на чужій підписці. '
            'Django і HTMX — ваш код, без платних плагінів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'PageSpeed 90+',
        'body': (
            'Швидка сторінка знижує ціну кліка і не втрачає людину, '
            'яка шукає обробку просто зараз.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50%',
        'body': 'Перед стартом: архітектура і UI/UX.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50%',
        'body': (
            'Після показу робочого сайту і тесту форм, '
            'перед деплоєм і передачею доступів.'
        ),
    },
]

TITLE = 'Сайт служби санітарної обробки під ключ'
LEAD = (
    'Канал заявок на дезінфекцію, дезінсекцію і дератизацію '
    'для приватних клієнтів і бізнесу.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає сайт, який приймає виклик: послуга, довіра і форма — без конструктора.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без WordPress і Tilda, без підписок на плагіни.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — сторінка встигає відкритись, поки людина ще шукає обробку.</li>
<li><strong>B2B і B2C</strong> — окремі напрямки для квартири і для об’єкта, одна адмінка.</li>
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
    help = 'Seed sanitary corporate proposal + classic demo-corp (idempotent)'

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

        site = CorpSite.objects.filter(proposal=proposal).first()
        if site is None:
            site = CorpSite(
                proposal=proposal,
                name='Demo Site',
                slug=CorpSite.generate_slug('sanitary'),
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
                'client_name': 'Служба санітарної обробки',
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
                'cta_label': 'Обговорити проєкт',
                'cta_label_ru': 'Обсудить проект',
                'cta_label_en': '',
                'cta_label_cs': '',
                'kind': Proposal.DemoKind.CORPORATE,
                'corp_catalog': False,
                'is_published': True,
                'order': 8,
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
