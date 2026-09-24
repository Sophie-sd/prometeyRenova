from datetime import date
from decimal import Decimal

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from apps.core.proposal_models import Proposal
from apps.democorp.models import CorpSite
from apps.demolanding.models import LandingSite
from apps.demoshop.models import DemoShop


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

    def test_glass_seed_is_idempotent_without_demo(self):
        call_command('seed_proposal_glass', no_demo=True)
        call_command('seed_proposal_glass', no_demo=True)
        proposal = Proposal.objects.get(slug='shop-glass-a7f3')
        self.assertTrue(proposal.is_published)
        self.assertEqual(proposal.client_name, 'Фабрика обробки скла')
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        self.assertFalse(proposal.corp_catalog)
        self.assertEqual(proposal.packages.count(), 3)
        self.assertEqual(proposal.modules.count(), 6)
        names = list(
            proposal.packages.order_by('order').values_list('name', 'is_recommended')
        )
        self.assertEqual(names[0][0], 'Base — каталог і розрахунок')
        self.assertFalse(names[0][1])
        self.assertEqual(names[1][0], 'Premium — конфігуратор')
        self.assertTrue(names[1][1])
        self.assertEqual(names[2][0], 'Platinum — дилери й оплата')
        self.assertFalse(names[2][1])
        recs = proposal.specs.filter(kind='recommendation')
        self.assertEqual(recs.count(), 6)
        self.assertTrue(recs.filter(title__icontains='Калькулятор як лід').exists())
        self.assertFalse(
            proposal.modules.filter(description__icontains='splenko').exists()
        )
        self.assertFalse(DemoShop.objects.filter(proposal=proposal).exists())

    def test_glass_seed_provisions_classic_shop_and_stays_private(self):
        call_command('seed_proposal_glass')
        proposal = Proposal.objects.get(slug='shop-glass-a7f3')
        shop = DemoShop.objects.get(proposal=proposal)
        self.assertTrue(shop.is_active)

        client = Client()
        kp = client.get(reverse('proposal_detail', kwargs={'slug': proposal.slug}))
        self.assertEqual(kp.status_code, 200)
        self.assertContains(kp, 'Фабрика обробки скла')
        self.assertContains(kp, 'noindex')
        self.assertNotContains(kp, 'GTM-K2FVPPTK')
        self.assertNotContains(kp, 'googletagmanager.com')
        self.assertNotContains(kp, 'splenko')
        self.assertEqual(kp['X-Robots-Tag'], 'noindex, nofollow')
        self.assertContains(kp, 'id="prop-demo"')
        self.assertContains(kp, 'Демо вже зібране')
        self.assertContains(kp, shop.get_absolute_url())
        self.assertContains(kp, 'Переглянути демо магазину')

        demo = client.get(reverse('demoshop:home', kwargs={'shop_slug': shop.slug}))
        self.assertEqual(demo.status_code, 200)
        self.assertContains(demo, 'noindex')
        self.assertNotContains(demo, 'GTM-K2FVPPTK')
        self.assertNotContains(demo, 'googletagmanager.com')
        self.assertNotContains(demo, 'splenko')
        self.assertEqual(demo['X-Robots-Tag'], 'noindex, nofollow')

        sitemap = client.get('/sitemap.xml')
        self.assertEqual(sitemap.status_code, 200)
        body = sitemap.content.decode()
        self.assertNotIn('/proposal/', body)
        self.assertNotIn(proposal.slug, body)
        self.assertNotIn(shop.slug, body)

    def test_mangaly_seed_is_shop_and_private(self):
        call_command('seed_proposal_mangaly', no_demo=True)
        call_command('seed_proposal_mangaly', no_demo=True)
        proposal = Proposal.objects.get(slug='shop-mangaly-a7f3')
        self.assertEqual(proposal.client_name, 'E-Commerce Мангали & Метал')
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        self.assertEqual(proposal.issued_on.isoformat(), '2026-09-23')
        names = list(proposal.packages.order_by('order').values_list('name', 'price'))
        self.assertEqual(names[0], ('Базовий', Decimal('1150.00')))
        self.assertEqual(names[1], ('Преміум', Decimal('2000.00')))
        self.assertEqual(names[2], ('Платінум', Decimal('3500.00')))
        self.assertFalse(proposal.packages.filter(is_recommended=True).exists())
        self.assertEqual(proposal.modules.count(), 7)
        self.assertTrue(
            proposal.specs.filter(title__icontains='Нової Пошти').exists()
        )
        self.assertFalse(DemoShop.objects.filter(proposal=proposal).exists())

    def test_garden_seed_is_its_own_shop_page(self):
        call_command('seed_proposal_garden', no_demo=True)
        call_command('seed_proposal_garden', no_demo=True)
        proposal = Proposal.objects.get(slug='shop-sad-gorod-a7f3')
        self.assertEqual(proposal.client_name, 'Все для саду та городу')
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        self.assertEqual(proposal.issued_on.isoformat(), '2026-09-23')
        package = proposal.packages.get()
        self.assertEqual(package.name, 'Інтернет-магазин під ключ')
        self.assertEqual(package.price, Decimal('900.00'))
        self.assertIn('900–950', package.scope)
        self.assertFalse(package.is_recommended)
        self.assertEqual(proposal.modules.count(), 6)
        self.assertFalse(
            Proposal.objects.filter(
                slug='shop-mangaly-a7f3',
                client_name='Все для саду та городу',
            ).exists()
        )

    def test_ecom_seed_is_its_own_shop_page(self):
        call_command('seed_proposal_ecom', no_demo=True)
        call_command('seed_proposal_ecom', no_demo=True)
        proposal = Proposal.objects.get(slug='shop-ecom-a7f3')
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        self.assertEqual(proposal.issued_on.isoformat(), '2026-09-23')
        names = list(
            proposal.packages.order_by('order').values_list('name', 'price', 'is_recommended')
        )
        self.assertEqual(names[0], ('Базовий', Decimal('1000.00'), False))
        self.assertEqual(names[1], ('Преміум', Decimal('1500.00'), True))
        self.assertEqual(names[2], ('Платінум', Decimal('4000.00'), False))
        self.assertEqual(names[3], ('Перенесення реклами', Decimal('100.00'), False))
        self.assertIn('пожиттєву гарантію', proposal.guarantee_html)
        self.assertFalse(Proposal.objects.filter(slug='shop-sad-gorod-a7f3', title=proposal.title).exists())

    def test_ecom_b_seed_is_a_separate_shop_page(self):
        call_command('seed_proposal_ecom', no_demo=True)
        call_command('seed_proposal_ecom_b', no_demo=True)
        call_command('seed_proposal_ecom_b', no_demo=True)
        proposal = Proposal.objects.get(slug='shop-ecom-b7f3')
        names = list(
            proposal.packages.order_by('order').values_list('name', 'price', 'is_recommended')
        )
        self.assertEqual(names, [
            ('Базовий', Decimal('950.00'), False),
            ('Преміум', Decimal('1500.00'), True),
            ('Платінум', Decimal('3500.00'), False),
        ])
        kept = Proposal.objects.get(slug='shop-ecom-a7f3')
        self.assertEqual(kept.packages.get(name='Базовий').price, Decimal('1000.00'))

    def test_agro_prom_seed_is_its_own_shop_page(self):
        call_command('seed_proposal_agro_prom', no_demo=True)
        call_command('seed_proposal_agro_prom', no_demo=True)
        proposal = Proposal.objects.get(slug='shop-agro-prom-a7f3')
        self.assertEqual(proposal.client_name, 'Агромагазин з Prom.ua')
        self.assertEqual(proposal.kind, Proposal.DemoKind.SHOP)
        self.assertEqual(proposal.issued_on.isoformat(), '2026-09-24')
        names = list(
            proposal.packages.order_by('order').values_list('name', 'price', 'is_recommended')
        )
        self.assertEqual(names, [
            ('Базовий', Decimal('1000.00'), False),
            ('Преміум', Decimal('1500.00'), True),
            ('Платінум', Decimal('3200.00'), False),
        ])
        self.assertIn('пожиттєву гарантію', proposal.guarantee_html)
        self.assertEqual(proposal.modules.count(), 6)
        self.assertIn('seal-on-dark.webp', proposal.hero_public_url)
        self.assertFalse(DemoShop.objects.filter(proposal=proposal).exists())
        self.assertFalse(
            Proposal.objects.filter(
                slug='shop-sad-gorod-a7f3',
                client_name='Агромагазин з Prom.ua',
            ).exists()
        )

    def test_agro_prom_seed_provisions_one_classic_shop(self):
        call_command('seed_proposal_agro_prom')
        call_command('seed_proposal_agro_prom')
        proposal = Proposal.objects.get(slug='shop-agro-prom-a7f3')
        self.assertEqual(DemoShop.objects.filter(proposal=proposal).count(), 1)
        shop = DemoShop.objects.get(proposal=proposal)
        self.assertEqual(shop.name, 'Demo Shop')
        self.assertTrue(shop.is_active)
        self.assertTrue(shop.slug.startswith('agro-prom-'))

        client = Client()
        kp = client.get(reverse('proposal_detail', kwargs={'slug': proposal.slug}))
        self.assertEqual(kp.status_code, 200)
        self.assertContains(kp, 'Рекомендовано')
        self.assertContains(kp, 'не версія вашого сайту')
        self.assertContains(kp, 'noindex')
        self.assertEqual(kp['X-Robots-Tag'], 'noindex, nofollow')
        self.assertContains(kp, shop.get_absolute_url())

        demo = client.get(reverse('demoshop:home', kwargs={'shop_slug': shop.slug}))
        self.assertEqual(demo.status_code, 200)
        self.assertContains(demo, 'noindex')
        self.assertEqual(demo['X-Robots-Tag'], 'noindex, nofollow')

        sitemap = client.get('/sitemap.xml')
        body = sitemap.content.decode()
        self.assertNotIn(proposal.slug, body)
        self.assertNotIn(shop.slug, body)

    def test_sanitary_seed_is_its_own_corporate_page(self):
        call_command('seed_proposal_sanitary', no_demo=True)
        call_command('seed_proposal_sanitary', no_demo=True)
        proposal = Proposal.objects.get(slug='corporate-sanitary-a7f3')
        self.assertEqual(proposal.client_name, 'Служба санітарної обробки')
        self.assertEqual(proposal.kind, Proposal.DemoKind.CORPORATE)
        self.assertFalse(proposal.corp_catalog)
        self.assertEqual(proposal.issued_on.isoformat(), '2026-09-24')
        names = list(
            proposal.packages.order_by('order').values_list('name', 'price', 'is_recommended')
        )
        self.assertEqual(names, [
            ('Односторінковий лендінг', Decimal('350.00'), False),
            ('Корпоративний сайт', Decimal('500.00'), True),
        ])
        self.assertIn('пожиттєву гарантію', proposal.guarantee_html)
        self.assertFalse(CorpSite.objects.filter(proposal=proposal).exists())
        call_command('seed_proposal_agro_prom', no_demo=True)
        kept = Proposal.objects.get(slug='shop-agro-prom-a7f3')
        self.assertEqual(kept.packages.get(name='Базовий').price, Decimal('1000.00'))
        self.assertNotEqual(kept.title, proposal.title)

    def test_sanitary_seed_provisions_one_classic_site(self):
        call_command('seed_proposal_sanitary')
        call_command('seed_proposal_sanitary')
        proposal = Proposal.objects.get(slug='corporate-sanitary-a7f3')
        self.assertEqual(CorpSite.objects.filter(proposal=proposal).count(), 1)
        site = CorpSite.objects.get(proposal=proposal)
        self.assertEqual(site.name, 'Demo Site')
        self.assertFalse(site.has_catalog)
        self.assertTrue(site.slug.startswith('sanitary-'))

        client = Client()
        kp = client.get(reverse('proposal_detail', kwargs={'slug': proposal.slug}))
        self.assertEqual(kp.status_code, 200)
        self.assertContains(kp, 'Рекомендовано')
        self.assertContains(kp, 'не версія вашого сайту')
        self.assertContains(kp, 'Переглянути демо сайту')
        self.assertEqual(kp['X-Robots-Tag'], 'noindex, nofollow')
        self.assertContains(kp, site.get_absolute_url())

        demo = client.get(reverse('democorp:home', kwargs={'slug': site.slug}))
        self.assertEqual(demo.status_code, 200)
        self.assertEqual(demo['X-Robots-Tag'], 'noindex, nofollow')

        sitemap = client.get('/sitemap.xml')
        body = sitemap.content.decode()
        self.assertNotIn(proposal.slug, body)
        self.assertNotIn(site.slug, body)

    def test_advocate_seed_is_its_own_landing_page(self):
        call_command('seed_proposal_advocate', no_demo=True)
        call_command('seed_proposal_advocate', no_demo=True)
        proposal = Proposal.objects.get(slug='landing-advocate-a7f3')
        self.assertEqual(proposal.client_name, 'Військове право')
        self.assertEqual(proposal.kind, Proposal.DemoKind.LANDING)
        self.assertEqual(proposal.issued_on.isoformat(), '2026-09-24')
        names = list(
            proposal.packages.order_by('order').values_list('name', 'price', 'is_recommended')
        )
        self.assertEqual(names, [
            ('Базовий', Decimal('400.00'), False),
            ('Сайт + ADS', Decimal('600.00'), True),
        ])
        self.assertIn('пожиттєву гарантію', proposal.guarantee_html)
        self.assertEqual(proposal.cta_label, 'Почати проєкт')
        self.assertFalse(LandingSite.objects.filter(proposal=proposal).exists())
        call_command('seed_proposal_sanitary', no_demo=True)
        kept = Proposal.objects.get(slug='corporate-sanitary-a7f3')
        self.assertEqual(kept.packages.get(name='Корпоративний сайт').price, Decimal('500.00'))

    def test_advocate_seed_provisions_one_classic_landing(self):
        call_command('seed_proposal_advocate')
        call_command('seed_proposal_advocate')
        proposal = Proposal.objects.get(slug='landing-advocate-a7f3')
        self.assertEqual(LandingSite.objects.filter(proposal=proposal).count(), 1)
        site = LandingSite.objects.get(proposal=proposal)
        self.assertEqual(site.name, 'Demo Landing')
        self.assertTrue(site.slug.startswith('advocate-'))

        client = Client()
        kp = client.get(reverse('proposal_detail', kwargs={'slug': proposal.slug}))
        self.assertEqual(kp.status_code, 200)
        self.assertContains(kp, 'Рекомендовано')
        self.assertContains(kp, 'Переглянути демо лендінгу')
        self.assertContains(kp, 'не версія вашого сайту')
        self.assertEqual(kp['X-Robots-Tag'], 'noindex, nofollow')
        self.assertContains(kp, site.get_absolute_url())

        demo = client.get(reverse('demolanding:home', kwargs={'slug': site.slug}))
        self.assertEqual(demo.status_code, 200)
        self.assertEqual(demo['X-Robots-Tag'], 'noindex, nofollow')

        sitemap = client.get('/sitemap.xml')
        body = sitemap.content.decode()
        self.assertNotIn(proposal.slug, body)
        self.assertNotIn(site.slug, body)
