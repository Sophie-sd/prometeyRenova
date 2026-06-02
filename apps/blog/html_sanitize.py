"""Санітизація HTML-контенту статей блогу (TinyMCE)."""
import bleach
from bleach.css_sanitizer import CSSSanitizer

ALLOWED_TAGS = [
    'p', 'h1', 'h2', 'h3', 'strong', 'em', 'u', 'span', 'ul', 'ol', 'li',
    'a', 'br', 'blockquote',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'span': ['style'],
    'p': ['style'],
    'h1': ['style'],
    'h2': ['style'],
    'h3': ['style'],
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


def sanitize_blog_html(content: str) -> str:
    """Очищає HTML від небезпечних тегів і стилів."""
    if not content:
        return ''
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=_CSS_SANITIZER,
        strip=True,
    )


def content_looks_like_html(content: str) -> bool:
    """Чи схожий контент на HTML з редактора."""
    stripped = (content or '').strip()
    return '<' in stripped and '>' in stripped
