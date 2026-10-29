"""
Management command: seed_proposal_furniture_shop

Idempotent заливка закритого КП «Розробка інтернет-магазину меблів під ключ»
(PDF 12.10.2026, українською) + стандартний демо-магазин (provision_demo_shop).
Це не версія сайту клієнта, а стандартне демо.
"""
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

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

from . import _furniture_shop_data as data

SLUG = data.SLUG
DEMO_TENANT_SLUG = data.DEMO_TENANT_SLUG


def _langs(payload: dict, text_keys: tuple[str, ...]) -> dict:
    """Усі мовні версії = український текст."""
    out = dict(payload)
    for key in text_keys:
        for lang in ('ru', 'en', 'cs'):
            out[f'{key}_{lang}'] = out.get(key, '')
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
    help = 'Seed furniture shop proposal + standard demo-shop (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-demo',
            action='store_true',
            help='Тільки КП, без демо-магазину',
        )

    def handle(self, *args, **options):
        from apps.core.management.commands._proposal_seed_guard import seed_must_skip
        if (skip_reason := seed_must_skip(SLUG)):
            self.stdout.write(f'Skip {SLUG}: {skip_reason}')
            return
        for model in (
            Proposal, ProposalModule, ProposalPackage,
            ProposalSpec, ProposalHighlight, ProposalArchNode,
        ):
            ensure_leftover_not_null_defaults(model)
        with transaction.atomic():
            proposal, created = self._seed_rows()
        if not options['no_demo']:
            self._provision_demo(proposal)
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action}: /proposal/{proposal.slug}/ '
            f'({proposal.modules.count()} modules, {proposal.packages.count()} packages)'
        ))

    def _provision_demo(self, proposal: Proposal) -> None:
        """Стандартний демо-магазин (як у всіх КП) через provision_demo_shop()."""
        from apps.demoshop.models import DemoShop
        from apps.demoshop.services.provision import provision_demo_shop

        shop = DemoShop.objects.filter(proposal=proposal).first()
        # Legacy custom furniture demo -> drop it and recreate as standard shop
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
        text = {
            'title': data.TITLE,
            'lead': data.LEAD,
            'recommendations_lead': data.RECS_LEAD,
            'intro_html': data.INTRO_HTML,
            'guarantee_html': data.GUARANTEE_HTML,
            'cta_label': data.CTA_LABEL,
        }
        defaults = {
            'client_name': data.CLIENT_NAME,
            'issued_on': date(2026, 10, 12),
            'kind': Proposal.DemoKind.SHOP,
            'corp_catalog': False,
            'is_published': True,
            'order': 26,
        }
        for key, value in text.items():
            defaults[key] = value
            for lang in ('ru', 'en', 'cs'):
                defaults[f'{key}_{lang}'] = value
        proposal, created = Proposal.objects.update_or_create(slug=SLUG, defaults=defaults)

        proposal.modules.all().delete()
        for row in data.MODULES:
            create_with_leftovers(
                ProposalModule, proposal=proposal, **_langs(row, ('title', 'description')),
            )
        proposal.packages.all().delete()
        for row in data.PACKAGES:
            create_with_leftovers(
                ProposalPackage, proposal=proposal,
                **_langs(row, ('name', 'scope', 'duration')),
            )
        proposal.specs.all().delete()
        for row in data.SPECS:
            create_with_leftovers(
                ProposalSpec, proposal=proposal, **_langs(row, ('title', 'body')),
            )
        proposal.highlights.all().delete()
        for row in data.HIGHLIGHTS:
            create_with_leftovers(
                ProposalHighlight, proposal=proposal, **_langs(row, ('title',)),
            )
        proposal.arch_nodes.all().delete()
        for row in data.ARCH_NODES:
            create_with_leftovers(
                ProposalArchNode, proposal=proposal, **_langs(row, ('title', 'caption')),
            )
        _attach_hero(proposal)
        return proposal, created
