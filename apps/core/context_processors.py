"""
Context processors для глобальних змінних шаблонів
"""
from django.conf import settings

from apps.core.utils import get_site_contact_settings


def global_settings(request):
    """
    Додає глобальні налаштування до контексту всіх шаблонів.
    `csp_nonce` — per-request nonce, set by CSPMiddleware.
    """
    return {
        'FACEBOOK_PIXEL_ID': getattr(settings, 'FACEBOOK_PIXEL_ID', None),
        'DEBUG': settings.DEBUG,
        'csp_nonce': getattr(request, 'csp_nonce', ''),
        'site_contact': get_site_contact_settings(),
    }

