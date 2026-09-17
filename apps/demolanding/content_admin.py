"""«Мій лендінг» — єдина CMS-сторінка: тексти, фото, кольори, стиль, hero-медіа."""
from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.demotenant.content_admin_base import TenantContentAdminBase

from .block_defaults import BLOCK_REGISTRY, PAGE_LABELS
from .content_models import LandingBlock
from .models import DEFAULT_THEME_COLORS, LandingSite

HEX_WIDGET = forms.TextInput(attrs={'type': 'color'})


class LandingSettingsForm(forms.ModelForm):
    """Кольори теми + стиль + hero-медіа лендінгу (theme_switcher_skill: порожнє
    кольорове поле = дефолт з `demolanding_tokens.css`, підставляємо initial).
    """

    class Meta:
        model = LandingSite
        fields = (
            'style_preset', 'hero_mode',
            'hero_image', 'hero_image_narrow', 'hero_video', 'hero_poster',
            'color_primary', 'color_primary_hover', 'color_accent', 'color_surface', 'color_text',
        )
        widgets = {
            'color_primary': HEX_WIDGET,
            'color_primary_hover': HEX_WIDGET,
            'color_accent': HEX_WIDGET,
            'color_surface': HEX_WIDGET,
            'color_text': HEX_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color_primary'].help_text = _('Ink / dark CTA, напр. #16181A')
        self.fields['color_primary_hover'].help_text = _('Hover dark CTA, напр. #33383C')
        self.fields['color_accent'].help_text = _('Lime CTA, напр. #DFF250')
        self.fields['color_surface'].help_text = _('Cream canvas, напр. #F7F6F4')
        self.fields['color_text'].help_text = _('Основний текст, напр. #16181A')
        if self.instance and self.instance.pk:
            for name in DEFAULT_THEME_COLORS:
                if not getattr(self.instance, name):
                    self.initial[name] = DEFAULT_THEME_COLORS[name]


@admin.register(LandingBlock)
class LandingContentAdmin(TenantContentAdminBase):
    """Реєстрація лише для стабільного admin URL — CRUD вимкнено (базовий клас)."""

    registry = BLOCK_REGISTRY
    tenant_model = LandingSite
    block_model = LandingBlock
    owner_attr = 'demo_landing'
    settings_form_class = LandingSettingsForm
    template_name = 'demolanding/admin/my_landing_content.html'
    picker_template_name = 'demolanding/admin/tenant_picker.html'
    page_labels = PAGE_LABELS
    title_text = _('Мій лендінг — контент і стиль')
