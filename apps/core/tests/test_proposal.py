from datetime import date

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from apps.core.proposal_models import Proposal
from apps.democorp.models import CorpSite


def make_proposal(**overrides):
    defaults = {
        'slug': 'test-kp-a7f3',
        'client_name': 'Test Client',
        'title': 'Test proposal title',
        'lead': 'Lead text',
        'issued_on': date(2026, 8, 20),
        'is_published': True,
        'kind': Proposal.DemoKind.SHOP,
        'order': 0,
    }
    defaults.update(overrides)
    return Proposal.objects.create(**defaults)


class ProposalPageTests(TestCase):
    def test_published_proposal_returns_200(self):
        proposal = make_proposal()
        response = Client().get(
            reverse('proposal_detail', kwargs={'slug': proposal.slug}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, proposal.title)
        self.assertContains(response, 'noindex')
        self.assertNotContains(response, 'id="prop-demo"')
        self.assertNotContains(response, 'GTM-K2FVPPTK')
        self.assertNotContains(response, 'googletagmanager.com')

    def test_unpublished_proposal_returns_404(self):
        proposal = make_proposal(is_published=False, slug='hidden-kp-a7f3')
        response = Client().get(
            reverse('proposal_detail', kwargs={'slug': proposal.slug}),
        )
        self.assertEqual(response.status_code, 404)

    def test_unknown_slug_returns_404(self):
        response = Client().get(
            reverse('proposal_detail', kwargs={'slug': 'missing-kp'}),
        )
        self.assertEqual(response.status_code, 404)

    def test_proposal_response_has_x_robots_tag(self):
        proposal = make_proposal()
        response = Client().get(
            reverse('proposal_detail', kwargs={'slug': proposal.slug}),
        )
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')

    def test_home_does_not_get_private_x_robots_tag(self):
        response = Client().get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('X-Robots-Tag', response)


class ProposalSeedTests(TestCase):
    def test_seed_is_idempotent_and_adds_visuals(self):
        call_command('seed_proposal_b2b_parts')
        call_command('seed_proposal_b2b_parts')
        proposal = Proposal.objects.get(slug='b2b-parts-platform-a7f3')
        self.assertTrue(proposal.is_published)
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        self.assertGreaterEqual(proposal.modules.count(), 1)
        self.assertGreaterEqual(proposal.highlights.count(), 1)
        self.assertGreaterEqual(proposal.arch_nodes.count(), 1)

    def test_corporate_seed_is_idempotent_without_demo(self):
        call_command('seed_proposal_corporate', no_demo=True)
        call_command('seed_proposal_corporate', no_demo=True)
        proposal = Proposal.objects.get(slug='corporate-liber-a7f3')
        self.assertTrue(proposal.is_published)
        self.assertEqual(proposal.client_name, 'Liber')
        self.assertEqual(proposal.kind, Proposal.DemoKind.CORPORATE)
        self.assertFalse(proposal.corp_catalog)
        self.assertEqual(proposal.packages.count(), 4)
        self.assertGreaterEqual(proposal.modules.count(), 6)
        names = list(proposal.packages.order_by('order').values_list('name', 'is_recommended'))
        self.assertEqual(names[0][0], 'Base — корпоративний сайт')
        self.assertFalse(names[0][1])
        self.assertEqual(names[1][0], 'Premium — маркетинговий старт')
        self.assertTrue(names[1][1])
        self.assertTrue(
            proposal.specs.filter(title__icontains='Міграція зі старого сайту').exists()
        )
        recs = proposal.specs.filter(kind='recommendation')
        self.assertEqual(recs.count(), 6)
        self.assertTrue(
            recs.filter(title__icontains='Код і доступи').exists()
        )
        self.assertFalse(CorpSite.objects.filter(proposal=proposal).exists())

    def test_corporate_seed_provisions_classic_demo_and_stays_private(self):
        call_command('seed_proposal_corporate')
        proposal = Proposal.objects.get(slug='corporate-liber-a7f3')
        site = CorpSite.objects.get(proposal=proposal)
        self.assertFalse(site.has_catalog)
        self.assertTrue(site.is_active)

        client = Client()
        kp = client.get(reverse('proposal_detail', kwargs={'slug': proposal.slug}))
        self.assertEqual(kp.status_code, 200)
        self.assertContains(kp, 'Liber')
        self.assertContains(kp, 'noindex')
        self.assertNotContains(kp, 'GTM-K2FVPPTK')
        self.assertNotContains(kp, 'googletagmanager.com')
        self.assertEqual(kp['X-Robots-Tag'], 'noindex, nofollow')
        self.assertContains(kp, 'id="prop-demo"')
        self.assertContains(kp, 'Демо вже зібране')
        self.assertContains(kp, site.get_absolute_url())
        self.assertContains(kp, 'Переглянути демо сайту')

        demo = client.get(reverse('democorp:home', kwargs={'slug': site.slug}))
        self.assertEqual(demo.status_code, 200)
        self.assertContains(demo, 'noindex')
        self.assertNotContains(demo, 'GTM-K2FVPPTK')
        self.assertNotContains(demo, 'googletagmanager.com')
        self.assertEqual(demo['X-Robots-Tag'], 'noindex, nofollow')

        sitemap = client.get('/sitemap.xml')
        self.assertEqual(sitemap.status_code, 200)
        body = sitemap.content.decode()
        self.assertNotIn('/proposal/', body)
        self.assertNotIn('/demo-site/', body)
        self.assertNotIn(proposal.slug, body)
        self.assertNotIn(site.slug, body)
