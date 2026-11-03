"""SEO pass 2026-11-03: canonical, hreflang, robots, sitemap, redirects, JSON-LD, meta."""
import importlib
import json
import re

from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from apps.blog.models import BlogPost
from apps.blog.slugs import LEGACY_SLUG_REDIRECTS
from apps.core import seo
from apps.core.redirects import CanonicalHostMiddleware

SITE = 'https://www.prometeylabs.com'
UNTRANSLATED_EN = ('/en/internet-shop-v2/', '/en/rozrobka-sajtiv/', '/en/dorobka-sajtu/')
INDEXABLE = (
    '/', '/ru/', '/en/', '/portfolio/', '/ru/portfolio/', '/en/portfolio/', '/contacts/', '/en/contacts/',
    '/calculator/', '/blog/', '/ru/blog/', '/en/blog/', '/telegram-bot/', '/en/telegram-bot/',
    '/corporate-website-v2/', '/en/corporate-website-v2/', '/internet-shop-v2/', '/ru/internet-shop-v2/',
    '/rozrobka-sajtiv/', '/ru/rozrobka-sajtiv/', '/dorobka-sajtu/', '/ru/dorabotka-sajta/',
    '/privacy/', '/ru/privacy/', '/en/privacy/', '/offer/', '/refund/', '/cookies/',
)


def _post(slug='test-post', **kw):
    data = dict(title='Тест', slug=slug, excerpt='e', content='<p>c</p>', seo_title='s',
                seo_description='d', keywords='k', is_published=True)
    data.update(kw)
    return BlogPost.objects.create(**data)


def head(html):
    return {
        'canonical': re.findall(r'<link rel="canonical" href="([^"]+)"', html),
        'alternates': dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html)),
        'robots': re.findall(r'<meta name="robots" content="([^"]+)"', html),
        'title': re.search(r'<title>(.*?)</title>', html, re.S).group(1).strip(),
        'description': re.search(r'<meta name="description"\s+content="(.*?)"', html, re.S).group(1).strip(),
        'ld': [json.loads(b) for b in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)],
    }


class CanonicalHreflangTests(TestCase):
    def get(self, path):
        r = self.client.get(path)
        self.assertEqual(r.status_code, 200, path)
        return head(r.content.decode())

    def test_self_canonical_absolute_single(self):
        for path in INDEXABLE + UNTRANSLATED_EN:
            with self.subTest(path=path):
                h = self.get(path)
                self.assertEqual(h['canonical'], [SITE + path])

    def test_query_params_dropped_except_blog_page(self):
        self.assertEqual(self.get('/portfolio/?utm_source=x')['canonical'], [SITE + '/portfolio/'])
        self.assertEqual(self.get('/blog/?page=1')['canonical'], [SITE + '/blog/'])

    def test_untranslated_en_noindex_no_hreflang(self):
        for path in UNTRANSLATED_EN:
            with self.subTest(path=path):
                h = self.get(path)
                self.assertEqual(h['robots'], ['noindex, follow'])
                self.assertEqual(h['alternates'], {})

    def test_hreflang_reciprocal_with_x_default(self):
        for path in INDEXABLE:
            with self.subTest(path=path):
                alts = self.get(path)['alternates']
                self.assertIn(SITE + path, alts.values())
                self.assertEqual(alts['x-default'], alts['uk'])
                for code, href in alts.items():
                    self.assertTrue(href.startswith(SITE + '/'))
                    self.assertNotIn(href[len(SITE):], UNTRANSLATED_EN)
                    if code != 'x-default':
                        self.assertEqual(self.get(href[len(SITE):])['alternates'], alts, href)

    def test_single_seo_head_block(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        self.assertEqual(html.count('rel="canonical"'), 1)
        self.assertEqual(html.count('name="robots"'), 1)

    def test_titles_and_descriptions_lengths(self):
        for (name, lang), (title, desc) in seo.META_OVERRIDES.items():
            with self.subTest(name=name, lang=lang):
                if title:
                    self.assertTrue(50 <= len(title) <= 60, (title, len(title)))
                    self.assertNotIn('курси програмування', title.lower())
                if desc:
                    self.assertTrue(150 <= len(desc) <= 160, (desc, len(desc)))

    def test_home_h1(self):
        for path, text in (('/', 'Розробка сайтів під ключ — PrometeyLabs'),
                           ('/ru/', 'Разработка сайтов под ключ — PrometeyLabs')):
            html = self.client.get(path).content.decode()
            h1 = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.S)
            self.assertEqual(len(h1), 1)
            self.assertEqual(re.sub(r'<[^>]+>', '', h1[0]).strip(), text)


class SitemapTests(TestCase):
    def setUp(self):
        _post('latin-post')

    def test_sitemap(self):
        r = self.client.get('/sitemap.xml')
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        locs = re.findall(r'<loc>([^<]+)</loc>', body)
        blocks = re.findall(r'<url>(.*?)</url>', body, re.S)
        self.assertEqual(len(locs), len(blocks))
        self.assertTrue(all('<lastmod>' in b for b in blocks))
        self.assertNotIn('<changefreq>', body)
        self.assertNotIn('<priority>', body)
        self.assertNotIn(SITE + '/developer/', locs)
        for p in UNTRANSLATED_EN:
            self.assertNotIn(SITE + p, locs)
        for p in ('/ru/', '/ru/portfolio/', '/en/portfolio/', '/blog/latin-post/'):
            self.assertIn(SITE + p, locs)
        # post without RU translation: only uk
        self.assertNotIn(SITE + '/ru/blog/latin-post/', locs)
        self.assertEqual(len(locs), len(set(locs)))


