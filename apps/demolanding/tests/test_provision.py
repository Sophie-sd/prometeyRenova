from datetime import date
from pathlib import Path

from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from apps.core.proposal_models import Proposal
from apps.demolanding.models import LandingSite
from apps.demolanding.services.provision import provision_demo_landing

ROOT = Path(__file__).resolve().parents[3]


class DemoLandingProvisionTests(TestCase):
    def test_provision_and_storefront(self):
        proposal = Proposal.objects.create(
            slug='landing-kp-a7f3',
            client_name='Landing Client',
            title='Landing KP',
            issued_on=date(2026, 8, 20),
            is_published=True,
            kind=Proposal.DemoKind.LANDING,
        )
        site = provision_demo_landing(proposal)
        site2 = provision_demo_landing(proposal)
        self.assertEqual(site.pk, site2.pk)
        self.assertEqual(LandingSite.objects.filter(proposal=proposal).count(), 1)
        response = Client().get(reverse('demolanding:home', kwargs={'slug': site.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')
        self.assertNotContains(response, 'GTM-K2FVPPTK')


class DemoLandingTemplateAdsTests(SimpleTestCase):
    def test_base_has_noindex_without_gtm(self):
        text = (ROOT / 'templates' / 'demolanding' / 'base.html').read_text(encoding='utf-8')
        self.assertIn('noindex, nofollow', text)
        self.assertNotIn('GTM-K2FVPPTK', text)
        self.assertNotIn('googletagmanager.com', text)
