"""Динамічний CSS override кольорів тенанта (theme_switcher_skill).

Статичні дефолти лишаються в `*_tokens.css`; цей рендер віддає лише
переозначені (непорожні) токени, каскад підключення `<link>` вирішує
порядок, не `!important` і не специфічність.
"""
from django.core.cache import cache

CACHE_TTL = 3600


def render_theme_css(tenant) -> str:
    cache_key = tenant.theme_cache_key()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    overrides = [
        f'  {var}: {getattr(tenant, field)};'
        for field, var in tenant.TOKEN_MAP.items()
        if getattr(tenant, field)
    ]
    css = ':root {\n' + '\n'.join(overrides) + '\n}\n' if overrides else '/* defaults */\n'
    cache.set(cache_key, css, CACHE_TTL)
    return css