class BlogTests(TestCase):
    def test_blog_posting_json_ld_and_dates(self):
        post = _post('latin-post')
        html = self.client.get('/blog/latin-post/').content.decode()
        nodes = [n for n in head(html)['ld'] if n.get('@type') == 'BlogPosting']
        self.assertEqual(len(nodes), 1)
        bp = nodes[0]
        for k in ('headline', 'author', 'datePublished', 'dateModified', 'image'):
            self.assertTrue(bp.get(k), k)
        img = bp['image'][0] if isinstance(bp['image'], list) else bp['image']
        self.assertTrue(img.startswith('https://'))
        self.assertIn(f'datetime="{timezone.localtime(post.created_at).isoformat()}"'[:30], html)
        self.assertEqual(bp['datePublished'][:10], timezone.localtime(post.created_at).date().isoformat())

    def test_untranslated_post_copies_noindex(self):
        _post('latin-post')
        h = head(self.client.get('/ru/blog/latin-post/').content.decode())
        self.assertEqual(h['robots'], ['noindex, follow'])
        self.assertEqual(h['canonical'], [SITE + '/ru/blog/latin-post/'])

    def test_legacy_cyrillic_slugs_301(self):
        for old, new in LEGACY_SLUG_REDIRECTS.items():
            _post(new)
            for pre in ('', '/ru', '/en'):
                with self.subTest(old=old, pre=pre):
                    r = self.client.get(f'{pre}/blog/{old}/')
                    self.assertEqual(r.status_code, 301)
                    self.assertTrue(r['Location'].endswith(f'{pre}/blog/{new}/'))

    def test_migration_renames_and_is_idempotent(self):
        mig = importlib.import_module('apps.blog.migrations.0004_latin_blog_slugs')
        from django.apps import apps
        for old in mig.RENAMES:
            _post(old)
        mig.forwards(apps, None)
        mig.forwards(apps, None)
        for old, new in mig.RENAMES.items():
            self.assertFalse(BlogPost.objects.filter(slug=old).exists())
            self.assertTrue(BlogPost.objects.filter(slug=new).exists())


class CsRedirectTests(TestCase):
    def test_known_paths_301_to_cz(self):
        for src, dst in (('/cs/', 'https://prometeylabs.cz/'), ('/cs/kontakty/', 'https://prometeylabs.cz/contacts/'),
                         ('/cs/rozrobka-sajtiv/', 'https://prometeylabs.cz/tvorba-webu/')):
            with self.subTest(src=src):
                r = self.client.get(src)
                self.assertEqual(r.status_code, 301)
                self.assertEqual(r['Location'], dst)

    def test_unknown_410(self):
        self.assertEqual(self.client.get('/cs/neexistuje/').status_code, 410)


class OrganizationTests(TestCase):
    def test_single_organization_node_referenced(self):
        ld = head(self.client.get('/rozrobka-sajtiv/').content.decode())['ld']
        flat = []
        for n in ld:
            flat += n.get('@graph', [n]) if isinstance(n, dict) else n
        def is_org(n):
            t = n.get('@type')
            return 'Organization' in (t if isinstance(t, list) else [t])
        orgs = [n for n in flat if is_org(n) and n.get('name')]
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0]['@id'], SITE + '/#organization')
        for n in flat:
            if n.get('@type') == 'BreadcrumbList':
                for el in n['itemListElement']:
                    self.assertTrue(el.get('name') and el.get('item'))


class CanonicalHostMiddlewareTests(TestCase):
    def run_mw(self, host, secure, path='/portfolio/?a=1'):
        req = RequestFactory().get(path, HTTP_HOST=host, secure=secure)
        return CanonicalHostMiddleware(lambda r: 'passed')(req)

    @override_settings(CANONICAL_HOST_REDIRECT=True, ALLOWED_HOSTS=['*'])
    def test_redirects_once_to_https_www(self):
        for host, secure in (('prometeylabs.com', False), ('prometeylabs.com', True), ('www.prometeylabs.com', False)):
            with self.subTest(host=host, secure=secure):
                r = self.run_mw(host, secure)
                self.assertEqual(r.status_code, 301)
                self.assertEqual(r['Location'], SITE + '/portfolio/?a=1')

    @override_settings(CANONICAL_HOST_REDIRECT=True, ALLOWED_HOSTS=['*'])
    def test_no_loop_and_other_hosts_untouched(self):
        self.assertEqual(self.run_mw('www.prometeylabs.com', True), 'passed')
        self.assertEqual(self.run_mw('prometei-web.onrender.com', False), 'passed')
        self.assertEqual(self.run_mw('127.0.0.1', False), 'passed')

    @override_settings(CANONICAL_HOST_REDIRECT=False, ALLOWED_HOSTS=['*'])
    def test_disabled_flag(self):
        self.assertEqual(self.run_mw('prometeylabs.com', False), 'passed')
