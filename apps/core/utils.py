"""Утиліти для apps.core."""
from django.core.cache import cache

from .models import SiteContactSettings

SITE_CONTACT_CACHE_KEY = 'site_contact_settings'
SITE_CONTACT_CACHE_TTL = 300

SITE_CONTACT_DEFAULTS = {
    'phone_display': '+38 (063) 952-05-65',
    'phone_e164': '380639520565',
    'email': 'prometeylabs@gmail.com',
    'instagram_url': 'https://instagram.com/prometeylabs',
    'facebook_url': 'https://facebook.com/prometeylabs',
    'linkedin_url': 'https://linkedin.com/company/prometeylabs',
    'telegram_url': 'https://t.me/prometeylabs',
}


def get_site_contact_settings():
    """Повертає singleton налаштувань контактів (кеш ~5 хв)."""
    cached = cache.get(SITE_CONTACT_CACHE_KEY)
    if cached is not None:
        return cached

    settings_obj, _created = SiteContactSettings.objects.get_or_create(
        pk=1,
        defaults=SITE_CONTACT_DEFAULTS,
    )
    cache.set(SITE_CONTACT_CACHE_KEY, settings_obj, SITE_CONTACT_CACHE_TTL)
    return settings_obj
