"""AEO P0 infra: sitemap 200 + EN mirrors; llms.txt 200 + price smoke."""
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.sitemaps import EN_MIRROR_NAMES, StaticViewSitemap


EXCLUDED_PATH_FRAGMENTS = (
    '/admin/',
    '/proposal/',
    '/demo/',
    '/demo-landing/',
    '/demo-site/',
    '/thank-you/',
    '/blog/search',
)

REQUIRED_UK_PATHS = (
    '/',
    '/portfolio/',
    '/corporate-website-v2/',
    '/internet-shop-v2/',
    '/telegram-bot/',
    '/rozrobka-sajtiv/',
    '/contacts/',
    '/blog/',
)

REQUIRED_EN_PATHS = (
    '/en/',
    '/en/portfolio/',
    '/en/corporate-website-v2/',
    '/en/internet-shop-v2/',
    '/en/telegram-bot/',
    '/en/rozrobka-sajtiv/',
    '/en/contacts/',
    '/en/blog/',
)


class SitemapAeoP0Tests(TestCase):
    def test_sitemap_200_valid_xml_contains_key_urls(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        ctype = response.get('Content-Type', '')
        self.assertTrue(
            'xml' in ctype or response.content.startswith(b'<?xml'),
            ctype,
        )
        body = response.content.decode()
        self.assertIn('<urlset', body)
        self.assertIn('</urlset>', body)
        for path in REQUIRED_UK_PATHS:
            self.assertIn(path, body)
        for path in REQUIRED_EN_PATHS:
            self.assertIn(path, body)
        for frag in EXCLUDED_PATH_FRAGMENTS:
            self.assertNotIn(frag, body)

    def test_static_pages_all_reverse(self):
        for name in StaticViewSitemap.PAGES:
            with self.subTest(name=name):
                with translation.override('uk'):
                    self.assertTrue(reverse(name))

    def test_en_mirrors_reverse(self):
        for name in EN_MIRROR_NAMES:
            with self.subTest(name=name):
                with translation.override('en'):
                    path = reverse(name)
                    self.assertTrue(path.startswith('/en/'), path)


class LlmsTxtAeoP0Tests(TestCase):
    def test_llms_txt_200_and_content_smoke(self):
        response = self.client.get('/llms.txt')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('PrometeyLabs', body)
        self.assertIn('500–700', body)
        self.assertIn('800–1400', body)
        self.assertIn('corporate-website-v2', body)
        self.assertIn('internet-shop-v2', body)
        self.assertIn('telegram-bot', body)
        self.assertIn('індивідуальний кошторис', body)
        self.assertIn('+380639520565', body)
        self.assertIn('info@prometeylabs.com', body)
        self.assertIn('/contacts/', body)
        for frag in ('/proposal/', '/demo/', '/thank-you/', '/admin/'):
            self.assertNotIn(frag, body)
        # Soft lock mirrored as hub line, not rewritten Soft CSS
        self.assertIn('rozrobka-sajtiv', body)
        self.assertIn('250', body)
