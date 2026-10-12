"""Меблевий режим демо-магазину: варіанти (оббивка/колір/розмір), фільтри, ключі кошика.

Усе вмикається лише для DemoShop.furniture_mode; інші тенанти цей модуль не зачіпає.
Індекси варіантів з запиту завжди обмежуються довжиною списку (без довіри до клієнта),
ціна рахується тільки з БД.
"""
from decimal import Decimal
from urllib.parse import urlencode

from django.utils.translation import gettext as _

OPTION_GROUPS = (
    ('u', 'upholstery', 'Оббивка'),
    ('c', 'color', 'Колір'),
    ('s', 'size', 'Розмір'),
)

WIDTH_RANGES = (
    ('s', 'до 100 см', 0, 100),
    ('m', '100–160 см', 100, 160),
    ('l', '160–220 см', 160, 220),
    ('xl', 'від 220 см', 220, 10000),
)
WIDTH_BY_CODE = {code: (low, high) for code, _label, low, high in WIDTH_RANGES}

ROOMS = (
    ('living', 'Вітальня'),
    ('bedroom', 'Спальня'),
    ('kitchen', 'Кухня та їдальня'),
    ('office', 'Кабінет'),
    ('kids', 'Дитяча'),
)
ROOM_LABELS = dict(ROOMS)


def _index(raw, size: int) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return 0
    if value < 0 or value >= size:
        return 0
    return value


def get_options(product) -> dict:
    """Нормалізовані групи варіантів товару: {'upholstery': [..], ...} лише непорожні."""
    raw = getattr(product, 'variant_options', None) or {}
    if not isinstance(raw, dict):
        return {}
    out = {}
    for _param, group, _title in OPTION_GROUPS:
        items = raw.get(group)
        if isinstance(items, list) and items:
            out[group] = [item for item in items if isinstance(item, dict) and item.get('label')]
    return {group: items for group, items in out.items() if items}


def has_variants(product) -> bool:
    return bool(get_options(product))


def selection_from(data, product) -> dict:
    """Вибір {'u': i, 'c': j, 's': k} з GET/POST-словника, з обмеженням діапазону."""
    options = get_options(product)
    return {
        param: _index(data.get(param), len(options.get(group, ())) or 1)
        for param, group, _title in OPTION_GROUPS
    }


def resolve(product, selection: dict) -> dict:
    """Ціна та підпис вибраної комбінації: {'unit_price', 'label', 'parts'}."""
    options = get_options(product)
    price = Decimal(product.price)
    parts = []
    for param, group, title in OPTION_GROUPS:
        items = options.get(group)
        if not items:
            continue
        item = items[_index(selection.get(param), len(items))]
        price += Decimal(str(item.get('delta', 0) or 0))
        parts.append({'title': title, 'label': item['label']})
    label = ' · '.join(part['label'] for part in parts)
    return {'unit_price': price, 'label': label, 'parts': parts}


def option_groups(product, selection: dict) -> list:
    """Структура для шаблону перемикачів з позначкою вибраного та доплатою."""
    options = get_options(product)
    groups = []
    for param, group, title in OPTION_GROUPS:
        items = options.get(group)
        if not items:
            continue
        current = _index(selection.get(param), len(items))
        groups.append({
            'param': param,
            'key': group,
            'title': _(title),
            'items': [
                {
                    'index': idx,
                    'label': item['label'],
                    'code': str(item.get('code', '')),
                    'delta': Decimal(str(item.get('delta', 0) or 0)),
                    'checked': idx == current,
                }
                for idx, item in enumerate(items)
            ],
        })
    return groups


def cart_key(product, selection: dict) -> str:
    """Ключ рядка кошика: id для звичайних товарів, id:u:c:s для варіантних."""
    if not has_variants(product):
        return str(product.pk)
    options = get_options(product)
    idx = [
        str(_index(selection.get(param), len(options.get(group, ())) or 1))
        for param, group, _title in OPTION_GROUPS
    ]
    return f'{product.pk}:' + ':'.join(idx)


def parse_cart_key(key) -> tuple:
    """'12:1:0:2' → ('12', {'u': 1, 'c': 0, 's': 2}); '12' → ('12', {})."""
    parts = str(key).split(':')
    selection = {}
    if len(parts) == 4:
        selection = {param: parts[i + 1] for i, (param, _g, _t) in enumerate(OPTION_GROUPS)}
    return parts[0], selection


def filter_products(products, params):
    """Фільтри меблевого каталогу: кімната, колір, ширина."""
    room = params.get('room', '')
    color = params.get('color', '')
    width = params.get('width', '')
    if room in ROOM_LABELS:
        products = products.filter(room=room)
    if color:
        products = products.filter(color__iexact=color)
    if width in WIDTH_BY_CODE:
        low, high = WIDTH_BY_CODE[width]
        products = products.filter(width_cm__gte=low, width_cm__lt=high)
    return products


FILTER_KEYS = ('room', 'width', 'material', 'color')


def active_params(params) -> list:
    """Активні фільтри як пари для прихованих полів форми пошуку/сортування."""
    return [(key, params.get(key)) for key in FILTER_KEYS if params.get(key)]


def _link(base_url: str, params: dict, key: str, value: str) -> str:
    skip = {'page', key}
    if key == 'room':
        skip.add('category')
    query = {k: v for k, v in params.items() if v and k not in skip}
    if value:
        query[key] = value
    return base_url + (f'?{urlencode(query)}' if query else '')


def filter_groups(shop_products, params, base_url: str) -> list:
    """Групи чипів-фільтрів (кімната, ширина, матеріал, колір) із готовими URL."""
    present_rooms = set(shop_products.exclude(room='').values_list('room', flat=True))
    colors = sorted(set(shop_products.exclude(color='').values_list('color', flat=True)))
    materials = sorted(set(shop_products.exclude(material='').values_list('material', flat=True)))
    spec = (
        ('room', _('Кімната'), [(code, _(label)) for code, label in ROOMS if code in present_rooms]),
        ('width', _('Ширина'), [(code, _(label)) for code, label, _l, _h in WIDTH_RANGES]),
        ('material', _('Матеріал'), [(m, m) for m in materials]),
        ('color', _('Колір'), [(c, c) for c in colors]),
    )
    groups = []
    for key, title, values in spec:
        if not values:
            continue
        current = params.get(key, '')
        if key == 'room' and not current:
            current = (params.get('category', '') or '').removeprefix('room-')
        items = [{
            'label': _('Усі'),
            'url': _link(base_url, params, key, ''),
            'active': not current,
        }]
        for value, label in values:
            items.append({
                'label': label,
                'url': _link(base_url, params, key, value),
                'active': current == value,
            })
        groups.append({'key': key, 'title': title, 'items': items})
    return groups
