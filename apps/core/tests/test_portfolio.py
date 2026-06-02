from django.test import SimpleTestCase

from apps.core.models import PortfolioProject
from apps.core.portfolio_sanitize import linkify_portfolio_html, sanitize_portfolio_html


class PortfolioSanitizeTests(SimpleTestCase):
    def test_strips_script(self):
        dirty = '<p>Hello</p><script>alert(1)</script>'
        clean = sanitize_portfolio_html(dirty)
        self.assertIn('<p>Hello</p>', clean)
        self.assertNotIn('script', clean.lower())

    def test_keeps_safe_img(self):
        html = '<img src="/media/portfolio/test.png" alt="Test" class="portfolio-modal-image-full">'
        clean = linkify_portfolio_html(html)
        self.assertIn('/media/portfolio/test.png', clean)

    def test_blocks_unsafe_img_src(self):
        html = '<img src="javascript:alert(1)" alt="X">'
        clean = linkify_portfolio_html(html)
        self.assertNotIn('javascript:', clean)


class PortfolioModelTests(SimpleTestCase):
    def test_integration_tags_parsing(self):
        project = PortfolioProject(
            title='Test',
            slug='test',
            card_description='Desc',
            integrations='tag one\ntag two\n\n',
        )
        self.assertEqual(project.get_integration_tags(), ['tag one', 'tag two'])

    def test_layout_modifier_even_order_left(self):
        project = PortfolioProject(title='T', slug='t', card_description='D', order=0)
        self.assertEqual(project.get_layout_modifier(), 'project-card--image-left')

    def test_layout_modifier_odd_order_right(self):
        project = PortfolioProject(title='T', slug='t', card_description='D', order=1)
        self.assertEqual(project.get_layout_modifier(), 'project-card--image-right')

    def test_modal_id(self):
        project = PortfolioProject(title='T', slug='speakup', card_description='D')
        self.assertEqual(project.get_modal_id(), 'project-speakup-modal')

