"""Динамічний CSS override кольорів демо-магазину (без деплою, без inline style).

Патерн — theme_switcher_skill: статичні дефолти лишаються в demoshop_tokens.css,
цей endpoint віддає лише переозначені (непорожні) токени, каскад вирішує порядок
підключення `<link>`, не специфічність і не `!important`.
"""
from django.core.cache import cache

from .models import DemoShop, theme_css_cache_key

CACHE_TTL = 3600


def render_theme_css(shop: DemoShop) -> str:
    cached = cache.get(theme_css_cache_key(shop.pk))
    if cached is not None:
        return cached

    overrides = [
        f'  {var}: {getattr(shop, field)};'
        for field, var in DemoShop.TOKEN_MAP.items()
        if getattr(shop, field)
    ]
    css = ':root {\n' + '\n'.join(overrides) + '\n}\n' if overrides else '/* defaults */\n'
    cache.set(theme_css_cache_key(shop.pk), css, CACHE_TTL)
    return css
