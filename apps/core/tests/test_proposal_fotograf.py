from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class FotografProposalTests(TestCase):
    slug = 'corporate-fotograf-0763'

    def setUp(self):
        call_command('seed_proposal_fotograf', verbosity=0)

    def test_packages_and_payment_from_pdf(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.CORPORATE)
        self.assertTrue(proposal.corp_catalog)
        packages = list(proposal.packages.order_by('order'))
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0].price, Decimal('650.00'))
        self.assertIsNone(packages[0].price_high)
        self.assertEqual(packages[0].duration, '30 днів')
        self.assertFalse(packages[0].is_recommended)
        self.assertEqual(proposal.modules.count(), 6)
        self.assertEqual(proposal.specs.filter(kind='spec').count(), 3)
        self.assertEqual(proposal.specs.filter(kind='recommendation').count(), 4)
        payments = list(proposal.specs.filter(kind='payment').order_by('order'))
        self.assertEqual(len(payments), 3)
        self.assertIn('325 €', payments[0].title)
        self.assertIn('325 €', payments[1].title)
        self.assertIn('130 €/міс', payments[2].title)
        self.assertIn('до 5 платежів', payments[2].title)
        self.assertIn('пожиттєву гарантію на код', proposal.guarantee_html)
        self.assertIn('1 рік безкоштовної підтримки', proposal.guarantee_html)
        self.assertNotIn('ПОЖИТТЄВУ ГАРАНТІЮ на стабільність', proposal.guarantee_html)
        self.assertIn('office@prometeylabs.com', proposal.intro_html)
        self.assertTrue(proposal.hero_image)
        self.assertTrue(proposal.hero_public_url)

    def test_page_noindex_with_single_corp_demo(self):
        call_command('seed_proposal_fotograf', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        site = proposal.demo_corp
        self.assertIsNotNone(site)
        self.assertEqual(site.name, 'Demo Site')
        self.assertTrue(site.has_catalog)
        self.assertIsNone(getattr(proposal, 'demo_shop', None))
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, 'не версія вашого сайту')
        self.assertContains(response, site.get_absolute_url())
        demo = self.client.get(site.get_absolute_url())
        self.assertEqual(demo.status_code, 200)
