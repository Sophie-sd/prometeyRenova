"""
Management command: seed_proposal_locks

Idempotent заливка КП «Замки та фурнітура» (PDF 18.09.2026)
+ класичний demo-shop. Це не версія сайту клієнта.
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

SLUG = 'shop-locks-a7f3'

RECS_LEAD = (
    'Інтернет-магазин замків і дверної фурнітури на Django / HTMX: '
    'бексет, клас зламостійкості і оформлення в один клік.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Django / HTMX'},
    {'order': 1, 'title': 'PageSpeed 90+'},
    {'order': 2, 'title': 'Нова Пошта'},
    {'order': 3, 'title': '30 днів'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Admin', 'caption': 'Прайс · залишки', 'is_accent': False},
    {'order': 1, 'title': 'Catalog', 'caption': 'Бексет · клас', 'is_accent': False},
    {'order': 2, 'title': 'Card', 'caption': 'Схема · колір', 'is_accent': True},
    {'order': 3, 'title': 'Delivery', 'caption': 'Відділення · ТТН', 'is_accent': False},
    {'order': 4, 'title': 'Pay', 'caption': 'Картка · рахунок', 'is_accent': False},
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'UI/UX під телефон і ПК',
        'description': (
            'Ергономічний інтерфейс для підбору замка. '
            'Телефон, планшет і десктоп, без окремої мобільної шкіри.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Каталог і живий пошук',
        'description': (
            'Фільтри за типом монтажу, бексетом, міжосьовою відстанню, '
            'вильотом ригеля, матеріалом, кольором, класом зламостійкості і брендом.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Кошик і доставка',
        'description': (
            'Оформлення без довгої форми. Відділення пошти підставляється в замовлення. '
            '«Купити в 1 клік» — лише номер телефону.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Оплата карткою',
        'description': 'LiqPay, WayForPay або Monobank. Рахунок і ТТН формуються при оформленні.',
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Адмінка залишків і прайсу',
        'description': (
            'Асортимент, ціни, залишки і замовлення без програміста. '
            'Оновлення цін з Excel або CSV.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Аналітика і SEO-база',
        'description': (
            'Рекламні пікселі, вебаналітика і структура під пошук. '
            'Сповіщення менеджера про замовлення в Telegram.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'Інтернет-магазин під ключ',
        'scope': (
            'Ніша: замки та фурнітура. UI/UX, каталог з фільтрами, адмінка залишків, '
            'оплата карткою, пошта, SEO-база, аналітика, деплой і домен.'
        ),
        'duration': '30 днів',
        'price': Decimal('900.00'),
        'currency': '€',
        'is_recommended': False,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Каталог замків і фурнітури',
        'body': (
            'Врізні, накладні, навісні й електромеханічні замки. '
            'Циліндри, ключі, ручки, броненакладки, петлі, доводчики і розсувні системи.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'Фільтр під сумісність',
        'body': (
            'Монтаж, бексет, міжосьова відстань, виліт ригеля, покриття, '
            'клас зламостійкості і виробник. Покупець звужує прайс, а не вгадує розмір.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Картка з кресленням',
        'body': (
            'Габаритна сітка, монтажна схема і таблиця специфікації. '
            'Колір або розмір міняє ціну на картці. Поруч — супутнє: броненакладка до цього замка.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Без OpenCart і WordPress',
        'body': (
            'Платні модулі фільтрів гальмують каталог і ламаються на оновленнях. '
            'Підписок на плагіни немає: прайс і залишок у своєму коді.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'PageSpeed 90+ на рекламі',
        'body': (
            'Наплив з кампанії не має класти картку замка. '
            '90+ на телефоні й ПК — умова здачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж: 50% — 450 €',
        'body': 'Перед стартом: фіксує термін і запускає проєктування інтерфейсу.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж: 50% — 450 €',
        'body': 'Після тесту і узгодження, перед деплоєм і передачею доступів.',
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 2,
        'title': 'Розстрочка до 5 платежів',
        'body': 'Без відсотків, від 180 € на місяць. Переплати немає.',
    },
]

TITLE = 'Інтернет-магазин замків та фурнітури під ключ'
LEAD = (
    'Швидкий магазин систем безпеки: врізні й накладні замки, '
    'циліндри, ручки і броненакладки з підбором за розміром.'
)

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> збирає інструмент продажів для замків і фурнітури: середній чек, точний підбір модифікації і замовлення без конструктора.</p>
<p>Стек: <strong>Django (Python) · HTML5 · HTMX · CSS3 · JavaScript</strong>. Без WordPress і OpenCart — їхні модулі фільтрів гальмують каталог.</p>
<ul>
<li><strong>PageSpeed 90+</strong> — картка відкривається одразу, пошук не віддає пріоритет повільній вітрині.</li>
<li><strong>Сумісність</strong> — бексет, міжосьова і клас зламостійкості фільтруються на сервері, не в описі.</li>
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
    help = 'Seed locks-and-hardware shop proposal + classic demo-shop (idempotent)'

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
                slug=DemoShop.generate_slug('locks'),
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
                'client_name': 'Замки та фурнітура',
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
                'issued_on': date(2026, 9, 18),
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
                'order': 10,
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
