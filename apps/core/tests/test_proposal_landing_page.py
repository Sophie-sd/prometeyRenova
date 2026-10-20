from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class LandingPageProposalTests(TestCase):
    slug = 'landing-page-k8r2'

    def setUp(self):
        call_command('seed_proposal_landing_page', verbosity=0)

    def test_package_and_payment_from_pdf(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.LANDING)
        package = proposal.packages.get()
        self.assertEqual(package.price, Decimal('300.00'))
        self.assertEqual(package.duration, '14 днів')
        self.assertFalse(package.is_recommended)
        self.assertEqual(proposal.modules.count(), 6)
        payments = list(proposal.specs.filter(kind='payment').order_by('order'))
        self.assertIn('150 €', payments[0].title)
        self.assertIn('150 €', payments[1].title)
        self.assertIn('3 × 100 €', payments[2].title)
        self.assertIn('пожиттєву гарантію на код', proposal.guarantee_html)
        self.assertIn('1 рік безкоштовної підтримки', proposal.guarantee_html)
        self.assertIn('office@prometeylabs.com', proposal.intro_html)

    def test_page_noindex_with_single_landing_demo(self):
        call_command('seed_proposal_landing_page', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertIsNotNone(proposal.demo_landing)
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, proposal.demo_landing.get_absolute_url())
        demo = self.client.get(proposal.demo_landing.get_absolute_url())
        self.assertEqual(demo.status_code, 200)
