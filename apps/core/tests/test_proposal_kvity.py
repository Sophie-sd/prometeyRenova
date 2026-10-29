from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal

LANDING = 'landing-kvity-t4m9'
SHOP = 'shop-kvity-r7l2'


class KvityProposalPairTests(TestCase):
    def setUp(self):
        call_command('seed_proposal_kvity_landing', verbosity=0)
        call_command('seed_proposal_kvity_shop', verbosity=0)

    def test_two_separate_prices(self):
        landing = Proposal.objects.get(slug=LANDING)
        shop = Proposal.objects.get(slug=SHOP)
        self.assertEqual(landing.kind, Proposal.DemoKind.LANDING)
        self.assertEqual(shop.kind, Proposal.DemoKind.SHOP)
        self.assertEqual([p.price for p in landing.packages.all()], [Decimal('250.00')])
        self.assertEqual([p.price for p in shop.packages.all()], [Decimal('1200.00')])
        for p in (landing, shop):
            self.assertIn('пожиттєву гарантію на код', p.guarantee_html)
            self.assertIn('1 рік безкоштовної підтримки', p.guarantee_html)

    def test_admin_only_in_shop(self):
        landing = Proposal.objects.get(slug=LANDING)
        names = ' '.join(m.title for m in landing.modules.all())
        self.assertNotIn('адмін', names.lower())
        self.assertIn('Без адмін-панелі', landing.packages.first().scope)
        shop = Proposal.objects.get(slug=SHOP)
        self.assertIn('Адмін-панель CMS', ' '.join(m.title for m in shop.modules.all()))

    def test_pages_show_both_demo_buttons(self):
        landing = Proposal.objects.get(slug=LANDING)
        shop = Proposal.objects.get(slug=SHOP)
        self.assertEqual(shop.demo_shop.name, 'Demo Shop')
        for p in (landing, shop):
            r = self.client.get(f'/proposal/{p.slug}/')
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, landing.demo_tenant.get_absolute_url())
            self.assertContains(r, shop.demo_tenant.get_absolute_url())
            self.assertContains(r, 'Інтернет-магазин')
            self.assertContains(r, 'Лендинг')
        self.assertEqual(self.client.get(shop.demo_tenant.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(landing.demo_tenant.get_absolute_url()).status_code, 200)
