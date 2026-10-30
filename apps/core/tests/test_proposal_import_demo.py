from pathlib import Path
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.proposal_import import import_proposal_package, import_warnings
from apps.core.proposal_models import Proposal
from apps.core.tests.test_proposal_import import TMP_MEDIA, make_zip


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class DemoAfterImportTests(TestCase):
    def test_corporate_gets_demo_corp(self):
        rec = import_proposal_package(make_zip({'slug': 'corp-demo-kp', 'kind': ''}, ptype='corporate'))
        p = Proposal.objects.get(pk=rec.proposal.pk)
        self.assertIsNotNone(p.demo_tenant)
        self.assertTrue(p.demo_tenant.is_active)
        self.assertEqual(p.demo_tenant._meta.model_name, 'corpsite')
        self.assertFalse(rec.demo_error)

    def test_landing_gets_demo(self):
        rec = import_proposal_package(make_zip({'slug': 'land-demo-kp'}))
        self.assertEqual(Proposal.objects.get(pk=rec.proposal.pk).demo_tenant._meta.model_name, 'landingsite')

    def test_create_demo_false_skips(self):
        rec = import_proposal_package(make_zip({'slug': 'nodemo-kp'}), create_demo=False)
        self.assertIsNone(Proposal.objects.get(pk=rec.proposal.pk).demo_tenant)

    def test_provision_failure_keeps_import(self):
        with mock.patch('apps.core.proposal_import.provision_demo_for', side_effect=RuntimeError('boom')):
            rec = import_proposal_package(make_zip({'slug': 'fail-demo-kp'}))
        self.assertTrue(Proposal.objects.filter(slug='fail-demo-kp').exists())
        self.assertIn('boom', rec.demo_error)
        rec.refresh_from_db()
        self.assertEqual(rec.status, 'success')
        self.assertTrue(any('демо не створено' in x for x in rec.log))

    def test_public_page_shows_demo(self):
        rec = import_proposal_package(make_zip({'slug': 'corp-pub-kp', 'kind': ''}, ptype='corporate'))
        html = self.client.get(reverse('proposal_detail', kwargs={'slug': rec.proposal.slug})).content.decode()
        self.assertIn('prop-demo', html)


@override_settings(MEDIA_ROOT=TMP_MEDIA, PROPOSAL_IMPORT_ENABLED=True)
class DemoAdminTests(TestCase):
    def test_checkbox_default_on_and_post(self):
        su = get_user_model().objects.create_superuser('su', 'su@x.cz', 'pw')
        self.client.force_login(su)
        url = reverse('admin:core_proposalimport_upload')
        self.assertIn('name="create_demo"', self.client.get(url).content.decode())
        self.assertIn('checked', self.client.get(url).content.decode().split('name="create_demo"')[0][-200:] +
                      self.client.get(url).content.decode().split('name="create_demo"')[1][:200])
        import io
        f = io.BytesIO(make_zip({'slug': 'adm-demo-kp', 'kind': ''}, ptype='corporate')); f.name = 'k.zip'
        self.client.post(url, {'package': f, 'create_demo': 'on'})
        self.assertIsNotNone(Proposal.objects.get(slug='adm-demo-kp').demo_tenant)

    def test_create_demo_action_still_works(self):
        su = get_user_model().objects.create_superuser('su2', 'su2@x.cz', 'pw')
        self.client.force_login(su)
        rec = import_proposal_package(make_zip({'slug': 'act-demo-kp', 'kind': ''}, ptype='corporate'), create_demo=False)
        self.client.post(reverse('admin:core_proposal_changelist'),
                         {'action': 'create_demo_action', '_selected_action': [rec.proposal.pk]})
        self.assertIsNotNone(Proposal.objects.get(pk=rec.proposal.pk).demo_tenant)


class WarningsAndDocsTests(TestCase):
    def test_soft_warnings(self):
        w = import_warnings({'lead': 'Робимо як Кодописець, PageSpeed 75', 'specs': [{'body': 'office@firma.ua'}]})
        self.assertEqual(len(w), 3)
        self.assertEqual(import_warnings({'lead': 'PageSpeed 95, info@firma.ua'}), [])

    def test_warnings_dont_block(self):
        with override_settings(MEDIA_ROOT=TMP_MEDIA):
            rec = import_proposal_package(make_zip({'slug': 'warn-kp', 'lead': 'office@x.ua PageSpeed 70'}),
                                          create_demo=False)
        self.assertEqual(len(rec.warnings), 2)

    def test_instruction_and_hints_have_demo_step(self):
        d = Path(__file__).resolve().parents[1] / 'kp_templates'
        self.assertIn('Одразу створити демо', (d / 'INSTRUCTION.md').read_text())
        for k in ('landing', 'shop', 'corporate', 'corporate-catalog'):
            self.assertIn('Створити/оновити демо', (d / f'template-{k}.HINTS.md').read_text())
            self.assertTrue((d / f'template-{k}.zip').exists())
