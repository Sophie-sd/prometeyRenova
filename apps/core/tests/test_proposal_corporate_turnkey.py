from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class CorporateTurnkeyProposalTests(TestCase):
    slug = 'corporate-pid-klyuch-58wg'

    def setUp(self):
        call_command('seed_proposal_corporate_turnkey', verbosity=0)

    def test_packages_and_payment_from_pdf(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.CORPORATE)
        packages = list(proposal.packages.order_by('order'))
        self.assertEqual(len(packages), 3)
        self.assertEqual(
            [p.price for p in packages],
            [Decimal('900.00'), Decimal('1600.00'), Decimal('3500.00')],
        )
        self.assertEqual(
            [p.duration for p in packages],
            ['до 25–30 днів', 'до 30 днів', 'до 30–40 днів'],
        )
        self.assertTrue(packages[0].name.startswith('BASE'))
        self.assertTrue(packages[1].name.startswith('PREMIUM'))
        self.assertTrue(packages[2].name.startswith('PLATINUM'))
        self.assertEqual([p.is_recommended for p in packages], [False, True, False])
        self.assertEqual(proposal.modules.count(), 6)
        self.assertEqual(proposal.specs.filter(kind='spec').count(), 3)
        self.assertEqual(proposal.specs.filter(kind='recommendation').count(), 6)
        payments = list(proposal.specs.filter(kind='payment').order_by('order'))
        self.assertEqual(len(payments), 2)
        self.assertIn('50% (Передоплата)', payments[0].title)
        self.assertIn('50% (Фінальний платіж)', payments[1].title)
        self.assertTrue(proposal.specs.filter(title='Швидкість PageSpeed 90+').exists())
        self.assertIn('пожиттєву гарантію на код', proposal.guarantee_html)
        self.assertIn('1 рік безкоштовної підтримки', proposal.guarantee_html)
        self.assertNotIn('1 рік гарантії', proposal.guarantee_html)
        self.assertIn('office@prometeylabs.com', proposal.intro_html)

    def test_page_noindex_with_single_corp_demo(self):
        call_command('seed_proposal_corporate_turnkey', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertIsNotNone(proposal.demo_corp)
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, 'корпоративного сайту під ключ')
        self.assertContains(response, 'PLATINUM')
        self.assertContains(response, proposal.demo_corp.get_absolute_url())
        demo = self.client.get(proposal.demo_corp.get_absolute_url())
        self.assertEqual(demo.status_code, 200)
