"""Idempotent cleanup: removes the metal-furniture proposal and its demo shop (with products/images)."""
from django.core.management.base import BaseCommand
from django.db import transaction

PROPOSAL_SLUG = 'kovovy-nabytek-7c1e'
SHOP_SLUG = 'metal-furniture-demo-7c1e'


class Command(BaseCommand):
    help = 'Delete metal-furniture proposal kovovy-nabytek-7c1e and demo shop metal-furniture-demo-7c1e (idempotent)'

    def handle(self, *args, **options):
        from apps.core.proposal_models import Proposal
        from apps.demoshop.catalog_models import ShopProductImage
        from apps.demoshop.models import DemoShop

        with transaction.atomic():
            shops = DemoShop.objects.filter(slug=SHOP_SLUG) | DemoShop.objects.filter(proposal__slug=PROPOSAL_SLUG)
            files = []
            for img in ShopProductImage.objects.filter(product__shop__in=shops):
                if img.image:
                    files.append((img.image.storage, img.image.name))
            n_shops = shops.count()
            shops.delete()
            proposals = Proposal.objects.filter(slug=PROPOSAL_SLUG)
            n_props = proposals.count()
            for p in proposals:
                if getattr(p, 'hero_image', None):
                    files.append((p.hero_image.storage, p.hero_image.name))
            proposals.delete()

        for storage, name in files:
            try:
                storage.delete(name)
            except Exception:  # noqa: BLE001 - file cleanup is best-effort
                pass
        self.stdout.write(self.style.SUCCESS(
            f'Metal-furniture cleanup: {n_props} proposal(s), {n_shops} shop(s), {len(files)} file(s) removed'
        ))
