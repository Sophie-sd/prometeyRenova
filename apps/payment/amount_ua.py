"""Сума прописом українською (гривні та копійки)."""
from decimal import Decimal, ROUND_HALF_UP


_ONES = [
    '', 'одна', 'дві', 'три', 'чотири', 'п\'ять', 'шість', 'сім', 'вісім', 'дев\'ять',
]
_ONES_MASC = [
    '', 'один', 'два', 'три', 'чотири', 'п\'ять', 'шість', 'сім', 'вісім', 'дев\'ять',
]
_TEENS = [
    'десять', 'одинадцять', 'дванадцять', 'тринадцять', 'чотирнадцять',
    'п\'ятнадцять', 'шістнадцять', 'сімнадцять', 'вісімнадцять', 'дев\'ятнадцять',
]
_TENS = [
    '', '', 'двадцять', 'тридцять', 'сорок', 'п\'ятдесят',
    'шістдесят', 'сімдесят', 'вісімдесят', 'дев\'яносто',
]
_HUNDREDS = [
    '', 'сто', 'двісті', 'триста', 'чотириста', 'п\'ятсот',
    'шістсот', 'сімсот', 'вісімсот', 'дев\'ятсот',
]


def _plural(n: int, one: str, few: str, many: str) -> str:
    n = abs(n) % 100
    if 11 <= n <= 19:
        return many
    n = n % 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return few
    return many


def _triad_to_words(n: int, feminine: bool) -> str:
    if n <= 0:
        return ''
    parts = []
    h = n // 100
    t = (n % 100) // 10
    o = n % 10
    if h:
        parts.append(_HUNDREDS[h])
    if t == 1:
        parts.append(_TEENS[o])
        return ' '.join(parts)
    if t:
        parts.append(_TENS[t])
    if o:
        ones = _ONES if feminine else _ONES_MASC
        parts.append(ones[o])
    return ' '.join(parts)


def _int_to_words(n: int) -> str:
    if n == 0:
        return 'нуль'
    parts = []
    billions = n // 1_000_000_000
    millions = (n % 1_000_000_000) // 1_000_000
    thousands = (n % 1_000_000) // 1000
    rest = n % 1000

    if billions:
        parts.append(_triad_to_words(billions, feminine=False))
        parts.append(_plural(billions, 'мільярд', 'мільярди', 'мільярдів'))
    if millions:
        parts.append(_triad_to_words(millions, feminine=False))
        parts.append(_plural(millions, 'мільйон', 'мільйони', 'мільйонів'))
    if thousands:
        parts.append(_triad_to_words(thousands, feminine=True))
        parts.append(_plural(thousands, 'тисяча', 'тисячі', 'тисяч'))
    if rest:
        parts.append(_triad_to_words(rest, feminine=False))
    return ' '.join(p for p in parts if p)


def amount_in_words_ua(amount) -> str:
    """
    >>> amount_in_words_ua(Decimal('20600.00'))
    'Двадцять тисяч шістсот гривень 00 копійок'
    """
    value = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    hryvnias = int(value)
    kopiyky = int((value - hryvnias) * 100)

    words = _int_to_words(hryvnias)
    if words:
        words = words[0].upper() + words[1:]
    else:
        words = 'Нуль'

    hryvnia_word = _plural(hryvnias, 'гривня', 'гривні', 'гривень')
    kop_word = _plural(kopiyky, 'копійка', 'копійки', 'копійок')
    return f'{words} {hryvnia_word} {kopiyky:02d} {kop_word}'


def format_money_ua(amount) -> str:
    """20 600,00"""
    value = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    sign = '-' if value < 0 else ''
    value = abs(value)
    whole = int(value)
    frac = int((value - whole) * 100)
    whole_str = f'{whole:,}'.replace(',', ' ')
    return f'{sign}{whole_str},{frac:02d}'
