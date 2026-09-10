"""Каталог продукції в адмінці клієнта — видно лише сайтам з `has_catalog=True`
(модуль реєструється завжди, `has_module_permission` перевіряє прапорець)."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline

from apps.demotenant.admin_mixins import TenantScopedAdminMixin

from .catalog_models import CorpCategory, CorpProduct, CorpProductImage


class CatalogScopedAdmin(TenantScopedAdminMixin, UnfoldModelAdmin):
    owner_attr = 'demo_corp'
    list_filter_sheet = False

    def _has_catalog(self, request) -> bool:
        if request.user.is_superuser:
            return True
        tenant = self._owned_tenant(request)
        return bool(tenant and tenant.has_catalog)

    def has_module_permission(self, request):
        return super().has_module_permission(request) and self._has_catalog(request)

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj) and self._has_catalog(request)

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj) and self._has_catalog(request)

    def has_add_permission(self, request):
        return super().has_add_permission(request) and self._has_catalog(request)


class CorpProductImageInline(UnfoldTabularInline):
    model = CorpProductImage
    extra = 0
    fields = ('image', 'is_main', 'order')
    ordering = ('-is_main', 'order', 'id')
    verbose_name = _('Фото')
    verbose_name_plural = _('Фото товару')


@admin.register(CorpCategory)
class CorpCategoryAdmin(CatalogScopedAdmin):
    list_display = ('name', 'tenant', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'name_ru', 'name_en', 'name_cs')
    ordering = ('tenant', 'order')


@admin.register(CorpProduct)
class CorpProductAdmin(CatalogScopedAdmin):
    inlines = [CorpProductImageInline]
    list_display = ('name', 'tenant', 'category', 'price_from', 'is_active', 'is_featured', 'order')
    list_filter = ('is_active', 'is_featured', 'category')
    search_fields = ('name',)
    ordering = ('tenant', 'order')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category' and not request.user.is_superuser:
            tenant = self._owned_tenant(request)
            kwargs['queryset'] = CorpCategory.objects.filter(tenant=tenant) if tenant else CorpCategory.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
