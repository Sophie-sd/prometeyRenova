from django.test import SimpleTestCase

from apps.blog.html_sanitize import (
    content_looks_like_html,
    sanitize_blog_html,
    sanitize_blog_title,
)
from apps.blog.models import BlogPost


class BlogHtmlSanitizeTests(SimpleTestCase):
    def test_sanitize_strips_script(self):
        dirty = '<p>Hello</p><script>alert(1)</script>'
        clean = sanitize_blog_html(dirty)
        self.assertIn('<p>Hello</p>', clean)
        self.assertNotIn('script', clean)

    def test_sanitize_keeps_formatting(self):
        html = (
            '<p><strong>Bold</strong> <em>italic</em> '
            '<span style="color: rgb(220, 20, 60);">red</span></p>'
        )
        clean = sanitize_blog_html(html)
        self.assertIn('<strong>Bold</strong>', clean)
        self.assertIn('<em>italic</em>', clean)

    def test_sanitize_title_inline_only(self):
        dirty = '<p>Title</p><strong>Bold</strong><script>x</script>'
        clean = sanitize_blog_title(dirty)
        self.assertIn('<strong>Bold</strong>', clean)
        self.assertNotIn('<p>', clean)
        self.assertNotIn('script', clean)

    def test_content_looks_like_html(self):
        self.assertFalse(content_looks_like_html('Plain text **bold**'))
        self.assertTrue(content_looks_like_html('<p>HTML</p>'))

    def test_get_safe_content_legacy_markdown(self):
        post = BlogPost(
            title='Test',
            slug='test',
            excerpt='Excerpt',
            content='**Bold line**\n\nNormal text',
            seo_title='SEO',
            seo_description='Desc',
            keywords='kw',
        )
        result = post.get_safe_content()
        self.assertIn('<strong>Bold line</strong>', result)
        self.assertNotIn('**', result)

    def test_get_safe_content_html_from_editor(self):
        post = BlogPost(
            title='Test',
            slug='test-html',
            excerpt='Excerpt',
            content='<p><strong>Editor</strong> content</p>',
            seo_title='SEO',
            seo_description='Desc',
            keywords='kw',
        )
        result = post.get_safe_content()
        self.assertIn('<strong>Editor</strong>', result)
        self.assertNotIn('<script', result.lower())
