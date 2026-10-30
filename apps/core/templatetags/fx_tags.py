import re

from django import template
from django.utils.translation import gettext as _

from apps.core.fx import SWITCH, format_amount, format_from, format_package_price, format_range

register = template.Library()

_VARIANTS = {'light', 'dark'}
_NAMES = {
    'EUR': 'Євро',
    'UAH': 'Гривня',
    'USD': 'Долар',
    'CZK': 'Крона',
}


def _fx(context):
    return context.get('fx_currency') or 'EUR', context.get('fx_rates')


@register.simple_tag(takes_context=True)
def fx_amount(context, amount):
    currency, rates = _fx(context)
    return format_amount(amount, currency, rates)


@register.simple_tag(takes_context=True)
def fx_range(context, low, high):
    currency, rates = _fx(context)
    return format_range(low, high, currency, rates)


@register.simple_tag(takes_context=True)
def fx_from(context, amount):
    currency, rates = _fx(context)
    return format_from(amount, currency, rates)


@register.simple_tag(takes_context=True)
def fx_package(context, package):
    currency, rates = _fx(context)
    return format_package_price(package, currency, rates)


_EUR_TXT = re.compile(r'(\d[\d\u00a0 ]*\d|\d)(?:\s?([–-])\s?(\d[\d\u00a0 ]*\d|\d))?\s?€')


@register.simple_tag(takes_context=True)
def fx_text(context, text):
    """Суми в євро всередині тексту («375–400 € передоплата») у вибраній валюті; решта тексту без змін."""
    currency, rates = _fx(context)

    def num(v):
        return int(re.sub(r'\D', '', v))

    def sub(m):
        if m.group(3):
            return format_range(num(m.group(1)), num(m.group(3)), currency, rates)
        return format_amount(num(m.group(1)), currency, rates)

    return _EUR_TXT.sub(sub, text or '')


@register.inclusion_tag('components/currency_switcher.html', takes_context=True)
def currency_switcher(context, variant='light', region='home', oob=False, slot=''):
    if variant not in _VARIANTS:
        variant = 'light'
    if region not in {'home', 'shop', 'proposal', 'soft'}:
        region = 'home'
    request = context.get('request')
    codes = context.get('fx_codes') or ['EUR']
    current = context.get('fx_currency') or 'EUR'
    next_url = request.get_full_path() if request is not None else '/'
    if request is not None and request.method == 'POST' and request.POST.get('next'):
        next_url = request.POST['next']  # OOB-перемальовка після HX: лишаємо сторінку (і мову) походження
    proposal = context.get('proposal')
    choices = [
        {
            'code': code,
            'symbol': symbol,
            'name': _(_NAMES[code]),
            'current': code == current,
        }
        for code, symbol in SWITCH
        if code in codes
    ]
    return {
        'choices': choices,
        'next': next_url,
        'variant': variant,
        'region': region,
        # slot: second switcher of the same region on one page (unique DOM id)
        'dom_id': f'{region}-{slot}' if slot else region,
        'oob': oob,
        'proposal_slug': getattr(proposal, 'slug', '') or '',
        'csrf_token': context.get('csrf_token'),
    }
