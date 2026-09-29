"""Окреме посилання кабінету на кожну КП.

Студійна адмінка лишається на `/admin/`. Клієнт демо туди не сідає:
його кабінет — це `/k/<console_key>/`, і `reverse('admin:…')` під час
цього запиту збирає посилання вже з цим префіксом.
"""
from __future__ import annotations

import re
import secrets
import types

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

CONSOLE_PREFIX = 'k'
_TOKEN_RE = re.compile(r'^/k/(?P<token>[A-Za-z0-9_-]{16,64})(?:/|$)')
_AUTH_BACKEND = 'django.contrib.auth.backends.ModelBackend'
_URLCONFS: dict[str, types.ModuleType] = {}
_TENANT_ATTRS = ('demo_shop', 'demo_landing', 'demo_corp')


def is_console_path(path: str) -> bool:
    return _TOKEN_RE.match(path or '') is not None


def path_for_key(console_key: str) -> str:
    return f'/{CONSOLE_PREFIX}/{console_key}/'


def assign_console_key(instance, update_fields=None):
    """Поставити ключ один раз. Повторний save його не крутить."""
    if instance.console_key:
        return update_fields
    instance.console_key = new_console_key()
    if update_fields is None:
        return None
    fields = set(update_fields)
    fields.add('console_key')
    return fields


def new_console_key() -> str:
    from apps.democorp.models import CorpSite
    from apps.demolanding.models import LandingSite
    from apps.demoshop.models import DemoShop

    models = (DemoShop, LandingSite, CorpSite)
    for _ in range(5):
        key = secrets.token_urlsafe(18)
        if not any(model.objects.filter(console_key=key).exists() for model in models):
            return key
    raise RuntimeError('Не вдалося зібрати унікальний ключ кабінету')


def resolve_active_tenant(token: str):
    from apps.democorp.models import CorpSite
    from apps.demolanding.models import LandingSite
    from apps.demoshop.models import DemoShop

    for model in (DemoShop, LandingSite, CorpSite):
        tenant = (
            model.objects.filter(console_key=token, is_active=True)
            .select_related('owner_user')
            .first()
        )
        if tenant is not None:
            return tenant
    return None


def tenant_for_user(user):
    if not getattr(user, 'is_authenticated', False):
        return None
    for attr in _TENANT_ATTRS:
        try:
            tenant = getattr(user, attr)
        except (ObjectDoesNotExist, AttributeError):
            tenant = None
        if tenant is not None and tenant.is_active and tenant.console_key:
            return tenant
    return None


def urlconf_for(token: str):
    module = _URLCONFS.get(token)
    if module is not None:
        return module
    from config.urls import build_urlpatterns

    module = types.ModuleType(f'demo_console_{token}')
    module.urlpatterns = build_urlpatterns(f'{CONSOLE_PREFIX}/{token}')
    _URLCONFS[token] = module
    return module


def _studio_admin_target(path: str, console_path: str) -> str:
    rest = path[len('/admin'):]
    base = console_path.rstrip('/')
    if rest in ('', '/'):
        return console_path
    if not rest.startswith('/'):
        rest = '/' + rest
    return base + rest


class ConsoleUrlconfMiddleware:
    """До Locale/Common: кабінет КП резолвиться своїм urlconf, не `/admin/`."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        match = _TOKEN_RE.match(request.path_info or '')
        if match:
            tenant = resolve_active_tenant(match.group('token'))
            if tenant is not None:
                request.demo_console_tenant = tenant
                request.urlconf = urlconf_for(tenant.console_key)
        return self.get_response(request)


class ConsoleAuthMiddleware(MiddlewareMixin):
    """Власник ключа входить у свій кабінет. З `/admin/` клієнта повертає на його URL."""

    def process_request(self, request):
        tenant = getattr(request, 'demo_console_tenant', None)
        if tenant is not None:
            return self._enter_console(request, tenant)

        path = request.path_info or ''
        if path != '/admin' and not path.startswith('/admin/'):
            return None
        owner_tenant = tenant_for_user(request.user)
        if owner_tenant is None:
            return None
        target = _studio_admin_target(path, owner_tenant.get_console_path())
        query = request.META.get('QUERY_STRING')
        if query:
            target = f'{target}?{query}'
        return HttpResponseRedirect(target)

    def _enter_console(self, request, tenant):
        owner = tenant.owner_user
        if owner is None or not owner.is_active:
            raise Http404('Клієнтський логін для цього демо ще не створено')
        if request.user.is_authenticated and request.user.pk == owner.pk:
            return None
        if request.user.is_authenticated:
            auth_logout(request)
        auth_login(request, owner, backend=_AUTH_BACKEND)
        if request.method in ('GET', 'HEAD'):
            return HttpResponseRedirect(request.get_full_path())
        return None
