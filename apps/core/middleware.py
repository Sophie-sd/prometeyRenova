"""
CSP (Content Security Policy) middleware.

Generates a per-request nonce and adds a Content-Security-Policy response header.
The nonce is exposed to templates via the `csp_nonce` context variable (see
context_processors.py).  Every inline <script nonce="{{ csp_nonce }}"> tag must
use this nonce — otherwise the browser will block it.

Allowed external origins are kept conservative; extend the lists below if new
third-party services are added.
"""
import secrets

_PRIVATE_ROOTS = (
    '/proposal',
    '/demo',
    '/demo-landing',
    '/demo-site',
)
_LANG_PREFIXES = ('/en', '/ru', '/cs', '/uk')


def is_private_index_path(path: str) -> bool:
    """КП і демо-вітрини: не індексувати (AdsBot ігнорує meta robots)."""
    stripped = path or ''
    for lang in _LANG_PREFIXES:
        if stripped == lang or stripped.startswith(lang + '/'):
            stripped = stripped[len(lang):] or '/'
            break
    for root in _PRIVATE_ROOTS:
        if stripped == root or stripped.startswith(root + '/'):
            return True
    return False


class NoIndexPrivatePathsMiddleware:
    """X-Robots-Tag на /proposal/ і /demo*, включно з CSS/HTML демо-тем."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if is_private_index_path(request.path_info or ''):
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response


class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        nonce = secrets.token_hex(16)
        request.csp_nonce = nonce

        response = self.get_response(request)

        # Skip non-HTML responses (JSON API, redirects, static files, etc.)
        content_type = response.get('Content-Type', '')
        if 'text/html' not in content_type:
            return response

        # Django admin ships its own JS/CSS bundle and uses inline event
        # handlers in some widgets. Applying 'strict-dynamic' here breaks the
        # nav sidebar, inline "Add another" buttons, autocomplete, etc., so we
        # leave the admin out of the CSP entirely. Admin is an internal,
        # authenticated tool and is not exposed to anonymous traffic.
        path = request.path_info or ''
        if path.startswith('/admin/') or path == '/admin':
            return response

        # Google Fonts load via protocol-relative URLs (//…).
        # On http://localhost that becomes http://, so both schemes must be allowed.
        script_src = (
            f"'self' 'nonce-{nonce}' 'strict-dynamic' 'unsafe-eval' "
            "https://www.googletagmanager.com "
            "https://connect.facebook.net "
            "https://scripts.clixtell.com "
            "https://tracker.clixtell.com "
            "https://www.google.com "
            "https://www.google-analytics.com "
            "https://googleads.g.doubleclick.net "
            "https://www.googleadservices.com"
        )
        csp = "; ".join([
            "default-src 'self'",
            "base-uri 'self'",
            f"script-src {script_src}",
            (
                "style-src 'self' 'unsafe-inline' "
                "https://fonts.googleapis.com http://fonts.googleapis.com"
            ),
            "img-src 'self' data: https: blob:",
            (
                "font-src 'self' data: "
                "https://fonts.gstatic.com http://fonts.gstatic.com"
            ),
            "frame-src 'self' https://www.google.com https://maps.google.com "
            "https://www.googletagmanager.com https://bid.g.doubleclick.net "
            "https://www.facebook.com https://td.doubleclick.net",
            "connect-src 'self' https:",
            "media-src 'self' data: blob:",
            "worker-src 'self' blob:",
        ])
        response['Content-Security-Policy'] = csp
        return response
