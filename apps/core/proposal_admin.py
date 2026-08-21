"""Unfold admin для комерційних пропозицій."""
from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import AdminTinyMCE
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline

from .admin_filters import BooleanDropdownFilter
from .portfolio_sanitize import linkify_portfolio_html
from .proposal_models import Proposal, ProposalModule, ProposalPackage, ProposalSpec

PROPOSAL_MCE_ATTRS = {
    'height': 280,
    'min_height': 180,
    'plugins': 'lists link autoresize code',
    'toolbar': (
        'undo redo | bold italic underline | bullist numlist link | '
        'removeformat | code'
    ),
}


class ProposalAdminForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = '__all__'
        widgets = {
            'intro_html': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'intro_html_ru': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'guarantee_html': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'guarantee_html_ru': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'lead': forms.Textarea(attrs={'rows': 3}),
            'lead_ru': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_intro_html(self):
        return linkify_portfolio_html(self.cleaned_data.get('intro_html', ''))

    def clean_intro_html_ru(self):
        return linkify_portfolio_html(self.cleaned_data.get('intro_html_ru', ''))

    def clean_guarantee_html(self):
        return linkify_portfolio_html(self.cleaned_data.get('guarantee_html', ''))

    def clean_guarantee_html_ru(self):
        return linkify_portfolio_html(self.cleaned_data.get('guarantee_html_ru', ''))


class ProposalModuleInline(UnfoldTabularInline):
    model = ProposalModule
    extra = 0
    fields = ('number', 'title', 'title_ru', 'description', 'description_ru', 'order')
    ordering = ('order', 'number', 'id')
    verbose_name = _('Модуль')
    verbose_name_plural = _('Модулі')


class ProposalPackageInline(UnfoldTabularInline):
    model = ProposalPackage
    extra = 0
    fields = (
        'name', 'name_ru', 'scope', 'scope_ru',
        'duration', 'duration_ru', 'price', 'currency',
        'is_recommended', 'order',
    )
    ordering = ('order', 'id')
    verbose_name = _('Пакет')
    verbose_name_plural = _('Пакети')


class ProposalSpecInline(UnfoldTabularInline):
    model = ProposalSpec
    extra = 0
    fields = ('kind', 'title', 'title_ru', 'body', 'body_ru', 'order')
    ordering = ('kind', 'order', 'id')
    verbose_name = _('Специфікація')
    verbose_name_plural = _('Специфікації')


@admin.register(Proposal)
class ProposalAdmin(UnfoldModelAdmin):
    form = ProposalAdminForm
    inlines = [ProposalModuleInline, ProposalPackageInline, ProposalSpecInline]
    list_filter_sheet = False
    list_display = (
        'client_name',
        'title',
        'issued_on',
        'is_published',
        'order',
        'open_page',
    )
    list_filter = (
        ('is_published', BooleanDropdownFilter),
    )
    search_fields = ('client_name', 'title', 'slug')
    prepopulated_fields = {'slug': ('client_name',)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order', '-issued_on')

    fieldsets = (
        (_('Основне'), {
            'fields': (
                'client_name',
                'slug',
                'title',
                'title_ru',
                'lead',
                'lead_ru',
                'issued_on',
                'cta_label',
                'cta_label_ru',
                'order',
                'is_published',
            ),
        }),
        (_('Про компанію / стек'), {
            'fields': ('intro_html', 'intro_html_ru'),
        }),
        (_('Гарантія'), {
            'fields': ('guarantee_html', 'guarantee_html_ru'),
        }),
        (_('Мета'), {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description=_('Відкрити'))
    def open_page(self, obj):
        if not obj or not obj.slug:
            return '—'
        url = reverse('proposal_detail', kwargs={'slug': obj.slug})
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a>',
            url,
            obj.slug,
        )
