"""Базова клієнтська CMS-сторінка «Контент і стиль» demo-тенанта.

Спільна логіка з `apps.demoshop.content_admin.ShopContentAdmin`
(admin_cms_blocks_skill §14: блоки не мають окремого CRUD ModelAdmin — уся
робота йде через `changelist_view` цього проксі, обмежену власним тенантом).
Конкретний ModelAdmin задає лише атрибути класу нижче.
"""
from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .registry import (
    build_block_form,
    ensure_registry_blocks,
    group_blocks_for_template,
    save_blocks,
)


class TenantContentAdminBase(UnfoldModelAdmin):
    #: BLOCK_REGISTRY конкретної app.
    registry: list = []
    #: Модель-тенант (LandingSite / CorpSite).
    tenant_model = None
    #: Модель блоку (LandingBlock / CorpBlock) — FK на тенанта зветься `tenant`.
    block_model = None
    #: Атрибут на User: 'demo_corp' / 'demo_landing'.
    owner_attr = ''
    #: forms.ModelForm(instance=tenant) — кольори + стиль/hero-налаштування.
    settings_form_class = None
    #: Шаблон сторінки «Контент і стиль».
    template_name = ''
    #: Superuser без ?tenant= — список тенантів, не сліпий redirect.
    picker_template_name = ''
    page_labels: dict = {}
    title_text = _('Контент і стиль')

    def get_registry(self, tenant):
        return self.registry

    def has_module_permission(self, request):
        return request.user.is_superuser or self._owned_tenant(request) is not None

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _user_owned_tenant(self, user):
        if not getattr(user, 'is_authenticated', False):
            return None
        try:
            return getattr(user, self.owner_attr)
        except (ObjectDoesNotExist, AttributeError):
            return None

    def _owned_tenant(self, request):
        if request.user.is_superuser:
            tenant_id = request.GET.get('tenant')
            if tenant_id:
                return self.tenant_model.objects.filter(pk=tenant_id).first()
            tenants = list(self.tenant_model.objects.order_by('-created_at'))
            if len(tenants) == 1:
                return tenants[0]
            return None
        return self._user_owned_tenant(request.user)

    def _content_redirect(self, request, tenant):
        if request.user.is_superuser:
            return redirect(f'{request.path}?tenant={tenant.pk}')
        return redirect(request.path)

    def _picker_response(self, request):
        tenants = list(self.tenant_model.objects.order_by('-created_at'))
        if not tenants:
            messages.error(request, _('Немає жодного демо-сайту для редагування.'))
            return redirect('admin:index')
        context = {
            **self.admin_site.each_context(request),
            'title': self.title_text,
            'tenants': tenants,
        }
        return render(request, self.picker_template_name, context)

    def changelist_view(self, request, extra_context=None):
        tenant = self._owned_tenant(request)
        if tenant is None:
            if request.user.is_superuser:
                return self._picker_response(request)
            messages.error(request, _('До вашого акаунту не привʼязано жодного демо-сайту.'))
            return redirect('admin:index')

        if (
            request.method == 'GET'
            and request.user.is_superuser
            and request.GET.get('tenant') != str(tenant.pk)
        ):
            return redirect(f'{request.path}?tenant={tenant.pk}')

        registry = self.get_registry(tenant)
        ensure_registry_blocks(self.block_model, tenant, registry)
        block_form, blocks = build_block_form(registry, tenant)
        settings_form = self.settings_form_class(instance=tenant)

        if request.method == 'POST':
            block_form = type(block_form)(request.POST, request.FILES)
            settings_form = self.settings_form_class(request.POST, request.FILES, instance=tenant)

            if block_form.is_valid() and settings_form.is_valid():
                save_blocks(self.block_model, tenant, registry, block_form)
                settings_form.save()
                messages.success(request, _('Сайт оновлено.'))
                return self._content_redirect(request, tenant)

        context = {
            **self.admin_site.each_context(request),
            'title': self.title_text,
            'tenant': tenant,
            'block_form': block_form,
            'settings_form': settings_form,
            'block_groups': group_blocks_for_template(
                registry, self.page_labels, block_form, blocks,
            ),
        }
        return render(request, self.template_name, context)
