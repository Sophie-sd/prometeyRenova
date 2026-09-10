"""Пересіяти контент demo-лендінгів. Ідемпотентно — безпечно запускати повторно."""
from django.core.management.base import BaseCommand

from apps.demolanding.models import LandingSite
from apps.demolanding.seed import seed_demo_landing


class Command(BaseCommand):
    help = 'Пересіяти seed-контент demo-лендінгів (--slug — лише один)'

    def add_arguments(self, parser):
        parser.add_argument('--slug', default='', help='slug конкретного лендінгу')

    def handle(self, *args, **options):
        qs = LandingSite.objects.all()
        if options['slug']:
            qs = qs.filter(slug=options['slug'])
        count = 0
        for site in qs:
            seed_demo_landing(site)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Пересіяно {count} лендінг(ів).'))
