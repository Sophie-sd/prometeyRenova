from datetime import date
from pathlib import Path

from django.contrib.admin.sites import AdminSite
from django.test import Client, RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from apps.core.proposal_models import Proposal
from apps.democorp.collection_admin import CorpLeadAdmin
from apps.democorp.lead_models import CorpLead
from apps.democorp.services.provision import provision_demo_corp

ROOT = Path(__file__).resolve().parents[3]


class DemoCorpProvisionTests(TestCase):
    def _proposal(self, **overrides):
        defaults = {
            'slug': 'corp-kp-a7f3',
            'client_name': 'Corp Client',
            'title': 'Corp KP',
            'issued_on': date(2026, 8, 20),
            'is_published': True,
            'kind': Proposal.DemoKind.CORPORATE,
            'corp_catalog': False,
        }
        defaults.update(overrides)
        return Proposal.objects.create(**defaults)

    def test_provision_without_catalog(self):
        proposal = self._proposal()
        site = provision_demo_corp(proposal)
        self.assertFalse(site.has_catalog)
        self.assertFalse(site.products.exists())
        response = Client().get(reverse('democorp:home', kwargs={'slug': site.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')
        self.assertNotContains(response, 'GTM-K2FVPPTK')

    def test_catalog_flag_seeds_products(self):
        proposal = self._proposal(slug='corp-cat-kp', corp_catalog=True)
        site = provision_demo_corp(proposal)
        self.assertTrue(site.has_catalog)
        self.assertTrue(site.products.exists())

    def test_client_does_not_see_foreign_leads(self):
        site_a = provision_demo_corp(self._proposal(slug='corp-a-kp', client_name='Corp A'))
        site_b = provision_demo_corp(self._proposal(slug='corp-b-kp', client_name='Corp B'))
        CorpLead.objects.create(tenant=site_b, name='Other', phone='+380000000000')
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = site_a.owner_user
        admin = CorpLeadAdmin(CorpLead, AdminSite())
        qs = admin.get_queryset(request)
        self.assertFalse(qs.filter(tenant=site_b).exists())
        self.assertFalse(qs.filter(pk__in=site_b.leads.values_list('pk', flat=True)).exists())


class DemoCorpTemplateAdsTests(SimpleTestCase):
    def test_base_has_noindex_without_gtm(self):
        text = (ROOT / 'templates' / 'democorp' / 'base.html').read_text(encoding='utf-8')
        self.assertIn('noindex, nofollow', text)
        self.assertNotIn('GTM-K2FVPPTK', text)
        self.assertNotIn('googletagmanager.com', text)
