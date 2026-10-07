"""Показ комерційних цін у валюті відвідувача. База — євро."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.utils.translation import gettext as _

CURRENCY_COOKIE = 'pl_currency'
CURRENCY_COOKIE_AGE = 60 * 60 * 24 * 365

SWITCH = (
    ('EUR', '€'),
    ('UAH', '₴'),
    ('USD', '$'),
    ('CZK', 'Kč'),
)
SYMBOLS = dict(SWITCH)
RATE_FIELDS = {
    'UAH': 'uah_per_eur',
    'USD': 'usd_per_eur',
    'CZK': 'czk_per_eur',
}
EUR_MARKS = {'', '€', 'eur', 'euro'}


def load_rates():
    from apps.core.fx_models import ExchangeRateSettings

    return ExchangeRateSettings.objects.filter(pk=1).first()


def rate_for(code: str, rates) -> Decimal:
    if code == 'EUR' or rates is None:
        return Decimal('1')
    raw = getattr(rates, RATE_FIELDS.get(code, ''), None)
    if raw is None:
        return Decimal('0')
    return Decimal(raw)


def available_codes(rates=None) -> list[str]:
    codes = ['EUR']
    if rates is None:
        return codes
    for code in ('UAH', 'USD', 'CZK'):
        if rate_for(code, rates) > 0:
            codes.append(code)
    return codes


def resolve_currency(request, codes: list[str] | None = None) -> str:
    if codes is None:
        codes = available_codes(load_rates())
    raw = ''
    if request is not None:
        raw = request.COOKIES.get(CURRENCY_COOKIE, '') or ''
    code = raw.strip().upper()
    if code in codes:
        return code
    return 'EUR'


def normalize_currency(raw: str | None, rates=None) -> str:
    if rates is None:
        rates = load_rates()
    code = (raw or '').strip().upper()
    if code in available_codes(rates):
        return code
    return 'EUR'


def public_fx(request) -> dict:
    rates = load_rates()
    codes = available_codes(rates)
    return {
        'fx_currency': resolve_currency(request, codes),
        'fx_codes': codes,
        'fx_rates': rates,
    }


def _grouped(value: int) -> str:
    return f'{value:,}'.replace(',', '\u00a0')


def format_eur_number(amount) -> str:
    amount = Decimal(amount)
    if amount == amount.to_integral_value():
        return _grouped(int(amount))
    quantized = amount.quantize(Decimal('0.01'))
    whole, frac = f'{quantized:.2f}'.split('.')
    return f'{_grouped(int(whole))}.{frac}'


def convert_amount(amount, currency: str, rates) -> Decimal:
    amount = Decimal(amount)
    if currency == 'EUR':
        return amount
    rate = rate_for(currency, rates)
    if rate <= 0:
        return amount
    return (amount * rate).quantize(Decimal('1'), rounding=ROUND_HALF_UP)


def format_amount(amount, currency: str, rates) -> str:
    code = currency if currency in available_codes(rates) else 'EUR'
    if code == 'EUR':
        return f'{format_eur_number(amount)} €'
    shown = convert_amount(amount, code, rates)
    return f'{_grouped(int(shown))} {SYMBOLS[code]}'


def format_range(low, high, currency: str, rates) -> str:
    code = currency if currency in available_codes(rates) else 'EUR'
    if code == 'EUR':
        return f'{format_eur_number(low)}–{format_eur_number(high)} €'
    left = convert_amount(low, code, rates)
    right = convert_amount(high, code, rates)
    return f'{_grouped(int(left))}–{_grouped(int(right))} {SYMBOLS[code]}'


def format_from(amount, currency: str, rates) -> str:
    return f'{_("від")} {format_amount(amount, currency, rates)}'


def is_eur_mark(mark: str | None) -> bool:
    return (mark or '').strip().lower() in EUR_MARKS


def format_package_price(package, currency: str, rates) -> str:
    if not is_eur_mark(getattr(package, 'currency', '')):
        return package.format_price()
    high = getattr(package, 'price_high', None)
    if high not in (None, '') and Decimal(high) > Decimal(package.price):
        return format_range(package.price, high, currency, rates)
    code = currency if currency in available_codes(rates) else 'EUR'
    if code == 'EUR':
        return package.format_price()
    shown = convert_amount(package.price, code, rates)
    return f'{_grouped(int(shown))} {SYMBOLS[code]}'
