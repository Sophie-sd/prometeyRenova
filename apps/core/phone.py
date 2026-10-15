"""Shared phone normalisation (server side mirror of static/js/core/phone-mask.js).

normalize_phone() -> E.164 string ("+380671234567") or None.
Ukraine (+380) is the default: exactly 9 national digits are required.
Other countries are accepted only with the correct national digit count.
"""
import re

UA_CODE = '380'
UA_NATIONAL_LEN = 9

# country code -> (min, max) national significant number length
COUNTRY_LENGTHS = {
    '380': (9, 9),    # Ukraine
    '1': (10, 10),    # US / Canada
    '7': (10, 10),    # RU / KZ
    '30': (10, 10), '31': (9, 9), '32': (8, 9), '33': (9, 9), '34': (9, 9),
    '36': (8, 9), '39': (6, 11), '40': (9, 9), '41': (9, 9), '43': (7, 13),
    '44': (10, 10), '45': (8, 8), '46': (7, 10), '47': (8, 8), '48': (9, 9),
    '49': (7, 12), '90': (10, 10),
    '351': (9, 9), '353': (7, 9), '358': (5, 12), '359': (8, 9),
    '370': (8, 8), '371': (8, 8), '372': (7, 8), '373': (8, 8), '375': (9, 9),
    '420': (9, 9), '421': (9, 9), '971': (8, 9), '972': (8, 9), '995': (9, 9),
}
GENERIC_E164_RANGE = (8, 15)
_ALLOWED = re.compile(r'^[\d\s()+\-.]*$')


def split_country(digits):
    for size in (3, 2, 1):
        code = digits[:size]
        if code in COUNTRY_LENGTHS:
            return code, digits[size:]
    return None, digits


def parse_phone(raw):
    """Return (e164 or None, error_code). error_code in: empty, chars, short, long, invalid."""
    value = (raw or '').strip()
    if not value:
        return None, 'empty'
    if not _ALLOWED.match(value):
        return None, 'chars'
    digits = re.sub(r'\D', '', value)
    if not digits:
        return None, 'empty'
    international = value.startswith('+') or digits.startswith('00')
    if digits.startswith('00'):
        digits = digits[2:]

    if digits.startswith(UA_CODE):
        country, national = UA_CODE, digits[3:]
    elif international:
        country, national = split_country(digits)
    elif digits.startswith('80') and len(digits) == 11:
        country, national = UA_CODE, digits[2:]
    else:
        country, national = UA_CODE, digits

    if country == UA_CODE:
        if national.startswith('0'):
            national = national[1:]
        if len(national) < UA_NATIONAL_LEN:
            return None, 'short'
        if len(national) > UA_NATIONAL_LEN:
            return None, 'long'
        return '+' + UA_CODE + national, ''

    if country is None:
        low, high = GENERIC_E164_RANGE
        if len(digits) < low:
            return None, 'short'
        if len(digits) > high:
            return None, 'long'
        return '+' + digits, ''

    low, high = COUNTRY_LENGTHS[country]
    if len(national) < low:
        return None, 'short'
    if len(national) > high:
        return None, 'long'
    return '+' + country + national, ''


def normalize_phone(raw):
    return parse_phone(raw)[0]
