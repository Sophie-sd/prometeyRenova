import io
import json
import shutil
import tempfile
import zipfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.core.proposal_import import (
    ImportError_, import_proposal_package, parse_package, rollback_import, soft_delete_proposal, restore_proposal,
)
from apps.core.proposal_models import Proposal, ProposalImport

TMP_MEDIA = tempfile.mkdtemp()


def img_bytes(fmt='WEBP', size=(20, 20)):
    b = io.BytesIO()
    Image.new('RGB', size, 'red').save(b, fmt)
    return b.getvalue()


def make_zip(data=None, manifest=None, extra=None, ptype='landing'):
    data = data or {}
    base = {'slug': 'test-kp-import', 'client_name': 'Клієнт', 'title': 'КП тест', 'issued_on': '2026-10-29',
            'intro_html': '<p>ok</p><script>alert(1)</script>', 'is_published': True,
            'highlights': [{'order': 0, 'title': 'Пункт'}],
            'packages': [{'order': 0, 'name': 'База', 'price': '950.00', 'currency': '€'}],
            'specs': [{'kind': 'spec', 'order': 0, 'title': 'ТЗ', 'body': '<b>x</b><img src=x onerror=1>'}],
            'hero_image': 'media/hero.webp'}
    base.update(data)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json', json.dumps(manifest or {'type': ptype, 'version': 1, 'title': 't', 'created': '2026-10-29'}))
        z.writestr('proposal.json', json.dumps(base))
        if base.get('hero_image'):
            z.writestr('media/hero.webp', img_bytes())
        for k, v in (extra or {}).items():
            z.writestr(k, v)
    return buf.getvalue()


