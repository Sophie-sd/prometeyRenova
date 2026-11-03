"""Sitemap для Google Search Console / краулерів.

Root cause note (AEO P0): django.contrib.sites is NOT in INSTALLED_APPS.
Django's default Sitemap.get_urls() calls Site.objects.get_current() when
site=None → ImproperlyConfigured / 500. AbsoluteSitemap always injects a
fixed prod domain so /sitemap.xml stays 200 without the sites framework.

Secondary 500 risk: NoReverseMatch if PAGES lists a dead URL name.
items() skips names that fail reverse; tests assert every PAGES name reverses.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import NoReverseMatch, reverse
from django.utils import timezone, translation

from apps.blog.models import BlogPost

from . import seo

SITE_DOMAIN = 'www.prometeylabs.com'

# Kept for backwards compatibility (tests / imports): EN versions listed in the sitemap.
EN_MIRROR_NAMES = tuple(name for name, langs in seo.PAGE_LANGUAGES.items() if 'en' in langs)


class AbsoluteSitemap(Sitemap):
    """Sitemap без django.contrib.sites — фіксований прод-домен.

    No <changefreq>/<priority> (ignored by Google); every URL has <lastmod>.
    """

    protocol = 'https'
    changefreq = None
    priority = None

    def get_urls(self, page=1, site=None, protocol=None):
        class _Site:
            domain = SITE_DOMAIN
            name = 'PrometeyLabs'

        return super().get_urls(
            page=page,
            site=_Site(),
            protocol=protocol or self.protocol,
        )


class StaticViewSitemap(AbsoluteSitemap):
    """Indexable static pages × real language versions (apps.core.seo.PAGE_LANGUAGES)."""

    # Backwards-compatible view of the registry (tests assert every name reverses).
    PAGES = dict.fromkeys(seo.PAGE_LANGUAGES)

    @staticmethod
    def _safe_reverse(name, lang):
        return seo.localized_path(name, lang)

    def items(self):
        return seo.sitemap_entries()

    def location(self, item):
        lang, name = item
        return self._safe_reverse(name, lang) or '/'

    def lastmod(self, item):
        _lang, name = item
        if name == seo.BLOG_LIST:
            latest = (
                BlogPost.objects.filter(is_published=True)
                .order_by('-updated_at')
                .values_list('updated_at', flat=True)
                .first()
            )
            if latest:
                # Always a date: mixing date/datetime breaks Django's latest_lastmod.
                return timezone.localtime(latest).date()
        return seo.STATIC_LASTMOD


class BlogPostSitemap(AbsoluteSitemap):
    """Published posts in every language that has a real translation (uk, ru when filled)."""

    def items(self):
        out = []
        posts = BlogPost.objects.filter(is_published=True).only(
            'slug', 'updated_at', 'title_ru', 'content_ru',
        )
        for post in posts:
            for lang in seo.blog_post_languages(post):
                out.append((lang, post))
        return out

    def location(self, item):
        lang, post = item
        return seo.localized_path(seo.BLOG_DETAIL, lang, {'slug': post.slug})

    def lastmod(self, item):
        return timezone.localtime(item[1].updated_at).date()


sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
}
