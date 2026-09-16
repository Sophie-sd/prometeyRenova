"""
Ідемпотентне наповнення портфоліо з static-зображень.

Після деплою: python manage.py migrate && python manage.py seed_portfolio_projects
"""
import json
import time
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import connection, IntegrityError

from apps.core.legacy_schema import ensure_leftover_not_null_defaults
from apps.core.models import PortfolioProject
from apps.core.portfolio_seed_data import IMAGE_FIELD_MAP, PORTFOLIO_PROJECTS

# #region agent log
_DEBUG_LOG = Path('/Users/sofiadmitrenko/prometeyRenova/.cursor/debug-104b19.log')


def _agent_log(hypothesis_id, location, message, data):
    payload = {
        'sessionId': '104b19',
        'hypothesisId': hypothesis_id,
        'location': location,
        'message': message,
        'data': data,
        'timestamp': int(time.time() * 1000),
    }
    try:
        with _DEBUG_LOG.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + '\n')
    except OSError:
        pass
    print(f'[debug-104b19] {hypothesis_id} {message} {data}', flush=True)
# #endregion


class Command(BaseCommand):
    help = 'Створює або оновлює проєкти портфоліо з поточного static-контенту'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-images',
            action='store_true',
            help='Перезаписати зображення навіть якщо вже завантажені',
        )

    def _table_columns(self):
        table = PortfolioProject._meta.db_table
        with connection.cursor() as cursor:
            descriptions = connection.introspection.get_table_description(
                cursor, table
            )
        return {
            col.name: {
                'null_ok': getattr(col, 'null_ok', None),
                'internal_size': getattr(col, 'internal_size', None),
            }
            for col in descriptions
        }

    def _not_null_columns(self, columns):
        return [
            name for name, meta in columns.items()
            if name != 'id' and not meta.get('null_ok')
        ]

    def _ensure_stub_row(self, slug, defaults, columns, model_fields):
        """
        After a code rollback the DB can still have later NOT NULL columns
        (site_url, *_en, *_cs) that the ORM no longer knows about. INSERT then
        sends NULL and Postgres/SQLite abort. Pre-insert a stub with ''/defaults.
        """
        if PortfolioProject.objects.filter(slug=slug).exists():
            return 'exists'
        not_null = self._not_null_columns(columns)
        extra = [c for c in not_null if c not in model_fields]
        if not extra:
            return 'no-extra-not-null'
        from django.utils import timezone

        now = timezone.now()
        values = []
        for col in not_null:
            if col == 'slug':
                values.append(slug)
            elif col in defaults:
                values.append(defaults[col])
            elif col in ('created_at', 'updated_at'):
                values.append(now)
            else:
                values.append('')
        qn = connection.ops.quote_name
        table = qn(PortfolioProject._meta.db_table)
        col_sql = ', '.join(qn(c) for c in not_null)
        placeholders = ', '.join(['%s'] * len(not_null))
        if connection.vendor == 'postgresql':
            sql = (
                f'INSERT INTO {table} ({col_sql}) VALUES ({placeholders}) '
                f'ON CONFLICT ({qn("slug")}) DO NOTHING'
            )
        else:
            sql = f'INSERT OR IGNORE INTO {table} ({col_sql}) VALUES ({placeholders})'
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
        return 'stub-inserted'

    def handle(self, *args, **options):
        force_images = options['force_images']
        static_root = Path(settings.BASE_DIR) / 'static'
        created = 0
        updated = 0
        model_fields = [f.name for f in PortfolioProject._meta.local_concrete_fields]
        columns = self._table_columns()
        extra_not_null = [
            c for c in self._not_null_columns(columns)
            if c not in model_fields
        ]
        defaulted = ensure_leftover_not_null_defaults(PortfolioProject)
        # #region agent log
        _agent_log(
            'A',
            'seed_portfolio_projects.py:handle',
            'schema-vs-model',
            {
                'vendor': connection.vendor,
                'has_site_url_column': 'site_url' in columns,
                'has_site_url_model': 'site_url' in model_fields,
                'site_url_null_ok': (columns.get('site_url') or {}).get('null_ok'),
                'extra_not_null': extra_not_null[:20],
                'defaulted': defaulted,
                'seed_slugs': [item['slug'] for item in PORTFOLIO_PROJECTS],
            },
        )
        # #endregion

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
            exists_before = PortfolioProject.objects.filter(slug=slug).exists()
            stub = self._ensure_stub_row(slug, defaults, columns, model_fields)
            # #region agent log
            _agent_log(
                'B',
                'seed_portfolio_projects.py:get_or_create',
                'before-upsert',
                {'slug': slug, 'exists_before': exists_before, 'stub': stub},
            )
            # #endregion
            try:
                project, was_created = PortfolioProject.objects.get_or_create(
                    slug=slug,
                    defaults=defaults,
                )
            except IntegrityError as exc:
                # #region agent log
                _agent_log(
                    'C',
                    'seed_portfolio_projects.py:get_or_create',
                    'integrity-error',
                    {'slug': slug, 'error': str(exc)[:400]},
                )
                # #endregion
                raise
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
        # #region agent log
        _agent_log(
            'E',
            'seed_portfolio_projects.py:handle',
            'seed-complete',
            {'created': created, 'updated': updated},
        )
        # #endregion

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