@override_settings(MEDIA_ROOT=TMP_MEDIA, PROPOSAL_IMPORT_ENABLED=True)
class ImportServiceTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def test_import_creates_and_sanitizes(self):
        rec = import_proposal_package(make_zip(), original_name='a.zip')
        p = rec.proposal
        self.assertEqual(p.source, Proposal.Source.IMPORT)
        self.assertNotIn('script', p.intro_html)
        self.assertNotIn('onerror', p.specs.first().body)
        self.assertEqual(p.hero_images.filter(is_active=True).count(), 1)
        self.assertTrue(p.hero_images.first().image.name.startswith('proposals/'))
        self.assertEqual(rec.version, 1)

    def test_dry_run_writes_nothing(self):
        import_proposal_package(make_zip(), dry_run=True)
        self.assertFalse(Proposal.objects.filter(slug='test-kp-import').exists())

    def test_duplicate_sha_rejected(self):
        blob = make_zip()
        import_proposal_package(blob)
        with self.assertRaises(ImportError_):
            import_proposal_package(blob)

    def test_seed_proposal_not_overwritten(self):
        Proposal.objects.create(slug='test-kp-import', client_name='x', title='x', issued_on='2026-01-01')
        with self.assertRaises(ImportError_):
            import_proposal_package(make_zip())

    def test_bad_inputs(self):
        for blob in (b'notzip', make_zip({'slug': 'admin'}), make_zip({'slug': 'A_B'}),
                     make_zip(manifest={'type': 'evil', 'version': 1}),
                     make_zip(extra={'../x.png': 'x'}), make_zip(extra={'media/x.svg': '<svg/>'}),
                     make_zip(extra={'media/fake.png': img_bytes('JPEG')})):
            with self.assertRaises(ImportError_):
                parse_package(blob)

    def test_big_image_rejected(self):
        with self.assertRaises(ImportError_):
            parse_package(make_zip(extra={'media/big.png': img_bytes('PNG', (2600, 10))}))

    def test_corporate_catalog_type(self):
        rec = import_proposal_package(make_zip({'slug': 'corp-cat-kp', 'kind': ''}, ptype='corporate_catalog'))
        self.assertEqual(rec.proposal.kind, Proposal.DemoKind.CORPORATE)
        self.assertTrue(rec.proposal.corp_catalog)

    def test_reimport_and_rollback(self):
        import_proposal_package(make_zip({'title': 'V1'}))
        rec2 = import_proposal_package(make_zip({'title': 'V2'}))
        self.assertEqual(rec2.version, 2)
        rb = rollback_import(rec2)
        self.assertEqual(rb.kind, ProposalImport.Kind.ROLLBACK)
        self.assertEqual(rb.version, 3)
        self.assertEqual(rb.rollback_of, rec2)
        self.assertEqual(Proposal.objects.get(slug='test-kp-import').title, 'V1')

    def test_soft_delete_restore(self):
        p = import_proposal_package(make_zip()).proposal
        soft_delete_proposal(p)
        p.refresh_from_db()
        self.assertIsNotNone(p.deleted_at)
        self.assertFalse(p.is_published)
        restore_proposal(p)
        p.refresh_from_db()
        self.assertIsNone(p.deleted_at)


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class ProtectedMediaTests(TestCase):
    def setUp(self):
        import os
        os.makedirs(f'{TMP_MEDIA}/proposals/x', exist_ok=True)
        os.makedirs(f'{TMP_MEDIA}/proposal_imports', exist_ok=True)
        for name, body in (('proposals/x/a.webp', img_bytes()), ('proposals/x/a.html', b'<h1>'),
                           ('proposals/x/a.SVG', b'<svg/>'), ('proposals/x/a.js', b'1'),
                           ('proposal_imports/p.zip', b'z'), ('other.txt', b'ok')):
            with open(f'{TMP_MEDIA}/{name}', 'wb') as f:
                f.write(body)

    def test_rules(self):
        r = self.client.get('/media/proposals/x/a.webp')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['X-Content-Type-Options'], 'nosniff')
        for u in ('/media/proposals/x/a.html', '/media/proposals/x/a.SVG', '/media/proposals/x/a.js',
                  '/media/proposal_imports/p.zip', '/media/PROPOSAL_IMPORTS/p.zip'):
            self.assertEqual(self.client.get(u).status_code, 404, u)
        self.assertEqual(self.client.get('/media/other.txt').status_code, 200)


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class AdminFlagTests(TestCase):
    def setUp(self):
        self.su = get_user_model().objects.create_superuser('su', 'su@x.cz', 'pw')
        self.staff = get_user_model().objects.create_user('st', 'st@x.cz', 'pw', is_staff=True)

    def test_flag_off_forbids(self):
        self.client.force_login(self.su)
        with override_settings(PROPOSAL_IMPORT_ENABLED=False):
            self.assertEqual(self.client.get(reverse('admin:core_proposalimport_upload')).status_code, 403)

    def test_staff_without_perm_forbidden(self):
        self.client.force_login(self.staff)
        with override_settings(PROPOSAL_IMPORT_ENABLED=True):
            self.assertEqual(self.client.get(reverse('admin:core_proposalimport_upload')).status_code, 403)

    def test_upload_and_templates(self):
        self.client.force_login(self.su)
        with override_settings(PROPOSAL_IMPORT_ENABLED=True):
            self.assertEqual(self.client.get(reverse('admin:core_proposalimport_upload')).status_code, 200)
            f = io.BytesIO(make_zip())
            f.name = 'kp.zip'
            r = self.client.post(reverse('admin:core_proposalimport_upload'), {'package': f})
            self.assertEqual(r.status_code, 302)
            self.assertTrue(Proposal.objects.filter(slug='test-kp-import').exists())
            for k in ('landing', 'shop', 'corporate', 'corporate_catalog', 'instruction'):
                self.assertEqual(self.client.get(reverse('admin:core_proposalimport_template', args=[k])).status_code, 200)

    def test_soft_delete_requires_slug(self):
        self.client.force_login(self.su)
        with override_settings(PROPOSAL_IMPORT_ENABLED=True):
            p = import_proposal_package(make_zip()).proposal
            url = reverse('admin:core_proposalimport_soft_delete', args=[p.pk])
            self.client.post(url, {'slug': 'wrong', 'confirm': 'on'})
            p.refresh_from_db()
            self.assertIsNone(p.deleted_at)
            self.client.post(url, {'slug': p.slug})
            p.refresh_from_db()
            self.assertIsNone(p.deleted_at)
            self.client.post(url, {'slug': p.slug, 'confirm': 'on'})
            p.refresh_from_db()
            self.assertIsNotNone(p.deleted_at)


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class CommandTests(TestCase):
    def test_export_and_purge(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        out = tempfile.mkdtemp()
        call_command('export_proposal_templates', out=out)
        p = import_proposal_package(make_zip()).proposal
        call_command('export_proposal_package', p.slug, out=f'{out}/x.zip')
        parse_package(open(f'{out}/x.zip', 'rb').read())
        with self.assertRaises(CommandError):
            call_command('purge_proposal', slug=p.slug, confirm=True)
        soft_delete_proposal(p)
        call_command('purge_proposal', slug=p.slug)
        self.assertTrue(Proposal.objects.filter(slug=p.slug).exists())
        call_command('purge_proposal', slug=p.slug, confirm=True)
        self.assertFalse(Proposal.objects.filter(slug=p.slug).exists())
        shutil.rmtree(out, ignore_errors=True)


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class RestorePublicTests(TestCase):
    def test_soft_delete_then_restore_public_200(self):
        p = import_proposal_package(make_zip()).proposal
        url = reverse('proposal_detail', kwargs={'slug': p.slug})
        self.assertEqual(self.client.get(url).status_code, 200)
        soft_delete_proposal(p)
        self.assertEqual(self.client.get(url).status_code, 404)
        restore_proposal(p)
        p.refresh_from_db()
        self.assertTrue(p.is_published)
        self.assertEqual(self.client.get(url).status_code, 200)
