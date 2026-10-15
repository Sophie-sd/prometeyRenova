"""Shared phone normalisation (server mirror of static/js/core/phone-mask.js).

Only Ukrainian numbers are accepted: +380 + exactly 9 national digits.
normalize_phone() -> E.164 "+380XXXXXXXXX" or None.
Accepted input formats: +380..., 380..., 0XX..., XX... (9 digits), 80XX..., 00380...,
with any spaces, dashes, dots or brackets.
"""
import re

UA_CODE = '380'
UA_NATIONAL_LEN = 9
_ALLOWED = re.compile(r'^[\d\s()+\-.]*$')


def parse_phone(raw):
    """Return (e164 or None, error_code). error_code: empty, chars, foreign, short, long."""
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
    elif international:
        return None, 'foreign'
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


def normalize_phone(raw):
    return parse_phone(raw)[0]
