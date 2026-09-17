"""URL для Unfold «Дивитися сайт» — вітрина демо-тенанта, не головний сайт агенції."""
from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest


def resolve_view_site_url(request: HttpRequest) -> str:
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return '/'

    for attr in ('demo_landing', 'demo_shop', 'demo_corp'):
        try:
            tenant = getattr(user, attr)
        except (ObjectDoesNotExist, AttributeError):
            tenant = None
        if tenant is None:
            continue
        if getattr(tenant, 'is_active', True) is False:
            continue
        return tenant.get_absolute_url()

    return '/'
