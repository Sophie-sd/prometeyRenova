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

        script_src = (
            f"'self' 'nonce-{nonce}' 'unsafe-eval' "
            "https://www.googletagmanager.com "
            "https://connect.facebook.net "
            "https://scripts.clixtell.com "
            "https://tracker.clixtell.com "
            "https://www.google.com "
            "https://www.google-analytics.com "
            "https://googleads.g.doubleclick.net "
            "https://www.googleadservices.com "
            "https://widgets.binotel.com"
        )
        csp = "; ".join([
            "default-src 'self'",
            f"script-src {script_src}",
            "style-src 'self' 'unsafe-inline' https://widgets.binotel.com https://fonts.googleapis.com",
            "img-src 'self' data: https: blob:",
            "font-src 'self' data: https://fonts.gstatic.com",
            "frame-src 'self' https://www.googletagmanager.com https://bid.g.doubleclick.net",
            "connect-src 'self' https:",
            "media-src 'self' data: blob:",
            "worker-src 'self' blob:",
        ])
        response['Content-Security-Policy'] = csp
        return response
