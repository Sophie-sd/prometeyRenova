"""Сесійний кошик, ізольований per-shop (ключ demoshop_cart:<shop_id>).

Ізоляція за shop_id критична: користувач може відкрити два різні демо-магазини
в одній сесії браузера (два таби), кошики не повинні змішуватись.
"""
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
    products = ShopProduct.objects.filter(shop_id=shop_id, pk__in=cart.keys(), is_active=True)
    products_by_id = {str(p.pk): p for p in products}
    lines = []
    total = 0
    for product_id, qty in cart.items():
        product = products_by_id.get(str(product_id))
        if not product:
            continue
        line_total = product.price * qty
        total += line_total
        lines.append({'product': product, 'qty': qty, 'line_total': line_total})
    return lines, total
