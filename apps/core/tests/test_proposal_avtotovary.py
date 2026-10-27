from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class AvtotovaryProposalTests(TestCase):
    slug = 'shop-avtotovary-ejja'

    def setUp(self):
        call_command('seed_proposal_avtotovary', verbosity=0)

    def test_packages_and_payment_from_pdf(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        self.assertFalse(proposal.corp_catalog)
        packages = list(proposal.packages.order_by('order'))
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0].price, Decimal('800.00'))
        self.assertIsNone(packages[0].price_high)
        self.assertEqual(packages[0].duration, '30 днів')
        self.assertFalse(packages[0].is_recommended)
        self.assertEqual(proposal.modules.count(), 6)
        self.assertEqual(proposal.specs.filter(kind='spec').count(), 3)
        self.assertEqual(proposal.specs.filter(kind='recommendation').count(), 4)
        payments = list(proposal.specs.filter(kind='payment').order_by('order'))
        self.assertEqual(len(payments), 3)
        self.assertIn('400 €', payments[0].title)
        self.assertIn('400 €', payments[1].title)
        self.assertIn('160 €/міс', payments[2].title)
        self.assertIn('до 5 платежів', payments[2].title)
        self.assertIn('пожиттєву гарантію на код', proposal.guarantee_html)
        self.assertIn('1 рік безкоштовної підтримки', proposal.guarantee_html)
        self.assertNotIn('ПОЖИТТЄВУ ГАРАНТІЮ на стабільність', proposal.guarantee_html)
        self.assertIn('office@prometeylabs.com', proposal.intro_html)
        # Вступ не обіцяє підбору під авто, якого немає в модулях (марка/модель).
        self.assertNotIn('підбір продукції під автомобіль', proposal.intro_html)
        self.assertNotIn('підбір продукції під автомобіль', proposal.lead)
        self.assertTrue(proposal.hero_image)
        self.assertTrue(proposal.hero_public_url)

    def test_seed_is_idempotent_single_demo(self):
        call_command('seed_proposal_avtotovary', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(Proposal.objects.filter(slug=self.slug).count(), 1)
        self.assertEqual(proposal.packages.count(), 1)
        self.assertEqual(proposal.modules.count(), 6)
        self.assertEqual(proposal.demo_shop.slug, 'avtotovary-551096')

    def test_page_noindex_with_standard_demo_shop(self):
        call_command('seed_proposal_avtotovary', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        site = proposal.demo_shop
        self.assertIsNotNone(site)
        self.assertEqual(site.name, 'Demo Shop')
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, 'не версія вашого сайту')
        self.assertContains(response, site.get_absolute_url())
        demo = self.client.get(site.get_absolute_url())
        self.assertEqual(demo.status_code, 200)
