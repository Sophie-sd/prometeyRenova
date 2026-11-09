"""Імпорт КП в студійній адмінці після візиту в демо-кабінет.

Штат з can_import_proposal лишається штатом. Відвідувач демо не потрапляє
в студійну адмінку і не імпортує КП.
"""
import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.core.proposal_models import Proposal, ProposalImport
from apps.core.tests.test_proposal_import import make_zip
from apps.demoshop.services.provision import provision_demo_shop
from apps.demotenant.tests import make_proposal

TMP_MEDIA = tempfile.mkdtemp()
User = get_user_model()


@override_settings(MEDIA_ROOT=TMP_MEDIA, PROPOSAL_IMPORT_ENABLED=True)
class StaffProposalImportAccessTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        perm = Permission.objects.get(codename='can_import_proposal')
        self.staff = User.objects.create_user('valeria', 'valeria@example.com', 'pw', is_staff=True)
        self.staff.user_permissions.add(perm)
        self.noperm = User.objects.create_user('noperm', 'noperm@example.com', 'pw', is_staff=True)
        self.plain = User.objects.create_user('plain', 'plain@example.com', 'pw')
        self.shop = provision_demo_shop(make_proposal(slug='zoo-console', client_name='Zoo'))
        self.upload = reverse('admin:core_proposalimport_upload')
        self.changelist = reverse('admin:core_proposalimport_changelist')

    def _zip(self, slug):
        blob = io.BytesIO(make_zip({'slug': slug}))
        blob.name = 'kp.zip'
        return blob

    def test_staff_with_perm_opens_and_imports(self):
        client = Client()
        client.force_login(self.staff)
        self.assertEqual(client.get(self.changelist).status_code, 200)
        self.assertEqual(client.get(self.upload).status_code, 200)
        response = client.post(self.upload, {'package': self._zip('staff-kp')})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('/k/', response['Location'])
        self.assertTrue(Proposal.objects.filter(slug='staff-kp').exists())
        self.assertEqual(response.wsgi_request.user.pk, self.staff.pk)

    def test_staff_after_demo_console_still_imports(self):
        client = Client()
        client.force_login(self.staff)
        opened = client.get(self.shop.get_console_path(), follow=True)
        self.assertEqual(opened.status_code, 200)
        self.assertEqual(opened.wsgi_request.user.pk, self.shop.owner_user_id)
        page = client.get(self.changelist)
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.wsgi_request.user.pk, self.staff.pk)
        self.assertTrue(page.wsgi_request.path.startswith('/admin/'))
        response = client.post(self.upload, {'package': self._zip('after-console-kp')})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.wsgi_request.user.pk, self.staff.pk)
        self.assertTrue(Proposal.objects.filter(slug='after-console-kp').exists())

    def test_staff_after_demo_admin_login_still_imports(self):
        client = Client()
        client.force_login(self.staff)
        opened = client.get(
            reverse('demoshop:admin_login', kwargs={'shop_slug': self.shop.slug}),
            follow=True,
        )
        self.assertEqual(opened.status_code, 200)
        self.assertEqual(opened.wsgi_request.user.pk, self.shop.owner_user_id)
        page = client.get(self.upload)
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.wsgi_request.user.pk, self.staff.pk)
        self.assertTrue(page.wsgi_request.path.startswith('/admin/'))

    def test_demo_session_then_staff_login_imports(self):
        client = Client()
        client.get(self.shop.get_console_path(), follow=True)
        client.force_login(self.staff)
        page = client.get(self.changelist)
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.wsgi_request.user.pk, self.staff.pk)
        response = client.post(self.upload, {'package': self._zip('after-relogin-kp')})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Proposal.objects.filter(slug='after-relogin-kp').exists())

    def test_demo_visitor_cannot_open_studio_import(self):
        client = Client()
        client.get(self.shop.get_console_path(), follow=True)
        denied = client.get(self.upload)
        self.assertEqual(denied.status_code, 302)
        self.assertTrue(denied.url.startswith(self.shop.get_console_path()))
        self.assertNotIn('/admin/', denied.url)
        followed = client.get(self.changelist, follow=True)
        self.assertEqual(followed.status_code, 403)
        self.assertEqual(followed.wsgi_request.user.pk, self.shop.owner_user_id)
        self.assertFalse(ProposalImport.objects.exists())

    def test_demo_visitor_reaches_login_form_not_import(self):
        client = Client()
        client.get(self.shop.get_console_path(), follow=True)
        login = client.get('/admin/login/')
        self.assertEqual(login.status_code, 200)
        self.assertFalse(login.wsgi_request.user.is_authenticated)
        self.assertFalse(ProposalImport.objects.exists())

    def test_staff_without_perm_stays_denied_after_demo(self):
        client = Client()
        client.force_login(self.noperm)
        self.assertEqual(client.get(self.upload).status_code, 403)
        client.get(self.shop.get_console_path(), follow=True)
        denied = client.get(self.changelist)
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.wsgi_request.user.pk, self.noperm.pk)
        self.assertTrue(denied.wsgi_request.path.startswith('/admin/'))
        self.assertFalse(ProposalImport.objects.exists())

    def test_nonstaff_denied_even_after_demo(self):
        client = Client()
        client.force_login(self.plain)
        first = client.get(self.upload)
        self.assertEqual(first.status_code, 302)
        self.assertIn('/admin/login/', first.url)
        client.get(self.shop.get_console_path(), follow=True)
        bounced = client.get('/admin/')
        self.assertEqual(bounced.status_code, 302)
        self.assertTrue(bounced.url.startswith(self.shop.get_console_path()))
        self.assertEqual(bounced.wsgi_request.user.pk, self.shop.owner_user_id)
        followed = client.get(self.upload, follow=True)
        self.assertEqual(followed.status_code, 403)
        self.assertFalse(ProposalImport.objects.exists())
