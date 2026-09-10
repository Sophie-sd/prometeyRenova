"""Провізіонування demo-лендінгу з `Proposal`."""
from apps.demotenant.services.provision import deactivate_tenant, provision_tenant

from ..models import LandingSite
from ..seed import seed_demo_landing


def provision_demo_landing(proposal) -> LandingSite:
    return provision_tenant(
        proposal,
        model=LandingSite,
        proposal_field='proposal',
        username_prefix='landing',
        group_name='DemoLandingClient',
        seed_fn=seed_demo_landing,
    )


def deactivate_demo_landing(site: LandingSite) -> None:
    deactivate_tenant(site)
