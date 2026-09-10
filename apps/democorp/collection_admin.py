"""Колекції корпоративного сайту в адмінці клієнта: доступ scoped до `CorpSite`."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from apps.demotenant.admin_mixins import TenantScopedAdminMixin

from .collection_models import CorpGalleryImage, CorpPartner, CorpProductionStep, CorpTestimonial
from .lead_models import CorpLead


class CorpScopedAdmin(TenantScopedAdminMixin, UnfoldModelAdmin):
    owner_attr = 'demo_corp'
    list_filter_sheet = False


@admin.register(CorpProductionStep)
class CorpProductionStepAdmin(CorpScopedAdmin):
    list_display = ('title', 'tenant', 'order')
    ordering = ('tenant', 'order')


@admin.register(CorpGalleryImage)
class CorpGalleryImageAdmin(CorpScopedAdmin):
    list_display = ('caption', 'tenant', 'kind', 'order')
    list_filter = ('kind',)
    ordering = ('tenant', 'kind', 'order')


@admin.register(CorpTestimonial)
class CorpTestimonialAdmin(CorpScopedAdmin):
    list_display = ('author_name', 'tenant', 'rating', 'order')
    ordering = ('tenant', 'order')


@admin.register(CorpPartner)
class CorpPartnerAdmin(CorpScopedAdmin):
    list_display = ('name', 'tenant', 'order')
    ordering = ('tenant', 'order')


@admin.register(CorpLead)
class CorpLeadAdmin(CorpScopedAdmin):
    list_display = ('name', 'tenant', 'product', 'phone', 'created_at', 'is_read')
    list_filter = ('is_read',)
    ordering = ('-created_at',)
    readonly_fields = ('name', 'phone', 'email', 'message', 'product', 'created_at', 'tenant')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
