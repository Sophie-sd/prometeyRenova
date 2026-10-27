"""UltraMarket single-file presentation: hidden like KP pages (noindex, no sitemap/llms)."""
import gzip

from django.test import Client, TestCase
from django.urls import reverse

SLUG = 'ultramarket-prezentatsiia-eea8d641'
URL = f'/proposal/{SLUG}/'


class PrivatePresentationTests(TestCase):
    def test_url_is_under_proposal_prefix(self):
        self.assertEqual(reverse('private_presentation_ultramarket'), URL)

    def test_serves_html_with_noindex_header_and_meta(self):
        response = Client().get(URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')
        self.assertTrue(response['Content-Type'].startswith('text/html'))
        head = response.content[:4000].decode('utf-8', 'ignore')
        self.assertIn('<meta name="robots" content="noindex, nofollow, noarchive">', head)
        self.assertIn('UltraMarket', head)
        self.assertNotIn(b'googletagmanager.com', response.content)

    def test_own_csp_allows_inline_scripts_by_hash(self):
        response = Client().get(URL)
        csp = response['Content-Security-Policy']
        self.assertIn("script-src 'sha256-", csp)
        self.assertNotIn('strict-dynamic', csp)
        self.assertNotIn("'unsafe-inline' 'nonce", csp)

    def test_gzip_when_accepted(self):
        response = Client().get(URL, HTTP_ACCEPT_ENCODING='gzip, br')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Encoding'], 'gzip')
        self.assertIn('Accept-Encoding', response['Vary'])
        self.assertIn(b'UltraMarket', gzip.decompress(response.content)[:4000])
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')

    def test_post_not_allowed_and_unknown_slug_still_404(self):
        self.assertEqual(Client().post(URL).status_code, 405)
        self.assertEqual(
            Client().get('/proposal/ultramarket-prezentatsiia-00000000/').status_code,
            404,
        )

    def test_not_in_sitemap_llms_or_robots(self):
        client = Client()
        for path in ('/sitemap.xml', '/llms.txt', '/robots.txt'):
            response = client.get(path)
            self.assertEqual(response.status_code, 200, path)
            body = response.content.decode()
            self.assertNotIn(SLUG, body, path)
            self.assertNotIn('ultramarket', body.lower(), path)

    def test_home_not_linking_and_keeps_site_csp(self):
        response = Client().get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SLUG, response.content.decode())
        self.assertIn("'strict-dynamic'", response['Content-Security-Policy'])
