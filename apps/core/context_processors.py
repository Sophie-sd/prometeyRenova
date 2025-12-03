"""
Context processors для глобальних змінних шаблонів
"""
from django.conf import settings


def global_settings(request):
    """
    Додає глобальні налаштування до контексту всіх шаблонів
    """
    return {
        'FACEBOOK_PIXEL_ID': getattr(settings, 'FACEBOOK_PIXEL_ID', None),
        'DEBUG': settings.DEBUG,
    }

