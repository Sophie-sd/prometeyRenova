"""Permission callbacks для UNFOLD sidebar (config/settings.py).

Один callback на тип клієнта (sidebar-секції «Мій магазин»/«Мій сайт»/
«Мій лендінг») + узагальнений `is_prometey_staff`, що виключає всіх трьох.
`apps.demoshop.admin_permissions` реекспортує звідси — щоб не міняти рядки
UNFOLD, які вже посилаються на `apps.demoshop.admin_permissions.*`.
"""


def is_demo_shop_client(request) -> bool:
    if not request.user.is_authenticated:
        return False
    from apps.demoshop.models import DemoShop

    return DemoShop.objects.filter(owner_user=request.user, is_active=True).exists()


def is_demo_corp_client(request) -> bool:
    if not request.user.is_authenticated:
        return False
    try:
        from apps.democorp.models import CorpSite
    except ImportError:
        # apps.democorp з'являється у фазі 3 — до того часу просто "немає таких клієнтів".
        return False

    return CorpSite.objects.filter(owner_user=request.user, is_active=True).exists()


def is_demo_corp_catalog_client(request) -> bool:
    """Sidebar каталогу — лише якщо в клієнта `has_catalog=True`."""
    if not request.user.is_authenticated:
        return False
    try:
        from apps.democorp.models import CorpSite
    except ImportError:
        return False

    return CorpSite.objects.filter(
        owner_user=request.user, is_active=True, has_catalog=True,
    ).exists()


def is_demo_landing_client(request) -> bool:
    if not request.user.is_authenticated:
        return False
    try:
        from apps.demolanding.models import LandingSite
    except ImportError:
        # apps.demolanding з'являється у фазі 2 — до того часу просто "немає таких клієнтів".
        return False

    return LandingSite.objects.filter(owner_user=request.user, is_active=True).exists()


def is_any_demo_client(request) -> bool:
    return (
        is_demo_shop_client(request)
        or is_demo_corp_client(request)
        or is_demo_landing_client(request)
    )


def is_prometey_staff(request) -> bool:
    """Наш штат: staff-логін, який НЕ є власником жодного demo-тенанта.

    Розмежовує sidebar агенції від клієнтських секцій — без цього
    demo-клієнт (теж is_staff=True) бачив би CRM/Платежі/Сайт/Блог/Систему.
    """
    if not (request.user.is_authenticated and request.user.is_staff):
        return False
    return not is_any_demo_client(request)
