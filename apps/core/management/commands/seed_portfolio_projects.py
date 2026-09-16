"""
Ідемпотентне наповнення портфоліо з static-зображень.

Після деплою: python manage.py migrate && python manage.py seed_portfolio_projects
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.core.models import PortfolioProject
from apps.core.portfolio_i18n import PORTFOLIO_I18N_CS, PORTFOLIO_I18N_EN
from apps.core.portfolio_i18n_common import integrations_ru_for
from apps.core.portfolio_seed_data import IMAGE_FIELD_MAP, PORTFOLIO_PROJECTS


class Command(BaseCommand):
    help = 'Створює або оновлює проєкти портфоліо з поточного static-контенту'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-images',
            action='store_true',
            help='Перезаписати зображення навіть якщо вже завантажені',
        )
        parser.add_argument(
            '--prune',
            action='store_true',
            help='Видалити проєкти, яких немає у поточному PORTFOLIO_PROJECTS',
        )

    def handle(self, *args, **options):
        force_images = options['force_images']
        static_root = Path(settings.BASE_DIR) / 'static'
        created = 0
        updated = 0

        seed_slugs = {item['slug'] for item in PORTFOLIO_PROJECTS}

        for item in PORTFOLIO_PROJECTS:
            slug = item['slug']
            en = PORTFOLIO_I18N_EN.get(slug) or {}
            cs = PORTFOLIO_I18N_CS.get(slug) or {}
            uk_tags = item.get('integrations', '')
            defaults = {
                'title': item['title'],
                'title_ru': item.get('title_ru', ''),
                'title_en': en.get('title', ''),
                'title_cs': cs.get('title', ''),
                'subtitle': item.get('subtitle', ''),
                'subtitle_ru': item.get('subtitle_ru', ''),
                'subtitle_en': en.get('subtitle', ''),
                'subtitle_cs': cs.get('subtitle', ''),
                'card_description': item['card_description'],
                'card_description_ru': item.get('card_description_ru', ''),
                'card_description_en': en.get('card_description', ''),
                'card_description_cs': cs.get('card_description', ''),
                'integrations': uk_tags,
                'integrations_ru': integrations_ru_for(uk_tags),
                'integrations_en': en.get('integrations', ''),
                'integrations_cs': cs.get('integrations', ''),
                'card_image_alt': item.get('card_image_alt', ''),
                'card_image_alt_ru': item.get('card_image_alt_ru', ''),
                'card_image_alt_en': en.get('card_image_alt', ''),
                'card_image_alt_cs': cs.get('card_image_alt', ''),
                'site_url': item.get('site_url', ''),
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

        pruned = 0
        if options['prune']:
            stale = PortfolioProject.objects.exclude(slug__in=seed_slugs)
            pruned = stale.count()
            stale.delete()

        hidden = (
            PortfolioProject.objects.exclude(slug__in=seed_slugs)
            .filter(show_on_portfolio=True)
            .count()
        )
        PortfolioProject.objects.exclude(slug__in=seed_slugs).update(
            show_on_portfolio=False,
            show_on_homepage=False,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Портфоліо: створено {created}, оновлено {updated}, видалено {pruned}, '
                f'сховано застарілих {hidden}, '
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
