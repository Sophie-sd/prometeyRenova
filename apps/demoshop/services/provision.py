"""Провізіонування демо-магазину з комерційної пропозиції (КП)."""
from django.contrib.auth.models import Group, User

from ..models import DemoShop
from .seed import seed_demo_shop

DEMO_CLIENT_GROUP = 'DemoClient'


def _create_owner_user(shop: DemoShop) -> None:
    username = f'shop-{shop.slug}'[:150]
    password = DemoShop.generate_password()
    user, _created = User.objects.get_or_create(username=username)
    user.is_staff = True
    user.is_active = True
    user.set_password(password)
    user.save()

    group, _created = Group.objects.get_or_create(name=DEMO_CLIENT_GROUP)
    user.groups.add(group)

    shop.owner_user = user
    shop.demo_login = username
    shop.demo_password = password


def provision_demo_shop(proposal) -> DemoShop:
    """Ідемпотентно: reuse існуючого магазину під Proposal, інакше створити + seed.

    Повторний виклик дії «Створити демо-магазин» у Proposal admin безпечний —
    не плодить дублікати юзера/slug, лише доповнює/оновлює контент.
    """
    shop = DemoShop.objects.filter(proposal=proposal).first()
    if shop is None:
        shop = DemoShop(
            proposal=proposal,
            name=proposal.client_name or proposal.title,
            slug=DemoShop.generate_slug(proposal.client_name or proposal.title),
        )
        shop.save()

    if shop.owner_user_id is None:
        _create_owner_user(shop)

    if not shop.is_active:
        shop.is_active = True

    shop.save()
    seed_demo_shop(shop)
    return shop


def deactivate_demo_shop(shop: DemoShop) -> None:
    """Вимикає магазин і деактивує клієнтський логін — без «висячих» акаунтів."""
    shop.is_active = False
    shop.save()
    if shop.owner_user_id:
        User.objects.filter(pk=shop.owner_user_id).update(is_active=False)
