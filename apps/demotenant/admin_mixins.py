"""Scoping для клієнтських колекцій (товари/проєкти/відгуки тощо).

Реальний захист — `get_queryset`, не group permissions (django_roles_permissions_skill):
Django permissions діють на рівні моделі, а не запису.
"""
from __future__ import annotations

from django import forms


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
            # Клієнт не обирає «Сайт» — він один; поле приховане, але валідується
            # (unique_together з tenant лишається в перевірці форми).
            kwargs['widget'] = forms.HiddenInput()
            kwargs['initial'] = tenant.pk if tenant else None
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def _hides_tenant(self, request) -> bool:
        """Клієнт не обирає «Сайт»: він у нього один і підставляється сам."""
        if request.user.is_superuser or self._owned_tenant(request) is None:
            return False
        if self.tenant_field in self.get_readonly_fields(request):
            return False
        return any(f.name == self.tenant_field for f in self.model._meta.fields)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not self._hides_tenant(request):
            return fieldsets
        cleaned = []
        for name, options in fieldsets:
            options = dict(options)
            lines = []
            for line in options.get('fields', ()):
                if isinstance(line, (list, tuple)):
                    line = tuple(f for f in line if f != self.tenant_field)
                    if line:
                        lines.append(line)
                elif line != self.tenant_field:
                    lines.append(line)
            options['fields'] = lines
            cleaned.append((name, options))
        return cleaned

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not self._hides_tenant(request):
            return form
        tenant = self._owned_tenant(request)
        tenant_field = self.tenant_field

        class TenantForm(form):
            def __init__(self, *args, **kw):
                super().__init__(*args, **kw)
                if getattr(self.instance, f'{tenant_field}_id', None) is None:
                    setattr(self.instance, tenant_field, tenant)

            def _get_validation_exclusions(self):
                # Поле приховане, але unique_together (tenant, slug) перевіряється.
                exclude = super()._get_validation_exclusions()
                exclude.discard(tenant_field)
                return exclude

        TenantForm.__name__ = form.__name__
        return TenantForm

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
