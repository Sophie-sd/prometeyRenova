"""Колір фону з явною українською дією."""
from django import forms
from django.utils.translation import gettext_lazy as _


class ColorActionInput(forms.TextInput):
    input_type = 'color'
    template_name = 'democorp/widgets/color_input.html'

    def __init__(self, action_label=None, attrs=None):
        self.action_label = action_label or _('Змінити фон')
        merged = {'class': 'dc-color__input'}
        if attrs:
            merged.update(attrs)
        super().__init__(attrs=merged)

    def get_context(self, name, value, attrs):
        if isinstance(value, str) and value:
            value = value.lower()
        context = super().get_context(name, value, attrs)
        context['widget']['action_label'] = str(self.action_label)
        return context
