"""Приватні single-file HTML-презентації КП під /proposal/<slug>/.

Той самий механізм приховування, що й у DB-КП (`ProposalDetailView`):
невгадуваний slug під /proposal/, X-Robots-Tag від NoIndexPrivatePathsMiddleware,
meta robots у <head>, відсутність у sitemap.xml / llms.txt і жодних посилань.

Файли лежать поза static/ (не потрапляють у collectstatic і не мають
публічної /static/ адреси). Віддаються з пам'яті, gzip рахується один раз.
Інлайн-скрипти презентації дозволені точковим CSP за sha256-хешами
(глобальний CSPMiddleware пропускає відповіді з власним CSP).
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import re
from functools import lru_cache
from pathlib import Path

from django.http import Http404, HttpResponse
from django.utils.cache import patch_vary_headers
from django.views.decorators.http import require_safe

PRESENTATIONS_DIR = Path(__file__).resolve().parent / 'private_presentations'

# slug (невгадуваний, як у КП) → файл у PRESENTATIONS_DIR
PRESENTATIONS = {
    'ultramarket-prezentatsiia-eea8d641': 'ultramarket.html',
}

_INLINE_SCRIPT = re.compile(rb'<script>(.*?)</script>', re.S)
_HEAD_TAG = re.compile(rb'<(?:meta|link)\b[^>]*>|<title>.*?</title>', re.S)
# Месенджери/соцмережі не дочитують 12-МБ сторінку → віддаємо їм легкий head з OG.
_PREVIEW_BOTS = re.compile(
    r'TelegramBot|facebookexternalhit|Facebot|Twitterbot|WhatsApp|Slackbot|'
    r'LinkedInBot|Discordbot|Viber|SkypeUriPreview|vkShare|Pinterest|redditbot|Applebot',
    re.I,
)


@lru_cache(maxsize=None)
def _preview(filename: str) -> bytes:
    raw = (PRESENTATIONS_DIR / filename).read_bytes()
    head = raw[:raw.find(b'</head>')]
    tags = b'\n'.join(_HEAD_TAG.findall(head))
    return (b'<!doctype html><html lang="uk"><head>' + tags
            + b'</head><body></body></html>')


@lru_cache(maxsize=None)
def _load(filename: str) -> tuple[bytes, bytes, str]:
    raw = (PRESENTATIONS_DIR / filename).read_bytes()
    hashes = ' '.join(
        "'sha256-%s'" % base64.b64encode(hashlib.sha256(body).digest()).decode()
        for body in _INLINE_SCRIPT.findall(raw)
    )
    return raw, gzip.compress(raw, compresslevel=6, mtime=0), hashes


def _csp(script_hashes: str) -> str:
    return '; '.join([
        "default-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        'script-src ' + (script_hashes or "'none'"),
        "style-src 'unsafe-inline'",
        "img-src 'self' data: blob:",
        "font-src data:",
        "media-src data: blob:",
        "connect-src 'none'",
    ])


@require_safe
def private_presentation(request, slug: str):
    filename = PRESENTATIONS.get(slug)
    if not filename:
        raise Http404
    if _PREVIEW_BOTS.search(request.META.get('HTTP_USER_AGENT', '')):
        response = HttpResponse(_preview(filename), content_type='text/html; charset=utf-8')
        patch_vary_headers(response, ('User-Agent',))
        response['X-Robots-Tag'] = 'noindex, nofollow'
        response['Content-Security-Policy'] = "default-src 'none'; img-src 'self'"
        response['Cache-Control'] = 'private, max-age=300'
        return response
    raw, compressed, script_hashes = _load(filename)
    accepts_gzip = 'gzip' in request.META.get('HTTP_ACCEPT_ENCODING', '')
    body = compressed if accepts_gzip else raw
    response = HttpResponse(body, content_type='text/html; charset=utf-8')
    if accepts_gzip:
        response['Content-Encoding'] = 'gzip'
    response['Content-Length'] = str(len(body))
    patch_vary_headers(response, ('Accept-Encoding', 'User-Agent'))
    response['X-Robots-Tag'] = 'noindex, nofollow'
    response['Content-Security-Policy'] = _csp(script_hashes)
    response['Referrer-Policy'] = 'no-referrer'
    response['Cache-Control'] = 'private, max-age=300'
    return response
