"""Shared phone normalisation (server mirror of static/js/core/phone-mask.js).

Ukrainian numbers: +380 + exactly 9 national digits. Other international numbers
(with + or 00) are accepted as E.164 (8-15 digits) only on the EN version (neutral
international mask); UA/RU versions accept only +380 (mirror of phone-mask.js).
normalize_phone() -> E.164 "+380XXXXXXXXX" or None.
Accepted input formats: +380..., 380..., 0XX..., XX... (9 digits), 80XX..., 00380...,
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

    if digits.startswith(UA_CODE):
        national = digits[3:]
    elif international and not allow_international:
        return None, 'foreign'
    elif international:
        # EN version uses a neutral international mask: accept any E.164 number (8-15 digits).
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
