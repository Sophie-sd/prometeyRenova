"""Фабрики view-функцій, спільних для всіх demo-тенантів (`admin_access`,
`admin_login`, `theme_css`) — parity з `apps.demoshop.views` еквівалентами.
"""
from __future__ import annotations

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from .theme import render_theme_css

_AUTH_BACKEND = 'django.contrib.auth.backends.ModelBackend'


def make_admin_access_view(
    tenant_model,
    template_name: str,
    slug_kwarg: str = 'slug',
    *,
    registry: list | None = None,
):
    """Прокладка з логіном/паролем не потрібна — одразу в admin_login."""

    @require_GET
    def admin_access(request, **kwargs):
        get_object_or_404(tenant_model, slug=kwargs[slug_kwarg], is_active=True)
        return redirect(reverse(
            request.resolver_match.namespace + ':admin_login',
            kwargs={slug_kwarg: kwargs[slug_kwarg]},
        ))

    return admin_access


def make_admin_login_view(tenant_model, slug_kwarg: str = 'slug'):
    @require_GET
    def admin_login(request, **kwargs):
        """Логінить власника цього тенанта і відкриває Django admin."""
        tenant = get_object_or_404(tenant_model, slug=kwargs[slug_kwarg], is_active=True)
        owner = tenant.owner_user
        if owner is None or not owner.is_active:
            raise Http404('Клієнтський логін для цього демо ще не створено')

        if request.user.is_authenticated and request.user.pk != owner.pk:
            auth_logout(request)

        if not request.user.is_authenticated or request.user.pk != owner.pk:
            auth_login(request, owner, backend=_AUTH_BACKEND)

        return redirect('admin:index')

    return admin_login


def make_theme_css_view(tenant_model, slug_kwarg: str = 'slug'):
    @require_GET
    def theme_css(request, **kwargs):
        tenant = get_object_or_404(tenant_model, slug=kwargs[slug_kwarg], is_active=True)
        response = HttpResponse(render_theme_css(tenant), content_type='text/css')
        response['Cache-Control'] = 'public, max-age=300'
        return response

    return theme_css
