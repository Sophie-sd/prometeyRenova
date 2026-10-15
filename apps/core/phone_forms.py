"""Django form helper: shared clean_phone (E.164) for lead forms."""
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.phone import parse_phone

PHONE_INVALID_MSG = _('Введіть коректний номер телефону')


def clean_phone_value(value, required=False):
    value = (value or '').strip()
    if not value and not required:
        return ''
    e164, _err = parse_phone(value)
    if not e164:
        raise forms.ValidationError(PHONE_INVALID_MSG, code='invalid_phone')
    return e164


class PhoneCleanMixin:
    def clean_phone(self):
        field = self.fields['phone']
        return clean_phone_value(self.cleaned_data.get('phone'), required=field.required)
