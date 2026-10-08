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
from django.utils import translation

from apps.blog.models import BlogPost

SITE_DOMAIN = 'www.prometeylabs.com'

# EN mirrors for key citability / Ads landings (i18n_patterns, prefix_default_language=False).
# Never include admin / proposal / demo / thank-you / blog search.
EN_MIRROR_NAMES = (
    'home',
    'portfolio',
    'internet_shop_v2',
    'corporate_website_v2',
    'telegram_bot',
    'rozrobka_sajtiv',
    'contacts',
    'blog:blog_list',
)


class AbsoluteSitemap(Sitemap):
    """Sitemap без django.contrib.sites — фіксований прод-домен."""

    protocol = 'https'

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
    """Публічні маркетингові та юридичні сторінки (+ EN mirrors)."""

    changefreq = 'weekly'
    priority = 0.7

    # name → (priority, changefreq) — default language (uk, no prefix)
    PAGES = {
        'home': (1.0, 'daily'),
        'portfolio': (0.9, 'weekly'),
        'internet_shop_v2': (0.9, 'weekly'),
        'corporate_website_v2': (0.9, 'weekly'),
        'tz_generator': (0.9, 'weekly'),
        'telegram_bot': (0.9, 'weekly'),
        'rozrobka_sajtiv': (0.9, 'weekly'),
        'rozrobka_lendingu': (0.8, 'weekly'),
        'rozrobka_veb_platform': (0.8, 'weekly'),
        'calculator': (0.8, 'weekly'),
        'contacts': (0.8, 'monthly'),
        'developer': (0.6, 'monthly'),
        'monobank_chastynamy': (0.5, 'monthly'),
        'offer': (0.3, 'yearly'),
        'privacy': (0.3, 'yearly'),
        'cookies': (0.3, 'yearly'),
        'refund': (0.3, 'yearly'),
        'intellectual_property': (0.3, 'yearly'),
        'blog:blog_list': (0.8, 'daily'),
    }

    @staticmethod
    def _safe_reverse(name, lang):
        try:
            with translation.override(lang):
                return reverse(name)
        except NoReverseMatch:
            return None

    def items(self):
        # ('uk'|'en', url_name)
        out = []
        for name in self.PAGES:
            if self._safe_reverse(name, 'uk'):
                out.append(('uk', name))
        for name in EN_MIRROR_NAMES:
            if name in self.PAGES and self._safe_reverse(name, 'en'):
                out.append(('en', name))
        return out

    def location(self, item):
        lang, name = item
        path = self._safe_reverse(name, lang)
        return path or '/'

    def priority(self, item):
        lang, name = item
        pri = self.PAGES[name][0]
        if lang == 'en' and pri > 0.5:
            return round(pri - 0.1, 1)
        return pri

    def changefreq(self, item):
        _lang, name = item
        return self.PAGES[name][1]


class BlogPostSitemap(AbsoluteSitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(is_published=True).only('slug', 'updated_at')

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
}
