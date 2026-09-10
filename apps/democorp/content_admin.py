"""«Мій сайт» — єдина CMS-сторінка: тексти, фото, кольори, стиль, каталог-прапорець."""
from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.demotenant.content_admin_base import TenantContentAdminBase

from .block_defaults import BLOCK_REGISTRY, PAGE_LABELS
from .content_models import CorpBlock
from .models import DEFAULT_THEME_COLORS, CorpSite

HEX_WIDGET = forms.TextInput(attrs={'type': 'color'})


class CorpSettingsForm(forms.ModelForm):
    """Кольори теми + стиль + hero-фото корпоративного сайту.

    `has_catalog` НЕ редагується тут — це рішення агенції при створенні КП
    (`Proposal.corp_catalog`), клієнт лише бачить наявний розділ каталогу.
    """

    class Meta:
        model = CorpSite
        fields = (
            'style_preset', 'hero_image',
            'color_surface', 'color_primary', 'color_primary_hover', 'color_text', 'color_accent',
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
        if self.instance and self.instance.pk:
            for name in DEFAULT_THEME_COLORS:
                if not getattr(self.instance, name):
                    self.initial[name] = DEFAULT_THEME_COLORS[name]
        color_ui = {
            'color_surface': (
                _('Полотно'),
                _('Фон сторінки'),
            ),
            'color_primary': (
                _('Хедер'),
                _('Шапка сайту'),
            ),
            'color_primary_hover': (
                _('Слоти'),
                _('Статистика, картки, поля форми'),
            ),
            'color_text': (
                _('Текст і CTA'),
                _('Основний текст і кнопка'),
            ),
            'color_accent': (
                _('Золото'),
                _('Акценти й лінії'),
            ),
        }
        for name, (label, help_text) in color_ui.items():
            self.fields[name].label = label
            self.fields[name].help_text = help_text


@admin.register(CorpBlock)
class CorpContentAdmin(TenantContentAdminBase):
    """Реєстрація лише для стабільного admin URL — CRUD вимкнено (базовий клас)."""

    registry = BLOCK_REGISTRY
    tenant_model = CorpSite
    block_model = CorpBlock
    owner_attr = 'demo_corp'
    settings_form_class = CorpSettingsForm
    template_name = 'democorp/admin/my_site_content.html'
    picker_template_name = 'democorp/admin/tenant_picker.html'
    page_labels = PAGE_LABELS
    title_text = _('Мій сайт — контент і стиль')
    _catalog_form_keys = {
        ('catalog', 'title'),
        ('catalog', 'buy_cta_label'),
        ('home', 'catalog_teaser_title'),
    }

    def get_registry(self, tenant):
        if tenant.has_catalog:
            return BLOCK_REGISTRY
        return [
            entry for entry in BLOCK_REGISTRY
            if (entry['page'], entry['key']) not in self._catalog_form_keys
        ]
