"""Фабрики view-функцій, спільних для всіх demo-тенантів (`admin_access`,
`admin_login`, `theme_css`) — parity з `apps.demoshop.views` еквівалентами.
"""
from __future__ import annotations

from django.contrib.auth import logout as auth_logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from .theme import render_theme_css


def make_admin_access_view(tenant_model, template_name: str, slug_kwarg: str = 'slug'):
    @require_GET
    def admin_access(request, **kwargs):
        tenant = get_object_or_404(tenant_model, slug=kwargs[slug_kwarg], is_active=True)
        # 'site' — щоб публічний base.html (extends) резолвив ту саму
        # змінну, що й на вітрині; 'tenant' — узагальнена назва для CMS-шаблонів.
        return render(request, template_name, {'tenant': tenant, 'site': tenant})

    return admin_access


def make_admin_login_view(tenant_model, slug_kwarg: str = 'slug'):
    @require_GET
    def admin_login(request, **kwargs):
        """Веде саме у скоуп власника ЦЬОГО тенанта."""
        tenant = get_object_or_404(tenant_model, slug=kwargs[slug_kwarg], is_active=True)
        if request.user.is_authenticated and request.user.pk != tenant.owner_user_id:
            auth_logout(request)
        admin_index = reverse('admin:index')
        return redirect(f'{reverse("admin:login")}?next={admin_index}')

    return admin_login


def make_theme_css_view(tenant_model, slug_kwarg: str = 'slug'):
    @require_GET
    def theme_css(request, **kwargs):
        tenant = get_object_or_404(tenant_model, slug=kwargs[slug_kwarg], is_active=True)
        response = HttpResponse(render_theme_css(tenant), content_type='text/css')
        response['Cache-Control'] = 'public, max-age=300'
        return response

    return theme_css
