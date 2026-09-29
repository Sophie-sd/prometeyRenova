"""Утиліти прав доступу для Django admin (Unfold sidebar + staff-користувачі)."""
from django.contrib.auth.models import Permission

STAFF_ADMIN_APP_LABELS = ('core', 'blog', 'payment', 'demoshop', 'demolanding', 'democorp')
STAFF_ADMIN_USERNAME = 'ValeriaKornienko'
FX_PERMISSION_CODENAME = 'change_exchangeratesettings'
FX_PERMISSION_CODENAMES = (
    'add_exchangeratesettings',
    'change_exchangeratesettings',
    'delete_exchangeratesettings',
    'view_exchangeratesettings',
)


def can_manage_admin_users(request) -> bool:
    return request.user.is_superuser


def can_set_exchange_rates(request) -> bool:
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    return user.is_staff and user.has_perm(f'core.{FX_PERMISSION_CODENAME}')


def user_has_fx_grant(user) -> bool:
    if not getattr(user, 'pk', None):
        return False
    return user.user_permissions.filter(
        content_type__app_label='core',
        codename=FX_PERMISSION_CODENAME,
    ).exists()


def apply_fx_grant(user, enabled: bool) -> None:
    perm = Permission.objects.get(
        content_type__app_label='core',
        codename=FX_PERMISSION_CODENAME,
    )
    if enabled:
        user.user_permissions.add(perm)
    else:
        user.user_permissions.remove(perm)


def get_staff_admin_permissions():
    """Усі permissions для операційних розділів адмінки (без auth і без курсу)."""
    return Permission.objects.filter(
        content_type__app_label__in=STAFF_ADMIN_APP_LABELS,
    ).exclude(
        content_type__app_label='core',
        codename__in=FX_PERMISSION_CODENAMES,
    )
