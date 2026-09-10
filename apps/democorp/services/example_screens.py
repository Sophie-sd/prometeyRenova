"""Прямокутні EN-скріни прикладів сайтів на тлі #100D0C."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = (16, 13, 12)
BAR = (24, 20, 18)
GOLD = (201, 154, 68)
CHAMPAGNE = (232, 213, 176)
CREAM = (247, 246, 244)
MUTED = (168, 156, 142)
SLOT = (42, 36, 32)

W, H = 1440, 900
SEED_DIR = Path(__file__).resolve().parents[3] / 'static' / 'democorp' / 'seed' / 'examples'

SCREENS = (
    {
        'file': 'company.webp',
        'nav': ('Home', 'About', 'Services', 'Contact'),
        'title': 'A company site\nthat gets requests',
        'lead': 'Home, about, contacts. Clear words. Easy on the phone.',
        'cta': 'Request a site',
        'kind': 'hero',
    },
    {
        'file': 'multilingual.webp',
        'nav': ('Home', 'Work', 'About', 'Contact'),
        'title': 'One site.\nFour languages.',
        'lead': 'UA · EN · CS · RU — switch in the header, same structure.',
        'cta': 'See languages',
        'kind': 'langs',
    },
    {
        'file': 'catalog.webp',
        'nav': ('Home', 'Services', 'About', 'Contact'),
        'title': 'Services, listed.\nEach with a page.',
        'lead': 'Cards, a detail page, a request button on every item.',
        'cta': 'View services',
        'kind': 'cards',
    },
    {
        'file': 'agency.webp',
        'nav': ('Work', 'Process', 'About', 'Contact'),
        'title': 'Cases that explain\nwho you are',
        'lead': 'Reviews, process, a form — partners understand the studio.',
        'cta': 'See our work',
        'kind': 'hero',
    },
    {
        'file': 'production.webp',
        'nav': ('Home', 'Process', 'Gallery', 'Contact'),
        'title': 'How we make it,\nnot just a slogan',
        'lead': 'Four steps, shop-floor photos, certificates in one place.',
        'cta': 'See the process',
        'kind': 'hero',
    },
    {
        'file': 'construction.webp',
        'nav': ('Projects', 'Services', 'About', 'Contact'),
        'title': 'Projects you can\nread on a phone',
        'lead': 'Services, objects, a consultation request — no pinch-zoom.',
        'cta': 'Get a quote',
        'kind': 'cards',
    },
    {
        'file': 'clinic.webp',
        'nav': ('Services', 'Doctors', 'Booking', 'Contact'),
        'title': 'Book from the site,\nnot from Direct',
        'lead': 'Services, a booking form, phone in the header.',
        'cta': 'Book a visit',
        'kind': 'hero',
    },
    {
        'file': 'school.webp',
        'nav': ('Programmes', 'Schedule', 'About', 'Contact'),
        'title': 'Parents get it\nfrom the first screen',
        'lead': 'Programmes, class booking, branches — short and clear.',
        'cta': 'View programmes',
        'kind': 'langs',
    },
)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        'Arial Bold.ttf' if bold else 'Arial.ttf',
        'Helvetica.ttc',
        'Arial Unicode.ttf',
    )
    roots = (
        Path('/System/Library/Fonts/Supplemental'),
        Path('/System/Library/Fonts'),
        Path('/Library/Fonts'),
    )
    for root in roots:
        for name in candidates:
            path = root / name
            if path.is_file():
                try:
                    return ImageFont.truetype(str(path), size=size)
                except OSError:
                    continue
    return ImageFont.load_default()


def _text(draw: ImageDraw.ImageDraw, xy, text, font, fill):
    draw.text(xy, text, font=font, fill=fill, spacing=8)


def _paint_header(draw: ImageDraw.ImageDraw, nav: tuple[str, ...]) -> None:
    draw.rectangle((0, 0, W, 88), fill=BAR)
    draw.line((0, 88, W, 88), fill=GOLD, width=1)
    logo = _font(18, bold=True)
    _text(draw, (56, 34), 'PROMETEYLABS', logo, CHAMPAGNE)
    item_font = _font(14)
    x = W - 56
    for label in reversed(nav):
        bbox = draw.textbbox((0, 0), label, font=item_font)
        tw = bbox[2] - bbox[0]
        x -= tw
        _text(draw, (x, 36), label, item_font, MUTED)
        x -= 36


def _paint_hero(draw: ImageDraw.ImageDraw, spec: dict) -> None:
    title_font = _font(54, bold=True)
    lead_font = _font(20)
    cta_font = _font(14, bold=True)
    _text(draw, (56, 180), spec['title'], title_font, CREAM)
    _text(draw, (56, 360), spec['lead'], lead_font, MUTED)
    cta = spec['cta'].upper()
    bbox = draw.textbbox((0, 0), cta, font=cta_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 22, 16
    x0, y0 = 56, 430
    draw.rectangle((x0, y0, x0 + tw + pad_x * 2, y0 + th + pad_y * 2), fill=CHAMPAGNE)
    _text(draw, (x0 + pad_x, y0 + pad_y - 2), cta, cta_font, BG)
    draw.rectangle((720, 150, 1384, 820), fill=SLOT)
    draw.rectangle((720, 150, 1384, 820), outline=GOLD, width=1)


def _paint_langs(draw: ImageDraw.ImageDraw, spec: dict) -> None:
    _paint_hero(draw, spec)
    pill = _font(13, bold=True)
    x = 56
    y = 540
    for code in ('UA', 'EN', 'CS', 'RU'):
        bbox = draw.textbbox((0, 0), code, font=pill)
        tw = bbox[2] - bbox[0]
        draw.rectangle((x, y, x + tw + 28, y + 36), outline=GOLD, width=1)
        _text(draw, (x + 14, y + 10), code, pill, CHAMPAGNE)
        x += tw + 40


def _paint_cards(draw: ImageDraw.ImageDraw, spec: dict) -> None:
    title_font = _font(40, bold=True)
    lead_font = _font(18)
    card_title = _font(16, bold=True)
    _text(draw, (56, 140), spec['title'], title_font, CREAM)
    _text(draw, (56, 280), spec['lead'], lead_font, MUTED)
    labels = ('Strategy', 'Build', 'Handover')
    gap, left, top, height = 24, 56, 360, 420
    width = (W - 56 * 2 - gap * 2) // 3
    for i, label in enumerate(labels):
        x = left + i * (width + gap)
        draw.rectangle((x, top, x + width, top + height), fill=SLOT)
        draw.rectangle((x, top, x + width, top + height), outline=GOLD, width=1)
        _text(draw, (x + 24, top + 28), label.upper(), card_title, CHAMPAGNE)
        draw.rectangle((x + 24, top + 80, x + width - 24, top + height - 24), fill=BAR)


def render_screen(spec: dict) -> Image.Image:
    image = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(image)
    _paint_header(draw, spec['nav'])
    kind = spec['kind']
    if kind == 'langs':
        _paint_langs(draw, spec)
    elif kind == 'cards':
        _paint_cards(draw, spec)
    else:
        _paint_hero(draw, spec)
    return image


def write_screens(out_dir: Path | None = None) -> list[Path]:
    target = out_dir or SEED_DIR
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for spec in SCREENS:
        path = target / spec['file']
        render_screen(spec).save(path, format='WEBP', quality=86, method=6)
        written.append(path)
    return written
