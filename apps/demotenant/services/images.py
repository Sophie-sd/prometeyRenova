"""Завантаження seed-зображень: спочатку `static/<app>/seed/…`, інакше
Pillow-плейсхолдер (ERR-74: fallback не мовчить, пише warning у консоль).
Копія логіки `apps.demoshop.services.images`, параметризована коренем seed.
"""
from __future__ import annotations

import hashlib
import io
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

PALETTE = ['#E65100', '#7B2CBF', '#0F766E', '#B45309', '#1D4ED8', '#BE123C']


def _pick_color(seed: str) -> str:
    idx = int(hashlib.sha1(seed.encode('utf-8')).hexdigest(), 16) % len(PALETTE)
    return PALETTE[idx]


def _load_font(size: int):
    try:
        return ImageFont.truetype('DejaVuSans-Bold.ttf', size)
    except OSError:
        return ImageFont.load_default()


def generate_placeholder(width: int, height: int, label: str, seed: str = '') -> ContentFile:
    seed = seed or label
    color = _pick_color(seed)
    image = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(image)

    text = (label or '').strip()[:28]
    font_size = max(14, min(width, height) // 8)
    font = _load_font(font_size)
    if text:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((width - text_w) / 2, (height - text_h) / 2),
            text,
            font=font,
            fill='#FFFFFF',
        )

    buffer = io.BytesIO()
    image.save(buffer, format='WEBP', quality=82)
    filename = f'{hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]}.webp'
    return ContentFile(buffer.getvalue(), name=filename)


def load_seed_image(seed_root: Path, relative_path: str, fallback_label: str = '', size=(800, 800)) -> ContentFile:
    """Читає WEBP з `seed_root/relative_path`; якщо немає — placeholder."""
    path = seed_root / relative_path
    if path.is_file():
        return ContentFile(path.read_bytes(), name=path.name)
    width, height = size
    print(f'[demotenant seed] missing image {relative_path} (root={seed_root}), using placeholder')
    return generate_placeholder(width, height, fallback_label or path.stem, seed=relative_path)
