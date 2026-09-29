from datetime import date

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.core.proposal_models import Proposal
from apps.demoshop.services.provision import provision_demo_shop

User = get_user_model()


def make_proposal(**overrides):
    defaults = {
        'slug': 'console-kp',
        'client_name': 'Console Client',
        'title': 'Console KP',
        'issued_on': date(2026, 9, 23),
        'is_published': True,
        'kind': Proposal.DemoKind.SHOP,
    }
    defaults.update(overrides)
    return Proposal.objects.create(**defaults)


class DemoConsoleTests(TestCase):
    def test_storefront_links_to_its_own_console(self):
        shop = provision_demo_shop(make_proposal())
        other = provision_demo_shop(make_proposal(slug='console-kp-b', client_name='Other'))
        response = Client().get(reverse('demoshop:home', kwargs={'shop_slug': shop.slug}))
        self.assertContains(response, shop.get_console_path())
        self.assertNotContains(response, other.get_console_path())
        self.assertNotContains(response, 'href="/admin/')

    def test_demo_client_is_sent_off_studio_admin(self):
        shop = provision_demo_shop(make_proposal(slug='bounce-kp', client_name='Bounce'))
        client = Client()
        client.force_login(shop.owner_user)
        response = client.get('/admin/demoshop/shopproduct/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(shop.get_console_path()))
        self.assertNotIn('/admin/', response.url)

    def test_staff_stays_on_studio_admin(self):
        staff = User.objects.create_superuser('studio', 'studio@example.com', 'studio-pass')
        client = Client()
        client.force_login(staff)
        response = client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/admin/')

    def test_unknown_console_key_is_404(self):
        response = Client().get('/k/this-key-does-not-exist-xx/')
        self.assertEqual(response.status_code, 404)

    def test_direct_console_url_opens_that_tenant(self):
        shop = provision_demo_shop(make_proposal(slug='direct-kp', client_name='Direct'))
        response = Client().get(shop.get_console_path(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user.pk, shop.owner_user_id)
        self.assertTrue(response.wsgi_request.path.startswith(shop.get_console_path()))
        self.assertContains(response, 'Мій магазин')
