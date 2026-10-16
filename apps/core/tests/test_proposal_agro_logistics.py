from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class AgroLogisticsProposalTests(TestCase):
    slug = 'corporate-agro-logistics-x7p3'

    def setUp(self):
        call_command('seed_proposal_agro_logistics', verbosity=0)

    def test_package_and_payment_from_pdf(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.CORPORATE)
        package = proposal.packages.get()
        self.assertEqual(package.price, Decimal('750.00'))
        self.assertEqual(package.price_high, Decimal('800.00'))
        self.assertEqual(package.duration, '21–30 днів')
        self.assertFalse(package.is_recommended)
        self.assertIn('150 €', proposal.specs.filter(kind='payment').last().title)
        self.assertIn('1 рік', proposal.guarantee_html)
        self.assertNotIn('ожиттєв', proposal.guarantee_html)

    def test_page_noindex_with_single_corp_demo(self):
        call_command('seed_proposal_agro_logistics', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertIsNotNone(proposal.demo_corp)
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, proposal.demo_corp.get_absolute_url())
