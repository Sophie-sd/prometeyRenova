"""Template-теги вітрини демо-магазину: CMS-тексти/фото, ideal_cols, money."""
from django import template

from apps.demoshop.content import get_image_url, get_text

register = template.Library()


@register.simple_tag
def product_img(product):
    """URL головного фото: static_image (меблі) або media/puburl; '' якщо немає."""
    from django.templatetags.static import static

    from apps.core.public_files import public_file_url

    path = (getattr(product, 'static_image', '') or '').strip()
    if path:
        return static(path)
    main = product.main_image
    if main:
        return public_file_url(main.image) or ''
    return ''


@register.simple_tag
def block_text(shop, page, key, default=''):
    return get_text(getattr(shop, 'blocks_map', {}), page, key, default)


@register.simple_tag
def block_image(shop, page, key):
    return get_image_url(getattr(shop, 'blocks_map', {}), page, key)


@register.filter
def ideal_cols(count, max_cols=4):
    """Найбільша кількість колонок ≤ max_cols без «сироти» в останньому ряді."""
    try:
        count = int(count)
        max_cols = int(max_cols)
    except (TypeError, ValueError):
        return max_cols
    if count <= 0:
        return max_cols
    if count <= max_cols:
        return count
    for cols in range(max_cols, 1, -1):
        if count % cols == 0:
            return cols
    return max_cols


@register.filter
def tel_href(value):
    """Нормалізує CMS-телефон у tel:+380... для iOS Safari."""
    raw = str(value or '')
    kept = ''.join(ch for ch in raw if ch.isdigit() or ch == '+')
    if not kept:
        return ''
    if kept.startswith('+'):
        return f'tel:{kept}'
    return f'tel:+{kept}'


@register.filter
def money(value):
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return value
    return f'{amount:,}'.replace(',', '\xa0')


@register.simple_tag(takes_context=True)
def currency_symbol(context):
    """₴ для uk/ru, Kč для cs/en."""
    request = context.get('request')
    lang = ''
    if request is not None:
        lang = getattr(request, 'LANGUAGE_CODE', '') or ''
    if not lang:
        from django.utils.translation import get_language
        lang = get_language() or 'uk'
    lang = lang.split('-')[0].lower()
    if lang in ('cs', 'en'):
        return 'Kč'
    return '₴'


# Тематичні фото для Color Wipe карток категорій (static/demoshop/seed/…)
_CATEGORY_IMAGES = {
    'електроніка': 'demoshop/seed/products/wireless-headphones.webp',
    'electronics': 'demoshop/seed/products/wireless-headphones.webp',
    'дім-і-побут': 'demoshop/seed/products/desk-lamp.webp',
    'home-living': 'demoshop/seed/products/desk-lamp.webp',
    'аксесуари': 'demoshop/seed/products/city-backpack.webp',
    'accessories': 'demoshop/seed/products/city-backpack.webp',
    'новинки': 'demoshop/seed/products/portable-speaker.webp',
    'new-arrivals': 'demoshop/seed/products/portable-speaker.webp',
    # Metal furniture B2B categories (Czech)
    'cat-metal-0': 'demoshop/seed/placeholder-metal.svg',
    'cat-metal-1': 'demoshop/seed/placeholder-metal.svg',
    'cat-metal-2': 'demoshop/seed/placeholder-metal.svg',
    'cat-metal-3': 'demoshop/seed/placeholder-metal.svg',
    'cat-metal-4': 'demoshop/seed/placeholder-metal.svg',
    'cat-metal-5': 'demoshop/seed/placeholder-metal.svg',
    'room-living': 'demoshop/seed/furniture/sofa.svg',
    'room-bedroom': 'demoshop/seed/furniture/bed.svg',
    'room-kitchen': 'demoshop/seed/furniture/dining.svg',
    'room-office': 'demoshop/seed/furniture/desk.svg',
    'room-kids': 'demoshop/seed/furniture/kidsbed.svg',
    'lavice': 'demoshop/seed/placeholder-metal.svg',
    'stoly': 'demoshop/seed/placeholder-metal.svg',
    'regály': 'demoshop/seed/placeholder-metal.svg',
    'skříně': 'demoshop/seed/placeholder-metal.svg',
    'vozíky': 'demoshop/seed/placeholder-metal.svg',
    'zdravotnický': 'demoshop/seed/placeholder-metal.svg',
}


@register.filter
def category_image(category):
    """Шлях static для тематичного фото категорії."""
    slug = (getattr(category, 'slug', '') or '').strip().lower()
    if slug in _CATEGORY_IMAGES:
        return _CATEGORY_IMAGES[slug]
    name = (getattr(category, 'name', '') or '').strip().lower()
    for key, path in _CATEGORY_IMAGES.items():
        if key in name or name in key:
            return path
    return 'demoshop/seed/products/wireless-headphones.webp'
