"""Провізіонування demo-тенанта з `Proposal` — узагальнено з
`apps.demoshop.services.provision`. Ідемпотентно: reuse існуючого тенанта під
`Proposal`, інакше створити + seed.
"""
from __future__ import annotations

from typing import Callable

from django.contrib.auth.models import Group, User


def _create_owner_user(tenant, *, username_prefix: str, group_name: str) -> None:
    username = f'{username_prefix}-{tenant.slug}'[:150]
    password = type(tenant).generate_password()
    user, _created = User.objects.get_or_create(username=username)
    user.is_staff = True
    user.is_active = True
    user.set_password(password)
    user.save()

    group, _created = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)

    tenant.owner_user = user
    tenant.demo_login = username
    tenant.demo_password = password


def provision_tenant(
    proposal,
    *,
    model,
    proposal_field: str,
    username_prefix: str,
    group_name: str,
    seed_fn: Callable[[object], None],
):
    """Повторний виклик безпечний — не плодить дублікати юзера/slug, лише
    доповнює/оновлює контент (seed_fn — `update_or_create`-ідемпотентний).
    """
    tenant = model.objects.filter(**{proposal_field: proposal}).first()
    if tenant is None:
        tenant = model(
            **{proposal_field: proposal},
            name=proposal.client_name or proposal.title,
            slug=model.generate_slug(proposal.client_name or proposal.title),
        )
        tenant.save()

    if tenant.owner_user_id is None:
        _create_owner_user(tenant, username_prefix=username_prefix, group_name=group_name)

    if not tenant.is_active:
        tenant.is_active = True

    tenant.save()
    seed_fn(tenant)
    return tenant


def deactivate_tenant(tenant) -> None:
    """Вимикає тенанта і деактивує клієнтський логін — без «висячих» акаунтів."""
    tenant.is_active = False
    tenant.save()
    if tenant.owner_user_id:
        User.objects.filter(pk=tenant.owner_user_id).update(is_active=False)
