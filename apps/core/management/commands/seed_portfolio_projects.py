"""
Ідемпотентне наповнення портфоліо з static-зображень.

Після деплою: python manage.py migrate && python manage.py seed_portfolio_projects
"""
from pathlib import Path

from django.conf import settings
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.core.models import PortfolioProject
from apps.core.portfolio_seed_data import IMAGE_FIELD_MAP, PORTFOLIO_PROJECTS


class Command(BaseCommand):
    help = 'Створює або оновлює проєкти портфоліо з поточного static-контенту'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-images',
            action='store_true',
            help='Перезаписати зображення навіть якщо вже завантажені',
        )

    def handle(self, *args, **options):
        force_images = options['force_images']
        static_root = Path(settings.BASE_DIR) / 'static'
        created = 0
        updated = 0

        for item in PORTFOLIO_PROJECTS:
            slug = item['slug']
            defaults = {
                'title': item['title'],
                'subtitle': item.get('subtitle', ''),
                'card_description': item['card_description'],
                'integrations': item.get('integrations', ''),
                'card_image_alt': item.get('card_image_alt', ''),
                'home_story_label': item.get('home_story_label', ''),
                'modal_content': item.get('modal_content', ''),
                'order': item.get('order', 0),
                'home_order': item.get('home_order', 0),
                'show_on_portfolio': item.get('show_on_portfolio', False),
                'show_on_homepage': item.get('show_on_homepage', False),
                'is_published': True,
            }
            project, was_created = PortfolioProject.objects.get_or_create(
                slug=slug,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                for key, value in defaults.items():
                    setattr(project, key, value)
                updated += 1

            self._attach_images(project, item, static_root, force_images)
            project.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Портфоліо: створено {created}, оновлено {updated}, '
                f'всього {PortfolioProject.objects.count()} записів.'
            )
        )

    def _attach_images(self, project, item, static_root, force_images):
        for static_key, field_name in IMAGE_FIELD_MAP:
            rel_path = item.get(static_key) or ''
            if not rel_path:
                continue
            field = getattr(project, field_name)
            if field and not force_images:
                media_path = Path(settings.MEDIA_ROOT) / field.name
                if media_path.is_file():
                    continue
            full_path = static_root / rel_path
            if not full_path.is_file():
                self.stdout.write(
                    self.style.WARNING(f'Файл не знайдено: {full_path}')
                )
                continue
            with full_path.open('rb') as handle:
                field.save(full_path.name, File(handle), save=False)
