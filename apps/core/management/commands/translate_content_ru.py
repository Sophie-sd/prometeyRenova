"""
Fill empty *_ru fields for portfolio, feature blocks and blog posts.
"""
from django.core.management.base import BaseCommand

from apps.blog.models import BlogPost
from apps.core.i18n_content import translate_ua_to_ru
from apps.core.models import PortfolioFeatureBlock, PortfolioProject


class Command(BaseCommand):
    help = 'Auto-translate UA database content into empty *_ru fields.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without saving.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing *_ru values.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        updated = 0

        def should_translate(ua_value: str, ru_value: str) -> bool:
            return bool(ua_value.strip()) and (force or not ru_value.strip())

        for project in PortfolioProject.objects.all():
            changed = False
            field_pairs = (
                ('title', 'title_ru'),
                ('subtitle', 'subtitle_ru'),
                ('card_description', 'card_description_ru'),
                ('modal_content', 'modal_content_ru'),
                ('home_story_label', 'home_story_label_ru'),
                ('card_image_alt', 'card_image_alt_ru'),
            )
            for ua_field, ru_field in field_pairs:
                ua_value = getattr(project, ua_field, '') or ''
                ru_value = getattr(project, ru_field, '') or ''
                if should_translate(ua_value, ru_value):
                    translated = translate_ua_to_ru(ua_value)
                    setattr(project, ru_field, translated)
                    changed = True
            if changed:
                updated += 1
                if dry_run:
                    self.stdout.write(f'[dry-run] PortfolioProject #{project.pk}: {project.title}')
                else:
                    project.save()

        for block in PortfolioFeatureBlock.objects.all():
            changed = False
            for ua_field, ru_field in (('title', 'title_ru'), ('text', 'text_ru')):
                ua_value = getattr(block, ua_field, '') or ''
                ru_value = getattr(block, ru_field, '') or ''
                if should_translate(ua_value, ru_value):
                    setattr(block, ru_field, translate_ua_to_ru(ua_value))
                    changed = True
            if changed:
                updated += 1
                if dry_run:
                    self.stdout.write(f'[dry-run] PortfolioFeatureBlock #{block.pk}: {block.title}')
                else:
                    block.save()

        for post in BlogPost.objects.all():
            changed = False
            for ua_field, ru_field in (
                ('title', 'title_ru'),
                ('excerpt', 'excerpt_ru'),
                ('content', 'content_ru'),
                ('keywords', 'keywords_ru'),
            ):
                ua_value = getattr(post, ua_field, '') or ''
                ru_value = getattr(post, ru_field, '') or ''
                if should_translate(ua_value, ru_value):
                    setattr(post, ru_field, translate_ua_to_ru(ua_value))
                    changed = True
            if changed:
                updated += 1
                if dry_run:
                    self.stdout.write(f'[dry-run] BlogPost #{post.pk}: {post.title[:60]}')
                else:
                    post.save()

        suffix = ' (dry-run)' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} records{suffix}.'))
