"""
Idempotent-команда для надання staff-доступу до операційних розділів адмінки.

Надає доступ до CRM, платежів, сайту та блогу без керування
користувачами. Суперюзерів не змінює.

ENV:
- DJANGO_STAFF_ADMIN_USERNAME (дефолт: ValeriaKornienko)

Приклад:
    python manage.py grant_staff_admin_access
    python manage.py grant_staff_admin_access --username ValeriaKornienko
    python manage.py grant_staff_admin_access --skip-missing

--skip-missing без явного --username: якщо облікового запису немає, команда
пише warning і завершується з кодом 0. Явний --username для неіснуючого
користувача завжди кидає CommandError. Наявного користувача команда як і
раніше перезаписує повним набором прав; деплой її не викликає.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.core.admin_permissions import (
    FX_PERMISSION_CODENAMES,
    STAFF_ADMIN_USERNAME,
    get_staff_admin_permissions,
)


class Command(BaseCommand):
    help = (
        'Надає staff-доступ до операційних розділів адмінки '
        '(CRM, платежі, сайт, блог). Суперюзерів не змінює.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username користувача для надання доступу',
        )
        parser.add_argument(
            '--skip-missing',
            action='store_true',
            help=(
                'Якщо --username не задано і користувача немає — warning і код 0. '
                'Явний --username для відсутнього користувача все одно дає CommandError.'
            ),
        )

    def handle(self, *args, **options):
        User = get_user_model()
        explicit_username = options.get('username') or None
        username = explicit_username or os.environ.get(
            'DJANGO_STAFF_ADMIN_USERNAME',
            STAFF_ADMIN_USERNAME,
        )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            if options['skip_missing'] and not explicit_username:
                self.stdout.write(
                    self.style.WARNING(
                        f'Користувач "{username}" не знайдений. '
                        'Надання доступу пропущено.'
                    )
                )
                return
            raise CommandError(
                f'Користувач "{username}" не знайдений. '
                'Створіть обліковий запис перед наданням доступу.'
            ) from exc

        superuser_username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        if user.is_superuser or (
            superuser_username and user.username == superuser_username
        ):
            self.stdout.write(
                self.style.WARNING(
                    f'Користувач "{username}" — суперюзер. '
                    'Деплой його не змінює.'
                )
            )
            return

        staff_permissions = get_staff_admin_permissions()
        kept_fx = list(
            user.user_permissions.filter(
                content_type__app_label='core',
                codename__in=FX_PERMISSION_CODENAMES,
            )
        )

        user.is_staff = True
        user.is_active = True
        user.save(update_fields=['is_staff', 'is_active'])

        user.user_permissions.set(list(staff_permissions) + kept_fx)

        perm_count = staff_permissions.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Staff-доступ надано користувачу "{username}":\n'
                f'   is_staff=True\n'
                f'   Призначено {perm_count} permissions (core, blog, payment)'
            )
        )
