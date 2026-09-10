"""Ручний reseed демо-магазинів (ідемпотентно, ERR-31)."""
from django.core.management.base import BaseCommand

from apps.demoshop.models import DemoShop
from apps.demoshop.services.seed import seed_demo_shop


class Command(BaseCommand):
    help = 'Ідемпотентно наповнює активні демо-магазини мінімальним контрактом вітрини.'

    def add_arguments(self, parser):
        parser.add_argument('--slug', help='Reseed лише один магазин за slug')
        parser.add_argument(
            '--force-images',
            action='store_true',
            help='Підмінити фото товарів / hero / about зі static/demoshop/seed (CMS-тексти не чіпає)',
        )
        parser.add_argument(
            '--force-reviews',
            action='store_true',
            help='Перезаписати відгуки фіксованим seed (дублікати / шаблонні тексти)',
        )

    def handle(self, *args, **options):
        qs = DemoShop.objects.filter(is_active=True)
        slug = options.get('slug')
        if slug:
            qs = qs.filter(slug=slug)
        force_images = bool(options.get('force_images'))
        force_reviews = bool(options.get('force_reviews'))
        count = 0
        for shop in qs:
            seed_demo_shop(shop, force_images=force_images, force_reviews=force_reviews)
            count += 1
        extras = []
        if force_images:
            extras.append('force-images')
        if force_reviews:
            extras.append('force-reviews')
        suffix = f' [{", ".join(extras)}]' if extras else ''
        self.stdout.write(self.style.SUCCESS(
            f'Reseed завершено: {count} магазин(ів){suffix}.',
        ))
