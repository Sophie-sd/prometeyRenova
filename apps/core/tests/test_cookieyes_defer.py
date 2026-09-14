from pathlib import Path

from django.test import SimpleTestCase

BASE_HTML = Path(__file__).resolve().parents[3] / 'templates' / 'base.html'


class CookieYesDeferTests(SimpleTestCase):
    def test_cmp_is_injected_after_first_paint_not_in_head_src(self):
        text = BASE_HTML.read_text(encoding='utf-8')
        self.assertIn('function _loadCookieYes', text)
        self.assertIn("requestIdleCallback(_loadCookieYes,{timeout:2500})", text)
        self.assertIn('_loadCookieYes();', text)
        self.assertNotIn('rel="preconnect" href="https://cdn-cookieyes.com"', text)
        self.assertNotIn(
            'id="cookieyes" type="text/javascript" async',
            text,
        )
        self.assertLess(text.find("gtag('consent','default'"), text.find('function _loadCookieYes'))
