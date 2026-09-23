"""Базовий пакет shop-ecom-a7f3 — 1000 €, не 100 €."""

from decimal import Decimal

from django.db import migrations


def set_base_price(apps, schema_editor):
    Proposal = apps.get_model('core', 'Proposal')
    Package = apps.get_model('core', 'ProposalPackage')
    proposal = Proposal.objects.filter(slug='shop-ecom-a7f3').first()
    if proposal is None:
        return
    Package.objects.filter(proposal=proposal, name='Базовий').update(
        price=Decimal('1000.00'),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_proposal_guarantee_text'),
    ]

    operations = [
        migrations.RunPython(set_base_price, migrations.RunPython.noop),
    ]
