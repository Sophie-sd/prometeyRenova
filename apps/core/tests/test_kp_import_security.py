"""Security/Launch: атак-тести T01–T22 для імпорту КП (kp-upload-hardening.md).

Fail-closed: кожна атака → ImportError_/403/404, 0 нових Proposal/ProposalImport, 0 файлів у MEDIA_ROOT.
Ізоляція: tmp MEDIA_ROOT (не видаляється — правило Олега «нічого не видаляти»), без мережі/SMS/email.
"""
import io
import json
import os
import stat
import tempfile
import zipfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.core.proposal_import import ImportError_, clean_html, import_proposal_package, parse_package
from apps.core.proposal_models import Proposal, ProposalImport

TMP_MEDIA = tempfile.mkdtemp(prefix='kp-sec-media-')


def img(fmt='WEBP', size=(16, 16), exif=None):
    b = io.BytesIO()
    im = Image.new('RGB', size, 'red')
    kw = {'exif': exif} if exif is not None else {}
    im.save(b, fmt, **kw)
    return b.getvalue()


def base_data(**kw):
    d = {'slug': 'sec-kp-test', 'client_name': 'Клієнт', 'title': 'КП', 'issued_on': '2026-10-29',
         'intro_html': '<p>ok</p>', 'is_published': False, 'hero_image': 'media/hero.webp'}
    d.update(kw)
    return d


