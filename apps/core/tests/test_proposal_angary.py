from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class AngaryProposalTests(TestCase):
    slug = 'corporate-angary-clg5'

    def setUp(self):
        call_command('seed_proposal_angary', verbosity=0)

    def test_packages_and_payment_from_pdf(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.CORPORATE)
        packages = list(proposal.packages.order_by('order'))
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0].price, Decimal('450.00'))
        self.assertEqual(packages[0].price_high, Decimal('500.00'))
        self.assertEqual(packages[0].duration, '14 днів')
        self.assertEqual(proposal.modules.count(), 6)
        self.assertEqual(proposal.specs.filter(kind='recommendation').count(), 4)
        payments = list(proposal.specs.filter(kind='payment').order_by('order'))
        self.assertIn('50%', payments[0].title)
        self.assertIn('50%', payments[1].title)
        self.assertIn('150–166 €', payments[2].title)
        self.assertTrue(proposal.specs.filter(title='Google PageSpeed 90+').exists())
        self.assertIn('пожиттєву гарантію на код', proposal.guarantee_html)
        self.assertIn('1 рік безкоштовної підтримки', proposal.guarantee_html)
        self.assertIn('office@prometeylabs.com', proposal.intro_html)

    def test_page_noindex_with_single_corp_demo(self):
        call_command('seed_proposal_angary', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertIsNotNone(proposal.demo_corp)
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, 'ангарів')
        self.assertContains(response, proposal.demo_corp.get_absolute_url())
        demo = self.client.get(proposal.demo_corp.get_absolute_url())
        self.assertEqual(demo.status_code, 200)
