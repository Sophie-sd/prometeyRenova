"""Shared phone normalisation (server mirror of static/js/core/phone-mask.js).

Ukrainian numbers: +380 + exactly 9 national digits.
UA/RU accept only Ukrainian numbers. EN also accepts any E.164 number that
starts with + or 00 (8-15 digits, country code not 0).
On every language a local 0XXXXXXXXX (10 digits) and 380XXXXXXXXX normalise to +380...
normalize_phone() -> E.164 or None.
Accepted UA input: +380..., 380..., 0XX..., XX... (9 digits), 80XX..., 00380...,
with any spaces, dashes, dots or brackets.
"""
import re

from django.utils import translation

UA_CODE = '380'
UA_NATIONAL_LEN = 9
_ALLOWED = re.compile(r'^[\d\s()+\-.]*$')


def _intl_allowed():
    return (translation.get_language() or '').split('-')[0] == 'en'


def parse_phone(raw, allow_international=None):
    """Return (e164 or None, error_code). error_code: empty, chars, foreign, short, long.

    allow_international=None → decided by the active language (EN only).
    """
    if allow_international is None:
        allow_international = _intl_allowed()
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

    # +380... / 380... / 00380... — Ukrainian even when the page is EN.
    if digits.startswith(UA_CODE):
        national = digits[3:]
    # Local trunk 0XXXXXXXXX (10 digits). A leading 0 is not a country code,
    # so "+0671234567" is the same number as "0671234567".
    elif digits.startswith('0') and len(digits) == 10:
        national = digits[1:]
    elif international and not allow_international:
        return None, 'foreign'
    elif international:
        # EN: any E.164 number (8-15 digits) whose country code does not start with 0.
        if digits.startswith('0'):
            return None, 'short' if len(digits) < 8 else 'long'
        if 8 <= len(digits) <= 15:
            return '+' + digits, ''
        return None, 'short' if len(digits) < 8 else 'long'
    elif digits.startswith('80') and len(digits) == 11:
        national = digits[2:]
    else:
        national = digits

    if national.startswith('0'):
        national = national[1:]
    if len(national) < UA_NATIONAL_LEN:
        return None, 'short'
    if len(national) > UA_NATIONAL_LEN:
        return None, 'long'
    return '+' + UA_CODE + national, ''


def normalize_phone(raw, allow_international=None):
    return parse_phone(raw, allow_international)[0]
