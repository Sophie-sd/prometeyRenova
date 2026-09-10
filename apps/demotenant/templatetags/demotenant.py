"""Template-теги для читання CMS-блоків тенанта у шаблонах.

Використання: `{% tenant_text tenant "home" "hero_title" REGISTRY %}` — але
реєстр різний на кожну app, тож теги приймають `blocks_map` (виставляється
у view через `request.blocks_map = get_blocks_map(tenant)`) і локальний
`REGISTRY`, переданий з контексту (`{{ registry }}`) або через `simple_tag`
з явним аргументом. Тут — низькорівневі обгортки над `apps.demotenant.content`.
"""
from django import template

from apps.demotenant.content import get_image_url, get_text, is_visible

register = template.Library()


@register.simple_tag
def tenant_text(blocks_map, registry, page, key):
    return get_text(blocks_map, registry, page, key)


@register.simple_tag
def tenant_image(blocks_map, page, key):
    return get_image_url(blocks_map, page, key)


@register.simple_tag
def tenant_visible(blocks_map, page, key, default=True):
    return is_visible(blocks_map, page, key, default=default)


@register.filter
def tel_href(value):
    raw = (value or '').strip()
    digits = ''.join(ch for ch in raw if ch.isdigit())
    if not digits:
        return ''
    if raw.startswith('+'):
        return '+' + digits
    return digits
