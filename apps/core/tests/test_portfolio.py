from django.test import SimpleTestCase, override_settings

from apps.core.models import PortfolioProject
from apps.core.portfolio_images import resolve_portfolio_image_url
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


class PortfolioImageFallbackTests(SimpleTestCase):
    @override_settings(MEDIA_ROOT='/tmp/prometey-empty-media-test')
    def test_static_fallback_when_media_missing(self):
        project = PortfolioProject(
            title='Speak Up',
            slug='speakup',
            card_description='Desc',
        )
        project.card_image.name = 'portfolio/speakup/speakup.png'
        src = resolve_portfolio_image_url(project, 'card_image')
        self.assertIn('portfolio_page/speakup.png', src)

    def test_home_image_prefers_static_over_media(self):
        project = PortfolioProject(
            title='PlayVision',
            slug='playvision',
            card_description='Desc',
        )
        project.home_story_image.name = 'portfolio/playvision/playvision.png'
        src = project.get_home_image_src()
        self.assertIn('/static/images/portfolio/playvision.png', src)
        self.assertNotIn('/media/', src)


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

