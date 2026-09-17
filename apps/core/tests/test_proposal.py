from datetime import date

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from apps.core.proposal_models import Proposal


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
