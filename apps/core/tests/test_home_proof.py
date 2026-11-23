"""Homepage proof: five service modals, studio video, cases and reviews."""
import re

from django.test import TestCase

HOME_URLS = ('/', '/ru/', '/en/')
SERVICE_MODALS = (
    'service-web-modal',
    'service-dorobka-modal',
    'service-mobile-modal',
    'service-smm-modal',
    'service-ai-modal',
)
ROZROBKA_HREF = {
    '/': '/rozrobka-sajtiv/',
    '/ru/': '/ru/rozrobka-sajtiv/',
    '/en/': '/en/rozrobka-sajtiv/',
}
MORE_RE = re.compile(
    r'<button type="button" class="hf-service__more" data-modal="([^"]+)"'
)


def _element_by_id(html, element_id):
    """Return the outer HTML of the first <div> whose id is element_id."""
    id_at = html.index(f'id="{element_id}"')
    start = html.rindex('<div', 0, id_at)
    depth = 0
    index = start
    while index < len(html):
        next_open = html.find('<div', index)
        next_close = html.find('</div>', index)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            index = next_open + 4
            continue
        depth -= 1
        index = next_close + len('</div>')
        if depth == 0:
            return html[start:index]
    raise AssertionError(f'unclosed element {element_id}')


class HomeProofTests(TestCase):
    def _html(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        return response.content.decode()

    def test_services_modals_video_and_proof_order(self):
        for url in HOME_URLS:
            with self.subTest(url=url):
                html = self._html(url)
                self.assertEqual(MORE_RE.findall(html), list(SERVICE_MODALS))
                for modal_id in SERVICE_MODALS:
                    self.assertEqual(html.count(f'id="{modal_id}"'), 1, modal_id)
                    modal = _element_by_id(html, modal_id)
                    self.assertIn('aria-modal="true"', modal)
                dorobka = _element_by_id(html, 'service-dorobka-modal')
                self.assertNotIn('<a ', dorobka)
                web = _element_by_id(html, 'service-web-modal')
                self.assertIn(f'href="{ROZROBKA_HREF[url]}"', web)
                self.assertEqual(html.count('data-rs-video="QVaSdrcDq6M"'), 1)
                self.assertEqual(html.count('data-rs-video-dialog'), 1)
                self.assertEqual(html.count('id="portfolio"'), 1)
                self.assertEqual(html.count('id="rs-reviews"'), 1)
                clients = html.index('id="clients"')
                portfolio = html.index('id="portfolio"')
                reviews = html.index('id="rs-reviews"')
                contact = html.index('id="contact"')
                self.assertLess(clients, portfolio)
                self.assertLess(portfolio, reviews)
                self.assertLess(reviews, contact)
                finale = html.index('class="hf-finale"')
                self.assertGreater(finale, reviews)
                between = html[finale:contact]
                self.assertIn('class="hf-finale__bg"', between)
                self.assertNotIn('id="portfolio"', between)
                self.assertNotIn('id="rs-reviews"', between)
                self.assertEqual(html.count('class="hf-finale__bg"'), 1)
                title_at = html.index('<h2 class="hf-cta__title" id="hf-cta-title">')
                title = html[title_at:html.index('</h2>', title_at)]
                self.assertNotIn('<br', title)
                hero_start = html.index('class="hf-hero"')
                hero = html[hero_start:html.index('</section>', hero_start)]
                self.assertNotIn('pl-calc-cta__micro', hero)

    def test_en_calculate_website_cost_label(self):
        html = self._html('/en/')
        self.assertIn('Calculate website cost', html)

    def test_uk_cta_hint_is_two_lines(self):
        html = self._html('/')
        self.assertIn('Менеджер передзвонить за 15 хвилин', html)
        self.assertIn('Графік роботи: цілодобово', html)
