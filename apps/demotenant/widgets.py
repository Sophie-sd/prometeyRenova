"""Віджети демо-адмінки: фото з українською кнопкою, без голого file-chrome."""
from django import forms
from django.utils.translation import gettext_lazy as _


class PhotoClearableInput(forms.ClearableFileInput):
    template_name = 'demotenant/widgets/photo_input.html'
    clear_checkbox_label = _('Прибрати фото')
    input_text = _('Змінити фото')
    initial_text = _('Поточне фото')

    def __init__(self, attrs=None):
        merged = {'accept': 'image/*', 'class': 'dc-photo__file'}
        if attrs:
            merged.update(attrs)
        super().__init__(attrs=merged)
