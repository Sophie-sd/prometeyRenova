"""Django form helper: shared clean_phone (E.164) for lead forms."""
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.phone import parse_phone

PHONE_INVALID_MSG = _('Введіть коректний номер телефону')
PHONE_FOREIGN_MSG = _('Приймаємо лише українські номери +380')


def clean_phone_value(value, required=False):
    value = (value or '').strip()
    if not value and not required:
        return ''
    e164, err = parse_phone(value)
    if not e164:
        if err == 'foreign':
            raise forms.ValidationError(PHONE_FOREIGN_MSG, code='foreign_phone')
        raise forms.ValidationError(PHONE_INVALID_MSG, code='invalid_phone')
    return e164


class PhoneCleanMixin:
    def clean_phone(self):
        field = self.fields['phone']
        return clean_phone_value(self.cleaned_data.get('phone'), required=field.required)
