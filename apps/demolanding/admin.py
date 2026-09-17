"""Демо-лендінги в адмінці (агенція): без CRUD create — лише з дії у `Proposal`."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from apps.demotenant.services.provision import deactivate_tenant

from . import collection_admin  # noqa: F401
from . import content_admin  # noqa: F401
from .models import LandingSite


@admin.register(LandingSite)
class LandingSiteAdmin(UnfoldModelAdmin):
    list_filter_sheet = False
    list_display = ('name', 'slug', 'style_preset', 'is_active', 'created_at')
    list_filter = ('is_active', 'style_preset')
    search_fields = ('name', 'slug')
    readonly_fields = ('demo_login', 'demo_password', 'created_at', 'updated_at')
    actions = ['deactivate_action', 'activate_action']

    def has_add_permission(self, request):
        return False

    @admin.action(description=_('Деактивувати (вимкнути клієнтський логін)'))
    def deactivate_action(self, request, queryset):
        for site in queryset:
            deactivate_tenant(site)
        self.message_user(request, _('Деактивовано %(count)d лендінг(ів).') % {'count': queryset.count()})

    @admin.action(description=_('Активувати'))
    def activate_action(self, request, queryset):
        count = queryset.update(is_active=True)
        for site in queryset:
            if site.owner_user_id:
                site.owner_user.is_active = True
                site.owner_user.save(update_fields=['is_active'])
        self.message_user(request, _('Активовано %(count)d лендінг(ів).') % {'count': count})
