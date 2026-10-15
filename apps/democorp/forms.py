"""Форми лід-заявок корпоративного сайту (контакти + «Хочу такий сайт» на сторінці прикладу)."""
from django import forms

from apps.core.phone_forms import PhoneCleanMixin
from django.utils.translation import gettext_lazy as _

from .lead_models import CorpLead

_LABELS = {
    'name': _('Імʼя'),
    'phone': _('Номер телефону'),
    'email': _('Email'),
    'message': _('Повідомлення'),
}


def _attrs(name, **extra):
    return {'class': 'dc-input', 'placeholder': _LABELS[name], **extra}


class CorpLeadForm(PhoneCleanMixin, forms.ModelForm):
    class Meta:
        model = CorpLead
        fields = ('name', 'phone', 'email', 'message')
        labels = _LABELS
        widgets = {
            'name': forms.TextInput(attrs=_attrs('name', autocomplete='name')),
            'phone': forms.TextInput(attrs=_attrs('phone', autocomplete='tel', inputmode='tel')),
            'email': forms.EmailInput(attrs=_attrs('email', autocomplete='email')),
            'message': forms.Textarea(attrs=_attrs('message', rows=4)),
        }
