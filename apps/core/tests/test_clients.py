from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client as DjangoTestClient, TestCase
from django.urls import reverse

from apps.core.mixins import homepage_clients
from apps.core.models import Client

MINIMAL_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00'
    b'\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


def make_client(name, order=0, is_active=True):
    logo = SimpleUploadedFile(f'{name.lower()}.png', MINIMAL_PNG, content_type='image/png')
    return Client.objects.create(
        name=name,
        logo=logo,
        order=order,
        is_active=is_active,
    )


class HomepageClientsTests(TestCase):
    def test_homepage_clients_returns_only_active_in_order(self):
        make_client('Alpha', order=2)
        make_client('Beta', order=1)
        make_client('Hidden', order=0, is_active=False)

        clients = list(homepage_clients())
        self.assertEqual([client.name for client in clients], ['Beta', 'Alpha'])

    def test_home_view_includes_home_clients(self):
        make_client('Play Vision', order=0)

        response = DjangoTestClient().get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('home_clients', response.context)
        self.assertEqual(
            [client.name for client in response.context['home_clients']],
            ['Play Vision'],
        )

    def test_home_page_renders_active_client_names(self):
        make_client('BeautyShop', order=0)

        response = DjangoTestClient().get(reverse('home'))
        self.assertContains(response, 'BeautyShop')

    def test_inactive_client_not_rendered(self):
        make_client('Visible Client', order=0, is_active=True)
        make_client('Hidden Client', order=1, is_active=False)

        response = DjangoTestClient().get(reverse('home'))
        self.assertContains(response, 'Visible Client')
        self.assertNotContains(response, 'Hidden Client')


class ClientAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin-pass-123',
        )
        self.client = DjangoTestClient()
        self.client.force_login(self.admin_user)

    def test_admin_changelist_accessible(self):
        response = self.client.get(reverse('admin:core_client_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_admin_add_form_accessible(self):
        response = self.client.get(reverse('admin:core_client_add'))
        self.assertEqual(response.status_code, 200)
