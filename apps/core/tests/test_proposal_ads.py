from pathlib import Path

from django.test import SimpleTestCase

from apps.core.middleware import is_private_index_path

ROOT = Path(__file__).resolve().parents[3]
PROPOSAL_BASE = ROOT / 'templates' / 'proposal' / 'base_proposal.html'
ROBOTS = ROOT / 'templates' / 'robots.txt'


class ProposalAdsProtectionTests(SimpleTestCase):
    def test_base_proposal_has_no_gtm(self):
        text = PROPOSAL_BASE.read_text(encoding='utf-8')
        self.assertNotIn('gtm_head.html', text)
        self.assertNotIn('gtm_noscript.html', text)
        self.assertNotIn('GTM-K2FVPPTK', text)
        self.assertNotIn('googletagmanager.com', text)
        self.assertIn('noindex, nofollow', text)
        self.assertNotIn('proposal_tilt.js', text)

    def test_robots_blocks_proposal_and_demo_for_adsbot(self):
        text = ROBOTS.read_text(encoding='utf-8')
        self.assertIn('User-agent: AdsBot-Google', text)
        self.assertIn('User-agent: AdsBot-Google-Mobile', text)
        for path in (
            '/proposal/',
            '/demo/',
            '/demo-landing/',
            '/demo-site/',
            '/*/proposal/',
            '/*/demo/',
        ):
            self.assertGreaterEqual(text.count(f'Disallow: {path}'), 3)
        self.assertNotIn('Disallow: /internet-shop-v2/', text)
        self.assertNotIn('Disallow: /corporate-website-v2/', text)

    def test_private_path_helper(self):
        self.assertTrue(is_private_index_path('/proposal/foo/'))
        self.assertTrue(is_private_index_path('/en/proposal/foo/'))
        self.assertTrue(is_private_index_path('/demo/acme/'))
        self.assertTrue(is_private_index_path('/ru/demo-landing/x/'))
        self.assertFalse(is_private_index_path('/'))
        self.assertFalse(is_private_index_path('/internet-shop-v2/'))
        self.assertFalse(is_private_index_path('/corporate-website-v2/'))
