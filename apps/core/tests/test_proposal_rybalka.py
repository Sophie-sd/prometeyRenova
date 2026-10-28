from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class RybalkaProposalTests(TestCase):
    slug = 'shop-rybalka-rh1k'

    def setUp(self):
        call_command('seed_proposal_rybalka', verbosity=0)

    def _all_text(self, proposal):
        parts = [proposal.title, proposal.lead, proposal.recommendations_lead,
                 proposal.intro_html, proposal.guarantee_html]
        parts += [f'{m.title} {m.description}' for m in proposal.modules.all()]
        parts += [f'{p.name} {p.scope}' for p in proposal.packages.all()]
        parts += [f'{s.title} {s.body}' for s in proposal.specs.all()]
        return ' '.join(parts)

    def test_price_payment_guarantee(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        packages = list(proposal.packages.all())
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0].price, Decimal('950.00'))
        self.assertEqual(packages[0].duration, '30 днів')
        payments = list(proposal.specs.filter(kind='payment').order_by('order'))
        self.assertIn('475 €', payments[0].title)
        self.assertIn('475 €', payments[1].title)
        self.assertIn('190 €/міс', payments[2].title)
        self.assertIn('пожиттєву гарантію на код', proposal.guarantee_html)
        self.assertIn('1 рік безкоштовної підтримки', proposal.guarantee_html)

    def test_wording_rules(self):
        text = self._all_text(Proposal.objects.get(slug=self.slug))
        self.assertIn('типом риби', text)
        self.assertIn('Товари, фото, описи й ціни заводить клієнт', text)
        self.assertIn('Домен і хостинг купує й оплачує клієнт', text)
        self.assertIn('Оптові ціни', text)
        for banned in ('оптового продажу', 'мови оплати', 'кодописн', 'PageSpeed 90'):
            self.assertNotIn(banned, text)

    def test_page_and_standard_demo(self):
        call_command('seed_proposal_rybalka', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        site = proposal.demo_shop
        self.assertEqual(site.slug, 'rybalka-8a6235')
        self.assertEqual(site.name, 'Demo Shop')
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, site.get_absolute_url())
        self.assertContains(response, '950')
        self.assertEqual(self.client.get(site.get_absolute_url()).status_code, 200)
