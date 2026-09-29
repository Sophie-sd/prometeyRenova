from django import template

from apps.core.fx import SWITCH, format_amount, format_from, format_package_price, format_range

register = template.Library()

_VARIANTS = {'light', 'dark'}


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


@register.inclusion_tag('components/currency_switcher.html', takes_context=True)
def currency_switcher(context, variant='light', region='home', oob=False):
    if variant not in _VARIANTS:
        variant = 'light'
    if region not in {'home', 'shop', 'proposal'}:
        region = 'home'
    request = context.get('request')
    codes = context.get('fx_codes') or ['EUR']
    current = context.get('fx_currency') or 'EUR'
    next_url = request.get_full_path() if request is not None else '/'
    proposal = context.get('proposal')
    choices = [
        {'code': code, 'symbol': symbol, 'current': code == current}
        for code, symbol in SWITCH
        if code in codes
    ]
    return {
        'choices': choices,
        'next': next_url,
        'variant': variant,
        'region': region,
        'oob': oob,
        'proposal_slug': getattr(proposal, 'slug', '') or '',
        'csrf_token': context.get('csrf_token'),
    }
