"""SEO redirects: canonical host/scheme (one hop) and legacy /cs/* → prometeylabs.cz."""
from django.conf import settings
from django.http import HttpResponseGone, HttpResponsePermanentRedirect

CANONICAL_HOST = 'www.prometeylabs.com'
CANONICAL_ORIGIN = 'https://' + CANONICAL_HOST
# Only the public domains are normalised. Render's own hostname, localhost and the
# internal health check (no Host of ours) pass through untouched → no loops, no failed checks.
PUBLIC_HOSTS = frozenset({'prometeylabs.com', 'www.prometeylabs.com'})


class CanonicalHostMiddleware:
    """http://(www.)prometeylabs.com/* and https://prometeylabs.com/* → 301 https://www.prometeylabs.com/*.

    Scheme comes from request.is_secure(), i.e. SECURE_PROXY_SSL_HEADER
    (X-Forwarded-Proto set by Render's proxy). Enabled via CANONICAL_HOST_REDIRECT.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'CANONICAL_HOST_REDIRECT', False)

    def __call__(self, request):
        if self.enabled:
            host = (request.META.get('HTTP_HOST') or '').split(':')[0].lower().rstrip('.')
            if host in PUBLIC_HOSTS and (host != CANONICAL_HOST or not request.is_secure()):
                return HttpResponsePermanentRedirect(CANONICAL_ORIGIN + request.get_full_path())
        return self.get_response(request)


CZ_ORIGIN = 'https://prometeylabs.cz'

# /cs/<path> on .com → verified 200 page on prometeylabs.cz (checked 2026-11-03).
CS_REDIRECTS = {
    '': '/',
    'kontakty/': '/contacts/',
    'contacts/': '/contacts/',
    'portfolio/': '/portfolio/',
    'blog/': '/blog/',
    'tvorba-webu/': '/tvorba-webu/',
    'rozrobka-sajtiv/': '/tvorba-webu/',
    'uprava-webu/': '/uprava-webu/',
    'dorobka-sajtu/': '/uprava-webu/',
    'internet-shop/': '/internet-shop/',
    'internet-shop-v2/': '/internet-shop/',
    'corporate-website/': '/corporate-website/',
    'corporate-website-v2/': '/corporate-website/',
    'telegram-bot/': '/telegram-bot/',
    'tz-dlia-saitu/': '/tz-dlia-saitu/',
    'calculator/': '/calculator/',
    'offer/': '/offer/',
    'privacy/': '/privacy/',
    'cookies/': '/cookies/',
    'refund/': '/refund/',
    'intellectual-property/': '/intellectual-property/',
}

# Blog posts that exist on prometeylabs.cz under the same slug.
CS_BLOG_SLUGS = frozenset({
    'majbutne-veb-rozrobky-prohnoz-cherez-2-3-roky',
    'pwa-sajt-chy-dodatok-chomu-krashche-mobilnoho',
    'avtomatyzatsiya-marketyngu-yak-ai-zaminyv-3-marketolohiv',
    'ai-v-internet-magazyni-yak-pidnyaly-serednij-chek',
    'bezpeka-saytu-istoriya-zlomu-400000-zbytkiv',
    'mvp-za-4-tyzhni-istoriya-startapu-shcho-zaluchyv-investytsiyi',
    'ai-spivrobitnyk-koly-shtuchnyj-intelekt-najnyaly-na-robotu',
    'seo-z-ai-yak-vyjty-v-top-google-za-2-misyatsi',
    'ai-chat-boty-koly-kliyent-ne-rozumiye-shcho-spilkuyetsya',
    'skilky-koshtuye-zrobyty-sajt-v-ukrayini-realni-tsiny',
    'api-intehratsii-yak-obyednaty-systemy-biznesu',
    'ai-u-veb-rozrobtsi-yak-shtuchnyj-intelekt-zminyuye-stvorennya-sajtiv',
})


def cs_target(rest: str) -> str | None:
    rest = (rest or '').lstrip('/')
    if rest and not rest.endswith('/'):
        rest += '/'
    if rest in CS_REDIRECTS:
        return CZ_ORIGIN + CS_REDIRECTS[rest]
    if rest.startswith('blog/'):
        slug = rest[len('blog/'):].strip('/')
        if slug in CS_BLOG_SLUGS:
            return f'{CZ_ORIGIN}/blog/{slug}/'
    return None


def cs_legacy_redirect(request, rest=''):
    """Czech section moved to prometeylabs.cz: 301 to the matching page, else 410 Gone."""
    target = cs_target(rest)
    if target:
        return HttpResponsePermanentRedirect(target)
    return HttpResponseGone('Gone', content_type='text/plain; charset=utf-8')
