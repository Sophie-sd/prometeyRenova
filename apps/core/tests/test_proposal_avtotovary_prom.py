from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal


class AvtotovaryPromProposalTests(TestCase):
    slug = 'shop-avtotovary-prom-rna3'

    def setUp(self):
        call_command('seed_proposal_avtotovary_prom', verbosity=0)

    def _all_text(self, proposal):
        parts = [proposal.title, proposal.lead, proposal.recommendations_lead,
                 proposal.intro_html, proposal.guarantee_html]
        parts += [f'{m.title} {m.description}' for m in proposal.modules.all()]
        parts += [f'{p.name} {p.scope}' for p in proposal.packages.all()]
        parts += [f'{s.title} {s.body}' for s in proposal.specs.all()]
        return ' '.join(parts)

    def test_packages_and_payment_from_pdf(self):
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        self.assertFalse(proposal.corp_catalog)
        packages = list(proposal.packages.order_by('order'))
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0].price, Decimal('920.00'))
        self.assertIsNone(packages[0].price_high)
        self.assertEqual(packages[0].duration, '30 днів')
        self.assertIn('Prom.ua', packages[0].name)
        self.assertEqual(proposal.modules.count(), 6)
        self.assertEqual(proposal.specs.filter(kind='spec').count(), 3)
        self.assertEqual(proposal.specs.filter(kind='recommendation').count(), 4)
        payments = list(proposal.specs.filter(kind='payment').order_by('order'))
        self.assertEqual(len(payments), 3)
        self.assertIn('460 €', payments[0].title)
        self.assertIn('460 €', payments[1].title)
        self.assertIn('184 €/міс', payments[2].title)
        self.assertIn('до 5 платежів', payments[2].title)
        self.assertIn('пожиттєву гарантію на код', proposal.guarantee_html)
        self.assertIn('1 рік безкоштовної підтримки', proposal.guarantee_html)
        self.assertIn('office@prometeylabs.com', proposal.intro_html)

    def test_migration_wording_rules(self):
        proposal = Proposal.objects.get(slug=self.slug)
        text = self._all_text(proposal)
        # 301-редиректи лише з умовою власного домену.
        self.assertIn('якщо на Prom був власний домен', text)
        for chunk in text.split('301')[1:]:
            self.assertIn('якщо на Prom був', chunk[:120])
        self.assertIn('товари, категорії', text)
        self.assertIn('сумісність з авто в картці товару', text)
        # Не називаємо магазин клієнта на Prom, не обіцяємо підбору під авто, без збоїв PDF.
        for banned in ('Cncprom', 'cncprom', 'точний підбір', 'підбір продукції під автомобіль',
                       'мови оплати', 'кодописн'):
            self.assertNotIn(banned, text)

    def test_seed_is_idempotent_single_demo(self):
        call_command('seed_proposal_avtotovary_prom', verbosity=0)
        proposal = Proposal.objects.get(slug=self.slug)
        self.assertEqual(Proposal.objects.filter(slug=self.slug).count(), 1)
        self.assertEqual(proposal.packages.count(), 1)
        self.assertEqual(proposal.modules.count(), 6)
        self.assertEqual(proposal.demo_shop.slug, 'avtotovary-prom-e06915')

    def test_page_noindex_with_standard_demo_shop(self):
        proposal = Proposal.objects.get(slug=self.slug)
        site = proposal.demo_shop
        self.assertIsNotNone(site)
        self.assertEqual(site.name, 'Demo Shop')
        response = self.client.get(f'/proposal/{self.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex')
        self.assertContains(response, 'не версія вашого сайту')
        self.assertContains(response, site.get_absolute_url())
        self.assertContains(response, '920')
        self.assertNotContains(response, 'Cncprom')
        demo = self.client.get(site.get_absolute_url())
        self.assertEqual(demo.status_code, 200)
