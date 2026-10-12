"""HTMX-ендпоінти меблевого демо: перемикання ціни, «Купити в 1 клік», консультація.

Нічого не відправляється: це демо. Усе 404, якщо магазин не в furniture_mode.
"""
import re

from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from . import furniture
from .catalog_models import ShopProduct
from .models import DemoShop

MIN_PHONE_DIGITS = 9
MAX_NAME_LEN = 120
MAX_NOTE_LEN = 500


def _furniture_shop(shop_slug: str) -> DemoShop:
    shop = get_object_or_404(DemoShop, slug=shop_slug, is_active=True)
    if not shop.furniture_mode:
        raise Http404
    return shop


def _clean_contact(post):
    name = re.sub(r'\s+', ' ', post.get('name', '')).strip()[:MAX_NAME_LEN]
    phone = post.get('phone', '').strip()[:32]
    digits = sum(ch.isdigit() for ch in phone)
    return name, phone, digits >= MIN_PHONE_DIGITS


def _result(request, shop, ok: bool, kind: str):
    return render(request, 'demoshop/partials/_furniture_form_result.html', {
        'shop': shop,
        'ok': ok,
        'kind': kind,
    })


@require_GET
def price_switch(request, shop_slug, product_slug):
    shop = _furniture_shop(shop_slug)
    product = get_object_or_404(ShopProduct, shop=shop, is_active=True, slug=product_slug)
    selection = furniture.selection_from(request.GET, product)
    resolved = furniture.resolve(product, selection)
    return render(request, 'demoshop/partials/_furniture_price.html', {
        'shop': shop,
        'product': product,
        'variant_price': resolved['unit_price'],
        'variant_label': resolved['label'],
    })


@require_POST
def quick_buy(request, shop_slug):
    shop = _furniture_shop(shop_slug)
    name, _phone, phone_ok = _clean_contact(request.POST)
    return _result(request, shop, bool(name) and phone_ok, 'quick')


@require_POST
def consult(request, shop_slug):
    shop = _furniture_shop(shop_slug)
    name, _phone, phone_ok = _clean_contact(request.POST)
    return _result(request, shop, bool(name) and phone_ok, 'consult')
