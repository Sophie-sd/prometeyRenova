"""Скріни галереї «Як працюємо»: адмінка та телефон на тлі #100D0C."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from .example_screens import BAR, BG, CHAMPAGNE, CREAM, GOLD, MUTED, SLOT, _font, _text

W, H = 1200, 900
SEED_DIR = Path(__file__).resolve().parents[3] / 'static' / 'democorp' / 'seed' / 'gallery'


def _paint_admin(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 280, H), fill=BAR)
    draw.line((280, 0, 280, H), fill=GOLD, width=1)
    logo = _font(16, bold=True)
    _text(draw, (28, 36), 'PROMETEYLABS', logo, CHAMPAGNE)
    _text(draw, (28, 64), 'Адмінка', _font(13), MUTED)
    nav = _font(15)
    items = (
        (120, 'Тексти', True),
        (168, 'Фото', False),
        (216, 'Заявки', False),
    )
    for y, label, active in items:
        if active:
            draw.rectangle((16, y - 10, 264, y + 28), outline=GOLD, width=1)
            _text(draw, (32, y), label, nav, CREAM)
        else:
            _text(draw, (32, y), label, nav, MUTED)

    _text(draw, (332, 40), 'Головна сторінка', _font(28, bold=True), CREAM)
    _text(draw, (332, 84), 'Тексти правите самі — без програміста.', _font(16), MUTED)

    label_f = _font(13, bold=True)
    field_f = _font(16)
    y = 150
    for title, value, tall in (
        ('Заголовок', 'Кілька сторінок — і люди пишуть вам', False),
        ('Підзаголовок', 'Головна, послуги, про нас, контакти.\nЗрозумілі слова, зручно з телефону.', True),
    ):
        _text(draw, (332, y), title.upper(), label_f, GOLD)
        box_h = 132 if tall else 56
        draw.rectangle((332, y + 28, 1144, y + 28 + box_h), fill=SLOT)
        draw.rectangle((332, y + 28, 1144, y + 28 + box_h), outline=GOLD, width=1)
        _text(draw, (348, y + 42), value, field_f, CREAM)
        y += box_h + 56

    cta = 'ЗБЕРЕГТИ ЗМІНИ'
    cta_f = _font(14, bold=True)
    bbox = draw.textbbox((0, 0), cta, font=cta_f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x0, y0 = 332, y
    draw.rectangle((x0, y0, x0 + tw + 44, y0 + th + 28), fill=CHAMPAGNE)
    _text(draw, (x0 + 22, y0 + 12), cta, cta_f, BG)


def _paint_phone(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    x0, y0, x1, y1 = 420, 48, 780, 852
    draw.rounded_rectangle((x0, y0, x1, y1), radius=42, fill=(28, 24, 22))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=42, outline=GOLD, width=2)
    sx0, sy0, sx1, sy1 = x0 + 18, y0 + 18, x1 - 18, y1 - 18
    draw.rounded_rectangle((sx0, sy0, sx1, sy1), radius=28, fill=BG)
    draw.rounded_rectangle((470, 62, 730, 86), radius=12, fill=BAR)
    _text(draw, (500, 108), 'PROMETEYLABS', _font(13, bold=True), CHAMPAGNE)
    _text(
        draw,
        (456, 160),
        'Кілька сторінок —\nі люди пишуть вам',
        _font(22, bold=True),
        CREAM,
    )
    _text(draw, (456, 250), 'Зручно з телефону.\nБез щипка й зуму.', _font(14), MUTED)
    cta = 'ЗАЯВКА'
    cta_f = _font(13, bold=True)
    bbox = draw.textbbox((0, 0), cta, font=cta_f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = 456, 340
    draw.rectangle((bx, by, bx + tw + 36, by + th + 24), fill=CHAMPAGNE)
    _text(draw, (bx + 18, by + 10), cta, cta_f, BG)
    stats = (('0.8s', 'завантаження'), ('44px', 'кнопки'), ('100%', 'з телефону'))
    y = 430
    for num, label in stats:
        draw.line((456, y, 744, y), fill=SLOT, width=1)
        _text(draw, (456, y + 16), num, _font(20, bold=True), GOLD)
        _text(draw, (560, y + 20), label, _font(13), MUTED)
        y += 64


def write_screens(out_dir: Path | None = None) -> list[Path]:
    target = out_dir or SEED_DIR
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name, painter in (('admin.webp', _paint_admin), ('phone.webp', _paint_phone)):
        image = Image.new('RGB', (W, H), BG)
        painter(image)
        path = target / name
        image.save(path, format='WEBP', quality=86, method=6)
        written.append(path)
    return written
