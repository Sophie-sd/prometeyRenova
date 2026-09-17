"""Форма заявки лендінгу. Honeypot перевіряється у view (тихий success, не 400)."""
from django import forms

from .lead_models import LandingLead


class TelInput(forms.TextInput):
    input_type = 'tel'


class LandingLeadForm(forms.ModelForm):
    class Meta:
        model = LandingLead
        fields = ('name', 'phone', 'email', 'message')
        widgets = {
            'name': forms.TextInput(attrs={
                'autocomplete': 'name', 'class': 'dl-input',
            }),
            'phone': TelInput(attrs={
                'autocomplete': 'tel', 'inputmode': 'tel', 'class': 'dl-input',
            }),
            'email': forms.EmailInput(attrs={
                'autocomplete': 'email', 'class': 'dl-input',
            }),
            'message': forms.Textarea(attrs={
                'rows': 4, 'class': 'dl-input',
            }),
        }
