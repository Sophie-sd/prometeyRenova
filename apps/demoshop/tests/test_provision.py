from datetime import date
from pathlib import Path

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from apps.core.proposal_models import Proposal
from apps.demoshop.catalog_admin import ShopProductAdmin
from apps.demoshop.catalog_models import ShopProduct
from apps.demoshop.models import DemoShop
from apps.demoshop.services.provision import provision_demo_shop

User = get_user_model()
ROOT = Path(__file__).resolve().parents[3]


def make_proposal(**overrides):
    defaults = {
        'slug': 'shop-kp-a7f3',
        'client_name': 'Demo Shop Client',
        'title': 'Shop KP',
        'issued_on': date(2026, 8, 20),
        'is_published': True,
        'kind': Proposal.DemoKind.SHOP,
    }
    defaults.update(overrides)
    return Proposal.objects.create(**defaults)


class DemoShopProvisionTests(TestCase):
    def test_provision_is_idempotent(self):
        proposal = make_proposal()
        shop1 = provision_demo_shop(proposal)
        user_id = shop1.owner_user_id
        slug = shop1.slug
        shop2 = provision_demo_shop(proposal)
        self.assertEqual(shop1.pk, shop2.pk)
        self.assertEqual(user_id, shop2.owner_user_id)
        self.assertEqual(slug, shop2.slug)
        self.assertEqual(DemoShop.objects.filter(proposal=proposal).count(), 1)
        self.assertEqual(User.objects.filter(username=shop2.demo_login).count(), 1)
        self.assertTrue(shop2.products.exists())

    def test_storefront_is_noindex_and_alive(self):
        proposal = make_proposal()
        shop = provision_demo_shop(proposal)
        response = Client().get(
            reverse('demoshop:home', kwargs={'shop_slug': shop.slug}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')
        self.assertContains(response, 'noindex')
        self.assertNotContains(response, 'GTM-K2FVPPTK')

    def test_inactive_shop_is_404(self):
        proposal = make_proposal()
        shop = provision_demo_shop(proposal)
        shop.is_active = False
        shop.save(update_fields=['is_active'])
        response = Client().get(
            reverse('demoshop:home', kwargs={'shop_slug': shop.slug}),
        )
        self.assertEqual(response.status_code, 404)

    def test_client_queryset_is_scoped(self):
        shop_a = provision_demo_shop(make_proposal(slug='shop-a-kp', client_name='Shop A'))
        shop_b = provision_demo_shop(make_proposal(slug='shop-b-kp', client_name='Shop B'))
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = shop_a.owner_user
        admin = ShopProductAdmin(ShopProduct, AdminSite())
        qs = admin.get_queryset(request)
        self.assertTrue(qs.filter(shop=shop_a).exists())
        self.assertFalse(qs.filter(shop=shop_b).exists())

    def test_admin_login_opens_client_cms(self):
        shop = provision_demo_shop(make_proposal(slug='shop-login-kp', client_name='Login Shop'))
        client = Client()
        response = client.get(
            reverse('demoshop:admin_login', kwargs={'shop_slug': shop.slug}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user.pk, shop.owner_user_id)
        self.assertContains(response, 'Мій магазин')
        self.assertNotContains(response, 'CRM — Заявки')


class DemoShopTemplateAdsTests(SimpleTestCase):
    def test_base_has_noindex_without_gtm(self):
        text = (ROOT / 'templates' / 'demoshop' / 'base.html').read_text(encoding='utf-8')
        self.assertIn('noindex, nofollow', text)
        self.assertNotIn('gtm_head.html', text)
        self.assertNotIn('GTM-K2FVPPTK', text)
        self.assertNotIn('googletagmanager.com', text)
