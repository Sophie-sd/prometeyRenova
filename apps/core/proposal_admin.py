"""Unfold admin для комерційних пропозицій."""
from django import forms
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import AdminTinyMCE
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline

from .admin_filters import BooleanDropdownFilter
from .portfolio_sanitize import linkify_portfolio_html
from .proposal_models import Proposal, ProposalModule, ProposalPackage, ProposalSpec
from .proposal_visual_models import ProposalArchNode, ProposalHighlight

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
            'intro_html_en': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'intro_html_cs': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'guarantee_html': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'guarantee_html_ru': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'guarantee_html_en': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'guarantee_html_cs': AdminTinyMCE(mce_attrs=PROPOSAL_MCE_ATTRS),
            'lead': forms.Textarea(attrs={'rows': 3}),
            'lead_ru': forms.Textarea(attrs={'rows': 3}),
            'lead_en': forms.Textarea(attrs={'rows': 3}),
            'lead_cs': forms.Textarea(attrs={'rows': 3}),
            'recommendations_lead': forms.Textarea(attrs={'rows': 3}),
            'recommendations_lead_ru': forms.Textarea(attrs={'rows': 3}),
            'recommendations_lead_en': forms.Textarea(attrs={'rows': 3}),
            'recommendations_lead_cs': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_intro_html(self):
        return linkify_portfolio_html(self.cleaned_data.get('intro_html', ''))

    def clean_intro_html_ru(self):
        return linkify_portfolio_html(self.cleaned_data.get('intro_html_ru', ''))

    def clean_intro_html_en(self):
        return linkify_portfolio_html(self.cleaned_data.get('intro_html_en', ''))

    def clean_intro_html_cs(self):
        return linkify_portfolio_html(self.cleaned_data.get('intro_html_cs', ''))

    def clean_guarantee_html(self):
        return linkify_portfolio_html(self.cleaned_data.get('guarantee_html', ''))

    def clean_guarantee_html_ru(self):
        return linkify_portfolio_html(self.cleaned_data.get('guarantee_html_ru', ''))

    def clean_guarantee_html_en(self):
        return linkify_portfolio_html(self.cleaned_data.get('guarantee_html_en', ''))

    def clean_guarantee_html_cs(self):
        return linkify_portfolio_html(self.cleaned_data.get('guarantee_html_cs', ''))


class ProposalModuleInline(UnfoldTabularInline):
    model = ProposalModule
    extra = 0
    fields = (
        'number',
        'title', 'title_ru', 'title_en', 'title_cs',
        'description', 'description_ru', 'description_en', 'description_cs',
        'order',
    )
    ordering = ('order', 'number', 'id')
    verbose_name = _('Модуль')
    verbose_name_plural = _('Модулі')


class ProposalPackageInline(UnfoldTabularInline):
    model = ProposalPackage
    extra = 0
    fields = (
        'name', 'name_ru', 'name_en', 'name_cs',
        'scope', 'scope_ru', 'scope_en', 'scope_cs',
        'duration', 'duration_ru', 'duration_en', 'duration_cs',
        'price', 'currency',
        'is_recommended', 'order',
    )
    ordering = ('order', 'id')
    verbose_name = _('Пакет')
    verbose_name_plural = _('Пакети')


class ProposalSpecInline(UnfoldTabularInline):
    model = ProposalSpec
    extra = 0
    fields = (
        'kind',
        'title', 'title_ru', 'title_en', 'title_cs',
        'body', 'body_ru', 'body_en', 'body_cs',
        'order',
    )
    ordering = ('kind', 'order', 'id')
    verbose_name = _('Специфікація')
    verbose_name_plural = _('Специфікації')


class ProposalHighlightInline(UnfoldTabularInline):
    model = ProposalHighlight
    extra = 0
    fields = (
        'title', 'title_ru', 'title_en', 'title_cs',
        'order',
    )
    ordering = ('order', 'id')
    verbose_name = _('Херо-пункт')
    verbose_name_plural = _('Херо-пункти')


class ProposalArchNodeInline(UnfoldTabularInline):
    model = ProposalArchNode
    extra = 0
    fields = (
        'title', 'title_ru', 'title_en', 'title_cs',
        'caption', 'caption_ru', 'caption_en', 'caption_cs',
        'is_accent',
        'order',
    )
    ordering = ('order', 'id')
    verbose_name = _('Вузол архітектури')
    verbose_name_plural = _('Дерево архітектури')