def zbytes(entries, comp=zipfile.ZIP_DEFLATED):
    """entries: list of (ZipInfo|name, bytes)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', comp) as z:
        for n, v in entries:
            z.writestr(n, v)
    return buf.getvalue()


def pkg(data=None, extra=(), hero=None):
    data = data or base_data()
    e = [('manifest.json', json.dumps({'type': 'landing', 'version': 1})),
         ('proposal.json', json.dumps(data))]
    if data.get('hero_image'):
        e.append((data['hero_image'], hero if hero is not None else img()))
    return zbytes(e + list(extra))


def media_files():
    out = []
    for r, _, fs in os.walk(TMP_MEDIA):
        out += [os.path.join(r, f) for f in fs]
    return out


@override_settings(MEDIA_ROOT=TMP_MEDIA, PROPOSAL_IMPORT_ENABLED=True)
class KPImportAttackTests(TestCase):
    def assertRejected(self, blob):
        before_files = set(media_files())
        n_p, n_i = Proposal.objects.count(), ProposalImport.objects.count()
        with self.assertRaises(ImportError_):
            import_proposal_package(blob)
        self.assertEqual(Proposal.objects.count(), n_p)
        self.assertEqual(ProposalImport.objects.count(), n_i)
        self.assertEqual(set(media_files()), before_files)

    def test_T01_zip_bomb(self):
        self.assertRejected(pkg(extra=[('media/bomb.png', b'\0' * (30 * 1024 * 1024))]))

    def test_T02_traversal(self):
        for name in ('../../config/x.py', '/etc/passwd', 'a/../../b.png', '..\\..\\x.png', 'C:/win.png'):
            with self.subTest(name=name):
                self.assertRejected(pkg(extra=[(name, b'x')]))

    def test_T03_symlink(self):
        zi = zipfile.ZipInfo('media/link.png')
        zi.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.assertRejected(pkg(extra=[(zi, b'/Users/x/.env')]))

    def test_T04_not_zip_magic(self):
        self.assertRejected(b'%PDF-1.4\n' + b'x' * 100)
        # prefix-junk polyglot: zipfile знаходить EOCD у кінці, magic на початку — не PK
        self.assertRejected(b'<html><script>alert(1)</script></html>' + pkg())

    def test_T05_forbidden_ext(self):
        for name in ('x.php', 'x.js', 'media/x.png.html', '.htaccess', 'media/X.HTML', 'media/a.JS', 'style.css'):
            with self.subTest(name=name):
                self.assertRejected(pkg(extra=[(name, b'<script>alert(1)</script>')]))

    def test_T06_oversized(self):
        blob = pkg(extra=[('media/pad.png', os.urandom(20 * 1024 * 1024 + 1))])
        self.assertGreater(len(blob), 20 * 1024 * 1024)
        self.assertRejected(blob)

    def test_T07_51_entries(self):
        extra = [(f'media/i{i}.webp', img()) for i in range(48)]  # 2 json + hero + 48 = 51
        self.assertRejected(pkg(extra=extra))
        ok = parse_package(pkg(extra=extra[:47]))  # рівно 50 — OK
        self.assertTrue(ok.sha256)

    def test_T08_ratio_101(self):
        zi = zipfile.ZipInfo('media/r.png')
        zi.compress_type = zipfile.ZIP_DEFLATED
        blob = pkg(extra=[(zi, b'A' * 2_000_000)])
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            i = z.getinfo('media/r.png')
            self.assertGreater(i.file_size / max(i.compress_size, 1), 100)
        self.assertRejected(blob)

    def test_T09_exif_stripped(self):
        ex = Image.Exif()
        ex[0x010F] = 'SecretCam'  # Make
        ex[0x8825] = {2: (50.0, 27.0, 0.0)}  # GPS
        jpg = img('JPEG', exif=ex.tobytes())
        self.assertTrue(Image.open(io.BytesIO(jpg)).getexif())
        rec = import_proposal_package(pkg(base_data(hero_image='media/hero.jpg'), hero=jpg))
        h = rec.proposal.hero_images.get(is_active=True)
        with Image.open(h.image.path) as im:
            self.assertFalse(dict(im.getexif()), 'EXIF має бути видалено (re-encode)')

    def test_T10_svg(self):
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>'
        self.assertRejected(pkg(extra=[('media/logo.svg', svg)]))
        self.assertRejected(pkg(base_data(hero_image='media/hero.png'), hero=svg))

    def test_T11_polyglot_png_html(self):
        poly = img('PNG') + b'<html><script>alert(1)</script></html>'
        rec = import_proposal_package(pkg(base_data(hero_image='media/hero.png'), hero=poly))
        data = open(rec.proposal.hero_images.get(is_active=True).image.path, 'rb').read()
        self.assertNotIn(b'<script>', data, 'хвіст HTML має зникнути після re-encode')

    def test_T14_xss_html(self):
        payloads = ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>', '<a href="javascript:alert(1)">x</a>',
                    '<svg><script>alert(1)</script></svg>', '<iframe srcdoc="<script>alert(1)</script>"></iframe>',
                    '<meta http-equiv="refresh" content="0;url=//evil">', '<base href="//evil/">',
                    '<style>@import "//evil";</style>', '<p style="background:url(javascript:alert(1))">x</p>',
                    '<noscript><p title="</noscript><img src=x onerror=alert(1)>">', '<a href="JaVaScRiPt:alert(1)">x</a>']
        for p in payloads:
            with self.subTest(p=p):
                out = clean_html(p).lower()
                for bad in ('<script', 'onerror', 'javascript:', '<iframe', '<meta', '<base', '<style', 'style=', '<svg'):
                    self.assertNotIn(bad, out)

    def test_T15_type_spoof(self):
        self.assertRejected(img('PNG'))  # png під .zip

    def test_T16_slug(self):
        for s in ('admin', 'ADMIN', 'media', 'a', 'x--', '<script>', '../x', 'x' * 65, 'static', 'api', 'Sec-Kp'):
            with self.subTest(s=s):
                self.assertRejected(pkg(base_data(slug=s)))

    def test_T21_atomic_failure_keeps_previous(self):
        rec = import_proposal_package(pkg(base_data(title='V1')))
        from unittest import mock
        with mock.patch('apps.core.proposal_import.ProposalImport.save', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                import_proposal_package(pkg(base_data(title='V2', client_name='Інший')))
        rec.proposal.refresh_from_db()
        self.assertEqual(rec.proposal.title, 'V1')


@override_settings(MEDIA_ROOT=TMP_MEDIA, PROPOSAL_IMPORT_ENABLED=True)
class KPImportAccessTests(TestCase):
    def setUp(self):
        U = get_user_model()
        self.staff = U.objects.create_user('st', 'st@x.cz', 'pw', is_staff=True)
        self.editor = U.objects.create_user('ed', 'ed@x.cz', 'pw', is_staff=True)
        self.editor.user_permissions.add(Permission.objects.get(codename='can_import_proposal'))
        self.client_user = U.objects.create_user('cl', 'cl@x.cz', 'pw')
        self.url = reverse('admin:core_proposalimport_upload')

    def _post(self, c):
        f = io.BytesIO(pkg()); f.name = 'kp.zip'
        return c.post(self.url, {'package': f})

    def test_T12_csrf_required(self):
        c = Client(enforce_csrf_checks=True)
        c.force_login(self.editor)
        self.assertEqual(self._post(c).status_code, 403)
        self.assertEqual(Proposal.objects.count(), 0)

    def test_T13_permissions(self):
        anon = Client()
        self.assertEqual(anon.get(self.url).status_code, 302)
        for u, code in ((self.staff, 403), (self.client_user, 302)):
            c = Client(); c.force_login(u)
            with self.subTest(u=u.username):
                self.assertEqual(c.get(self.url).status_code, code)
                self.assertIn(self._post(c).status_code, (302, 403))
        self.assertEqual(Proposal.objects.count(), 0)
        c = Client(); c.force_login(self.editor)
        self.assertEqual(c.get(self.url).status_code, 200)

    def test_T17_delete_traversal(self):
        c = Client(); c.force_login(self.editor)
        for bad in ('../../media', '1%20OR%201', '..%2f..%2fx'):
            r = c.get(f'/admin/core/proposalimport/proposal/{bad}/soft-delete/')
            self.assertIn(r.status_code, (302, 404))
        p = import_proposal_package(pkg()).proposal
        with self.assertRaises(CommandError):
            call_command('purge_proposal', slug=p.slug, confirm=True)  # не soft-deleted
        self.assertTrue(Proposal.objects.filter(pk=p.pk).exists())
        r = c.post(reverse('admin:core_proposalimport_soft_delete', args=[p.pk]), {'slug': 'wrong', 'confirm': 'on'})
        p.refresh_from_db(); self.assertIsNone(p.deleted_at)

    def test_T18_media_serving(self):
        from django.test import RequestFactory
        from django.http import Http404
        from apps.core.proposal_media import protected_media_serve
        os.makedirs(os.path.join(TMP_MEDIA, 'proposals', 'x'), exist_ok=True)
        os.makedirs(os.path.join(TMP_MEDIA, 'proposal_imports'), exist_ok=True)
        with open(os.path.join(TMP_MEDIA, 'proposals', 'x', 'evil.html'), 'w') as f:
            f.write('<script>alert(1)</script>')
        with open(os.path.join(TMP_MEDIA, 'proposal_imports', 'a.zip'), 'wb') as f:
            f.write(b'PK')
        with open(os.path.join(TMP_MEDIA, 'proposals', 'x', 'ok.webp'), 'wb') as f:
            f.write(img())
        rf = RequestFactory()
        for path in ('proposals/x/evil.html', 'PROPOSALS/x/evil.html', 'proposal_imports/a.zip',
                     'x/../proposals/x/evil.html', './proposals/x/evil.html', 'x/../proposal_imports/a.zip',
                     'proposals//x/evil.html', '/proposals/x/evil.html'):
            with self.subTest(path=path):
                with self.assertRaises(Http404):
                    protected_media_serve(rf.get('/media/' + path), path)
        r = protected_media_serve(rf.get('/media/proposals/x/ok.webp'), 'proposals/x/ok.webp')
        self.assertEqual(r['X-Content-Type-Options'], 'nosniff')
        self.assertIn('sandbox', r['Content-Security-Policy'])
        self.assertNotIn('Set-Cookie', r)

    def test_T19_audit_log(self):
        c = Client(); c.force_login(self.editor)
        self._post(c)
        rec = ProposalImport.objects.get()
        self.assertEqual(rec.user, self.editor)
        self.assertEqual(len(rec.sha256), 64)
        self.assertTrue(rec.created_at)
        self.assertNotEqual(c.get(reverse('admin:core_proposalimport_change', args=[rec.pk])).status_code, 500)
        self.assertEqual(c.post(reverse('admin:core_proposalimport_delete', args=[rec.pk]), {'post': 'yes'}).status_code, 403)
        self.assertTrue(ProposalImport.objects.filter(pk=rec.pk).exists())

    def test_T20_soft_delete_hides_keeps_files(self):
        from apps.core.proposal_import import soft_delete_proposal
        p = import_proposal_package(pkg(base_data(is_published=True))).proposal
        path = p.hero_images.get().image.path
        soft_delete_proposal(p, user=self.editor)
        self.assertTrue(os.path.exists(path))
        self.assertEqual(Client().get(f'/proposal/{p.slug}/').status_code, 404)

    def test_T22_noindex_and_sitemap(self):
        p = import_proposal_package(pkg(base_data(is_published=True))).proposal
        r = Client().get(f'/proposal/{p.slug}/', follow=True)
        body = r.content.decode('utf-8', 'ignore') + r.get('X-Robots-Tag', '')
        self.assertIn('noindex', body)
        sm = Client().get('/sitemap.xml').content.decode()
        self.assertNotIn(p.slug, sm)
