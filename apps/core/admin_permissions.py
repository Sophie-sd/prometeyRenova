"""Утиліти прав доступу для Django admin (Unfold sidebar + staff-користувачі)."""
from django.contrib.auth.models import Permission

STAFF_ADMIN_APP_LABELS = ('core', 'blog', 'payment')
STAFF_ADMIN_USERNAME = 'ValeriaKornienko'


def can_manage_admin_users(request) -> bool:
    return request.user.is_superuser


def get_staff_admin_permissions():
    """Усі permissions для операційних розділів адмінки (без auth)."""
    return Permission.objects.filter(
        content_type__app_label__in=STAFF_ADMIN_APP_LABELS,
    )
