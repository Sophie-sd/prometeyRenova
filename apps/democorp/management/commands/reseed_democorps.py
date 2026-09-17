"""Пересіяти контент demo-корпоративних сайтів. Ідемпотентно."""
from django.core.management.base import BaseCommand

from apps.democorp.models import CorpSite
from apps.democorp.seed import seed_demo_corp


class Command(BaseCommand):
    help = 'Пересіяти seed-контент demo-корпоративних сайтів (--slug, --reset-defaults, --refresh-images)'

    def add_arguments(self, parser):
        parser.add_argument('--slug', default='', help='slug конкретного сайту')
        parser.add_argument(
            '--reset-defaults',
            action='store_true',
            help='Перезаписати CMS-тексти, колекції та legacy-кольори з нових дефолтів',
        )
        parser.add_argument(
            '--refresh-images',
            action='store_true',
            help='Перекласти hero / gallery / partners / about.photo / картки каталогу з static/democorp/seed без скидання текстів',
        )

    def handle(self, *args, **options):
        qs = CorpSite.objects.all()
        if options['slug']:
            qs = qs.filter(slug=options['slug'])
        reset = options['reset_defaults']
        refresh_images = options['refresh_images']
        count = 0
        for site in qs:
            seed_demo_corp(site, reset_defaults=reset, refresh_images=refresh_images)
            count += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Пересіяно {count} сайт(ів), reset_defaults={reset}, refresh_images={refresh_images}.'
            )
        )
