from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class ZootovaryProposalTests(TestCase):
    slug = 'internet-mahazyn-zootovariv-cxpo'

    def setUp(self):
        call_command('seed_proposal_zootovary', verbosity=0)

    def test_packages_and_payment_from_pdf(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        packages = list(proposal.packages.order_by('order'))
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0].price, Decimal('800.00'))
        self.assertEqual(packages[0].price_high, Decimal('900.00'))
        self.assertEqual(packages[0].duration, '30 днів')
        self.assertEqual(proposal.modules.count(), 6)
        self.assertEqual(proposal.specs.filter(kind='recommendation').count(), 4)
        payments = list(proposal.specs.filter(kind='payment').order_by('order'))
        self.assertIn('50%', payments[0].title)
        self.assertIn('50%', payments[1].title)
        self.assertIn('160–180 €', payments[2].title)
        self.assertIn('пожиттєву гарантію на код', proposal.guarantee_html)
        self.assertIn('1 рік безкоштовної підтримки', proposal.guarantee_html)
        self.assertIn('office@prometeylabs.com', proposal.intro_html)

    def test_page_noindex_with_standard_demo_shop(self):
        call_command('seed_proposal_zootovary', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        shop = proposal.demo_shop
        self.assertIsNotNone(shop)
        self.assertGreater(shop.products.count(), 0)
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, 'зоотоварів')
        self.assertContains(response, shop.get_absolute_url())
        demo = self.client.get(shop.get_absolute_url())
        self.assertEqual(demo.status_code, 200)
