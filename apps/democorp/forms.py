"""Форми лід-заявок корпоративного сайту (контакти + «Купити» на PDP)."""
from django import forms
from django.utils.translation import gettext_lazy as _

from .lead_models import CorpLead

_INPUT_ATTRS = {
    'name': {'autocomplete': 'name', 'class': 'dc-input'},
    'phone': {'autocomplete': 'tel', 'inputmode': 'tel', 'class': 'dc-input'},
    'email': {'autocomplete': 'email', 'class': 'dc-input'},
}


class CorpLeadForm(forms.ModelForm):
    class Meta:
        model = CorpLead
        fields = ('name', 'phone', 'email', 'message')
        labels = {
            'name': _('Імʼя'),
            'phone': _('Телефон'),
            'email': _('Email'),
            'message': _('Повідомлення'),
        }
        widgets = {
            'name': forms.TextInput(attrs=_INPUT_ATTRS['name']),
            'phone': forms.TextInput(attrs=_INPUT_ATTRS['phone']),
            'email': forms.EmailInput(attrs=_INPUT_ATTRS['email']),
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'dc-input'}),
        }
