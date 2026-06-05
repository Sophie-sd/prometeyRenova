"""
Ідемпотентне наповнення клієнтів для секції «Наші клієнти».

Після деплою: python manage.py migrate && python manage.py seed_clients
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.core.models import Client
from apps.core.portfolio_seed_data import PORTFOLIO_PROJECTS


class Command(BaseCommand):
    help = 'Створює або оновлює клієнтів на головній з поточного static-контенту'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-images',
            action='store_true',
            help='Перезаписати логотипи навіть якщо вже завантажені',
        )

    def handle(self, *args, **options):
        force_images = options['force_images']
        static_root = Path(settings.BASE_DIR) / 'static'
        created = 0
        updated = 0

        for item in PORTFOLIO_PROJECTS:
            if not item.get('show_on_homepage'):
                continue

            name = (item.get('home_story_label') or item['title']).strip()
            defaults = {
                'order': item.get('home_order', 0),
                'is_active': True,
            }
            client, was_created = Client.objects.get_or_create(
                name=name,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                for key, value in defaults.items():
                    setattr(client, key, value)
                updated += 1

            self._attach_logo(client, item, static_root, force_images)
            client.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Клієнти: створено {created}, оновлено {updated}, '
                f'всього {Client.objects.count()} записів.'
            )
        )

    def _attach_logo(self, client, item, static_root, force_images):
        rel_path = item.get('static_home') or ''
        if not rel_path:
            return
        if client.logo and not force_images:
            media_path = Path(settings.MEDIA_ROOT) / client.logo.name
            if media_path.is_file():
                return
        full_path = static_root / rel_path
        if not full_path.is_file():
            self.stdout.write(
                self.style.WARNING(f'Файл не знайдено: {full_path}')
            )
            return
        with full_path.open('rb') as handle:
            client.logo.save(full_path.name, File(handle), save=False)
