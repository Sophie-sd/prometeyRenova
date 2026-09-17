"""Scoping для клієнтських колекцій (товари/проєкти/відгуки тощо).

Реальний захист — `get_queryset`, не group permissions (django_roles_permissions_skill):
Django permissions діють на рівні моделі, а не запису.
"""
from __future__ import annotations


class TenantScopedAdminMixin:
    """Клієнт бачить і редагує лише дані свого тенанта.

    Підклас задає `tenant_field` (FK-поле моделі на тенанта, дефолт `'tenant'`),
    `tenant_lookup` (шлях фільтра queryset, напр. `'tenant__pk'` або
    `'product__tenant__pk'` для вкладених колекцій) і `owner_attr`
    (атрибут на `User`: `'demo_corp'` / `'demo_landing'`).
    """

    tenant_field = 'tenant'
    tenant_lookup = 'tenant__pk'
    owner_attr = ''

    def _owned_tenant(self, request):
        return getattr(request.user, self.owner_attr, None)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        tenant = self._owned_tenant(request)
        if tenant is None:
            return qs.none()
        return qs.filter(**{self.tenant_lookup: tenant.pk})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == self.tenant_field and not request.user.is_superuser:
            tenant = self._owned_tenant(request)
            model = db_field.remote_field.model
            kwargs['queryset'] = model.objects.filter(pk=tenant.pk) if tenant else model.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not change and getattr(obj, f'{self.tenant_field}_id', None) is None:
            tenant = self._owned_tenant(request)
            if tenant:
                setattr(obj, self.tenant_field, tenant)
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.is_superuser and self.tenant_field in fields:
            fields.remove(self.tenant_field)
        return fields
