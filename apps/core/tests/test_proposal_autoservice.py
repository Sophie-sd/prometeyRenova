from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class AutoserviceProposalTests(TestCase):
    slug = 'landing-autoservice-2587'

    def setUp(self):
        call_command('seed_proposal_autoservice', verbosity=0)

    def test_packages_and_payment_from_pdf(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.LANDING)
        packages = list(proposal.packages.order_by('order'))
        self.assertEqual(len(packages), 3)
        self.assertEqual(packages[0].price, Decimal('250.00'))
        self.assertEqual(packages[0].duration, '10 днів')
        self.assertEqual(packages[1].price, Decimal('350.00'))
        self.assertEqual(packages[1].price_high, Decimal('500.00'))
        self.assertEqual(packages[1].duration, '5–7 днів')
        self.assertEqual(packages[2].price, Decimal('500.00'))
        self.assertEqual(packages[2].duration, '10 днів')
        self.assertIn('25.10.2026', packages[2].scope)
        self.assertEqual(proposal.modules.count(), 6)
        self.assertEqual(proposal.specs.filter(kind='recommendation').count(), 4)
        self.assertEqual(proposal.specs.filter(kind='spec').count(), 3)
        payments = list(proposal.specs.filter(kind='payment').order_by('order'))
        self.assertIn('50%', payments[0].title)
        self.assertIn('50%', payments[1].title)
        self.assertIn('83 €', payments[2].title)
        self.assertIn('пожиттєву гарантію на код', proposal.guarantee_html)
        self.assertIn('1 рік безкоштовної підтримки', proposal.guarantee_html)
        self.assertIn('office@prometeylabs.com', proposal.intro_html)

    def test_page_noindex_with_single_landing_demo(self):
        call_command('seed_proposal_autoservice', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertIsNotNone(proposal.demo_landing)
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, 'лендингу автосервісу')
        self.assertContains(response, proposal.demo_landing.get_absolute_url())
        demo = self.client.get(proposal.demo_landing.get_absolute_url())
        self.assertEqual(demo.status_code, 200)
