"""Провізіонування demo-корпоративного сайту з `Proposal`."""
from apps.demotenant.services.provision import deactivate_tenant, provision_tenant

from ..models import CorpSite
from ..seed import seed_demo_corp


def provision_demo_corp(proposal) -> CorpSite:
    site = provision_tenant(
        proposal,
        model=CorpSite,
        proposal_field='proposal',
        username_prefix='site',
        group_name='DemoCorpClient',
        seed_fn=seed_demo_corp,
    )
    if site.has_catalog != proposal.corp_catalog:
        site.has_catalog = proposal.corp_catalog
        site.save()
        seed_demo_corp(site)
    return site


def deactivate_demo_corp(site: CorpSite) -> None:
    deactivate_tenant(site)
