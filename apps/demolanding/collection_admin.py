"""Колекції лендінгу в адмінці клієнта: доступ scoped до власного `LandingSite`."""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from apps.demotenant.admin_mixins import TenantScopedAdminMixin

from .collection_models import (
    LandingBeforeAfter,
    LandingGalleryImage,
    LandingOffer,
    LandingPartner,
    LandingTestimonial,
)
from .lead_models import LandingLead


def _thumb(file_field):
    if not file_field:
        return '—'
    return format_html(
        '<img src="{}" alt="" width="64" height="48" class="dl-admin-thumb">',
        file_field.url,
    )


class LandingScopedAdmin(TenantScopedAdminMixin, UnfoldModelAdmin):
    owner_attr = 'demo_landing'
    list_filter_sheet = False

    class Media:
        css = {'all': ('demolanding/css/demolanding_admin.css',)}


@admin.register(LandingOffer)
class LandingOfferAdmin(LandingScopedAdmin):
    list_display = ('thumb', 'title', 'tenant', 'price_from', 'is_active', 'order')
    list_filter = ('is_active',)
    ordering = ('tenant', 'order')
    fieldsets = (
        (_('Основне'), {'fields': (
            'tenant', 'title', 'title_ru', 'title_en', 'title_cs',
            'description', 'description_ru', 'description_en', 'description_cs',
            'price_from', 'image',
        )}),
        (_('Видимість'), {'fields': ('is_active', 'order')}),
    )

    @admin.display(description=_('Фото'))
    def thumb(self, obj):
        return _thumb(obj.image)


@admin.register(LandingGalleryImage)
class LandingGalleryImageAdmin(LandingScopedAdmin):
    list_display = ('thumb', 'caption', 'tenant', 'span', 'order')
    ordering = ('tenant', 'order')

    @admin.display(description=_('Фото'))
    def thumb(self, obj):
        return _thumb(obj.image)


@admin.register(LandingBeforeAfter)
class LandingBeforeAfterAdmin(LandingScopedAdmin):
    list_display = ('thumb', 'title', 'tenant', 'order')
    ordering = ('tenant', 'order')

    @admin.display(description=_('До'))
    def thumb(self, obj):
        return _thumb(obj.image_before)


@admin.register(LandingTestimonial)
class LandingTestimonialAdmin(LandingScopedAdmin):
    list_display = ('author_name', 'tenant', 'rating', 'order')
    ordering = ('tenant', 'order')


@admin.register(LandingPartner)
class LandingPartnerAdmin(LandingScopedAdmin):
    list_display = ('name', 'tenant', 'order')
    ordering = ('tenant', 'order')


@admin.register(LandingLead)
class LandingLeadAdmin(LandingScopedAdmin):
    list_display = ('name', 'tenant', 'phone', 'created_at', 'is_read')
    list_filter = ('is_read',)
    ordering = ('-created_at',)
    readonly_fields = ('name', 'phone', 'email', 'message', 'created_at', 'tenant')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
