"""Сесійний кошик, ізольований per-shop (ключ demoshop_cart:<shop_id>).

Ізоляція за shop_id критична: користувач може відкрити два різні демо-магазини
в одній сесії браузера (два таби), кошики не повинні змішуватись.
"""
from . import furniture
from .catalog_models import ShopProduct


def _cart_key(shop_id: int) -> str:
    return f'demoshop_cart:{shop_id}'


def get_cart(session, shop_id: int) -> dict:
    return session.get(_cart_key(shop_id), {})


def _set_cart(session, shop_id: int, cart: dict) -> None:
    session[_cart_key(shop_id)] = cart
    session.modified = True


def add_item(session, shop_id: int, product_id, qty: int = 1) -> dict:
    cart = get_cart(session, shop_id)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + max(int(qty or 1), 1)
    _set_cart(session, shop_id, cart)
    return cart


def set_qty(session, shop_id: int, product_id, qty: int) -> dict:
    cart = get_cart(session, shop_id)
    key = str(product_id)
    qty = int(qty or 0)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    _set_cart(session, shop_id, cart)
    return cart


def remove_item(session, shop_id: int, product_id) -> dict:
    cart = get_cart(session, shop_id)
    cart.pop(str(product_id), None)
    _set_cart(session, shop_id, cart)
    return cart


def clear_cart(session, shop_id: int) -> None:
    _set_cart(session, shop_id, {})


def cart_count(session, shop_id: int) -> int:
    return sum(get_cart(session, shop_id).values())


# Аліаси для views: один шар імен, без дубля логіки.
cart_add = add_item
cart_remove = remove_item
cart_set_qty = set_qty


def cart_lines(session, shop_id: int):
    cart = get_cart(session, shop_id)
    if not cart:
        return [], 0
    parsed = {key: furniture.parse_cart_key(key) for key in cart}
    ids = {pid for pid, _sel in parsed.values() if pid.isdigit()}
    products = ShopProduct.objects.filter(shop_id=shop_id, pk__in=ids, is_active=True)
    products_by_id = {str(p.pk): p for p in products}
    lines = []
    total = 0
    for key, qty in cart.items():
        pid, selection = parsed[key]
        product = products_by_id.get(pid)
        if not product:
            continue
        variant_label = ''
        unit_price = product.price
        if selection and furniture.has_variants(product):
            resolved = furniture.resolve(product, selection)
            unit_price = resolved['unit_price']
            variant_label = resolved['label']
        line_total = unit_price * qty
        total += line_total
        lines.append({
            'key': key,
            'product': product,
            'qty': qty,
            'unit_price': unit_price,
            'variant_label': variant_label,
            'line_total': line_total,
        })
    return lines, total