@admin.register(Proposal)
class ProposalAdmin(UnfoldModelAdmin):
    form = ProposalAdminForm
    inlines = [
        ProposalHighlightInline,
        ProposalArchNodeInline,
        ProposalModuleInline,
        ProposalPackageInline,
        ProposalSpecInline,
    ]
    list_filter_sheet = False
    actions = ['create_demo_action']
    list_display = (
        'client_name',
        'title',
        'kind',
        'issued_on',
        'is_published',
        'order',
        'open_page',
        'demo_link',
        'client_access_link',
    )
    list_filter = (
        'kind',
        ('is_published', BooleanDropdownFilter),
    )
    search_fields = ('client_name', 'title', 'slug')
    prepopulated_fields = {'slug': ('client_name',)}
    readonly_fields = ('created_at', 'updated_at', 'hero_image_preview')
    ordering = ('order', '-issued_on')

    fieldsets = (
        (_('Основне'), {
            'fields': (
                'client_name',
                'slug',
                'title',
                'title_ru',
                'title_en',
                'title_cs',
                'lead',
                'lead_ru',
                'lead_en',
                'lead_cs',
                'issued_on',
                'cta_label',
                'cta_label_ru',
                'cta_label_en',
                'cta_label_cs',
                'order',
                'is_published',
            ),
        }),
        (_('Вітрина'), {
            'fields': (
                'hero_image',
                'hero_image_preview',
                'recommendations_lead',
                'recommendations_lead_ru',
                'recommendations_lead_en',
                'recommendations_lead_cs',
            ),
        }),
        (_('Демо'), {
            'description': _(
                'Тип демо визначає, яку вітрину створює дія «Створити/оновити демо» '
                'нижче у списку. «Каталог» доступний лише для корпоративного сайту.',
            ),
            'fields': ('kind', 'corp_catalog'),
        }),
        (_('Про компанію / стек'), {
            'fields': ('intro_html', 'intro_html_ru', 'intro_html_en', 'intro_html_cs'),
        }),
        (_('Гарантія'), {
            'fields': ('guarantee_html', 'guarantee_html_ru', 'guarantee_html_en', 'guarantee_html_cs'),
        }),
        (_('Мета'), {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description=_('Прев’ю херо'))
    def hero_image_preview(self, obj):
        if not obj or not obj.hero_image:
            return '—'
        return format_html(
            '<img src="{}" alt="" class="pl-admin-image-preview">',
            obj.hero_image.url,
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

    _DEMO_HOME_URL = {
        Proposal.DemoKind.SHOP: ('demoshop:home', 'shop_slug'),
        Proposal.DemoKind.LANDING: ('demolanding:home', 'slug'),
        Proposal.DemoKind.CORPORATE: ('democorp:home', 'slug'),
    }
    _DEMO_ACCESS_URL = {
        Proposal.DemoKind.SHOP: ('demoshop:admin_access', 'shop_slug'),
        Proposal.DemoKind.LANDING: ('demolanding:admin_access', 'slug'),
        Proposal.DemoKind.CORPORATE: ('democorp:admin_access', 'slug'),
    }

    @admin.display(description=_('Демо'))
    def demo_link(self, obj):
        tenant = obj.demo_tenant
        if not tenant:
            return '—'
        url_name, kwarg_name = self._DEMO_HOME_URL[obj.kind]
        url = reverse(url_name, kwargs={kwarg_name: tenant.slug})
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', url, tenant.slug)

    @admin.display(description=_('Доступ клієнта'))
    def client_access_link(self, obj):
        tenant = obj.demo_tenant
        if not tenant:
            return '—'
        url_name, kwarg_name = self._DEMO_ACCESS_URL[obj.kind]
        url = reverse(url_name, kwargs={kwarg_name: tenant.slug})
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', url, tenant.demo_login or '—')

    @admin.action(description=_('Створити/оновити демо'))
    def create_demo_action(self, request, queryset):
        from apps.demoshop.services.provision import provision_demo_shop

        count = 0
        for proposal in queryset:
            if proposal.kind == Proposal.DemoKind.LANDING:
                from apps.demolanding.services.provision import provision_demo_landing

                provision_demo_landing(proposal)
            elif proposal.kind == Proposal.DemoKind.CORPORATE:
                from apps.democorp.services.provision import provision_demo_corp

                provision_demo_corp(proposal)
            else:
                provision_demo_shop(proposal)
            count += 1
        self.message_user(
            request,
            _('Демо готове для %(count)d КП.') % {'count': count},
            messages.SUCCESS,
        )
