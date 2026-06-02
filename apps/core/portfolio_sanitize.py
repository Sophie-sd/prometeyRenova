"""Санітизація HTML модальних вікон портфоліо (TinyMCE)."""
import re

import bleach
from bleach.css_sanitizer import CSSSanitizer

ALLOWED_TAGS = [
    'p', 'h2', 'h3', 'strong', 'em', 'u', 'span', 'ul', 'ol', 'li',
    'a', 'br', 'blockquote', 'img',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'span': ['style'],
    'p': ['class', 'style'],
    'h2': ['class'],
    'h3': ['class'],
    'ul': ['class'],
    'li': [],
    'img': ['src', 'alt', 'loading', 'decoding', 'class'],
}

_CSS_SANITIZER = CSSSanitizer(
    allowed_css_properties=[
        'color',
        'background-color',
        'font-family',
        'font-size',
        'text-decoration',
    ],
)

_SAFE_IMG_SRC = re.compile(r'^(?:/media/|/static/)[a-zA-Z0-9_./%-]+$')


def _filter_img_src(tag: str, name: str, value: str) -> bool:
    if name != 'src' or tag != 'img':
        return True
    if not value:
        return False
    lowered = value.strip().lower()
    if lowered.startswith(('javascript:', 'data:', 'vbscript:')):
        return False
    return bool(_SAFE_IMG_SRC.match(value.strip()))


def sanitize_portfolio_html(content: str) -> str:
    """Очищає HTML модалки портфоліо."""
    if not content:
        return ''
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=_CSS_SANITIZER,
        strip=True,
        protocols=['http', 'https', 'mailto'],
    )


def linkify_portfolio_html(content: str) -> str:
    """Додаткова перевірка img src після bleach."""
    cleaned = sanitize_portfolio_html(content)
    if '<img' not in cleaned:
        return cleaned

    def repl(match: re.Match) -> str:
        tag = match.group(0)
        src_match = re.search(r'src=["\']([^"\']+)["\']', tag)
        if not src_match:
            return ''
        src = src_match.group(1)
        if _filter_img_src('img', 'src', src):
            return tag
        return ''

    return re.sub(r'<img\b[^>]*>', repl, cleaned, flags=re.IGNORECASE)
