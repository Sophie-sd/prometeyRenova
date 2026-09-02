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


_BLOCK_RE = re.compile(
    r'<(?:p|ul|ol|h2|h3|blockquote)\b[^>]*>.*?</(?:p|ul|ol|h2|h3|blockquote)>',
    flags=re.DOTALL | re.IGNORECASE,
)


def split_modal_content_for_detail(content: str) -> tuple[str, str, str]:
    """Розбиває HTML модалки на 3 частини для сторінки деталей проєкту."""
    cleaned = linkify_portfolio_html(content)
    if not cleaned.strip():
        return '', '', ''

    chunks = _BLOCK_RE.findall(cleaned)
    if not chunks:
        return cleaned, '', ''

    if len(chunks) == 1:
        return chunks[0], '', ''

    integrations_start = None
    integrations_end = None

    for index, chunk in enumerate(chunks):
        if re.search(r'portfolio-modal-integrations', chunk, re.IGNORECASE):
            integrations_start = index
            break

    if integrations_start is None:
        for index, chunk in enumerate(chunks):
            if re.search(r'<ul\b', chunk, re.IGNORECASE):
                integrations_start = index
                if index > 0 and re.search(r'<p\b', chunks[index - 1], re.IGNORECASE):
                    integrations_start = index - 1
                break

    if integrations_start is not None:
        integrations_end = integrations_start + 1
        for index in range(integrations_start, len(chunks)):
            if re.search(r'<ul\b', chunks[index], re.IGNORECASE):
                integrations_end = index + 1
                break

        part1 = ''.join(chunks[:integrations_start])
        part2 = ''.join(chunks[integrations_start:integrations_end])
        rest = chunks[integrations_end:]

        if not rest:
            return part1, part2, ''
        return part1, part2, ''.join(rest)

    split1 = 1
    for index, chunk in enumerate(chunks):
        if re.search(r'<ul\b', chunk, re.IGNORECASE):
            split1 = index + 1
            break

    part1 = ''.join(chunks[:split1])
    rest = chunks[split1:]

    if not rest:
        return part1, '', ''
    if len(rest) == 1:
        return part1, rest[0], ''

    mid = (len(rest) + 1) // 2
    part2 = ''.join(rest[:mid])
    part3 = ''.join(rest[mid:])
    return part1, part2, part3
