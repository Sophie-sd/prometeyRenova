"""URL для ImageField: файл у media, якщо він є на диску, інакше static seed.

На Render диск media зі збірки не потрапляє в runtime, а static віддається.
Імена збігаються з файлами в static/*/seed. Django-суфікс `_Ab12CdE` відкидається.
Слайди магазину збережені як hero-0-wide.webp, у static це slide-1-wide.webp.
"""
from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static

_INDEX: dict[str, list[str]] | None = None
_DJANGO_SUFFIX = re.compile(r'^(.+)_[A-Za-z0-9]{7}$')
_SHOP_HERO = re.compile(r'^hero-(\d+)-(wide|narrow)\.webp$')

_ROOTS = (
    'demoshop/seed',
    'democorp/seed',
    'demolanding/seed',
    'proposal/img',
    'images/portfolio/screens',
)


def _index() -> dict[str, list[str]]:
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    found: dict[str, list[str]] = {}
    base = Path(settings.BASE_DIR) / 'static'
    for root_name in _ROOTS:
        root = base / root_name
        if not root.is_dir():
            continue
        for path in root.rglob('*'):
            if path.suffix.lower() not in {'.webp', '.png', '.jpg', '.jpeg'}:
                continue
            rel = path.relative_to(base).as_posix()
            found.setdefault(path.name, []).append(rel)
    _INDEX = found
    return found


def _name_variants(stored_name: str) -> list[str]:
    filename = Path(stored_name).name
    names = [filename]
    hero = _SHOP_HERO.match(filename)
    if hero:
        number = int(hero.group(1)) + 1
        names.append(f'slide-{number}-{hero.group(2)}.webp')
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    match = _DJANGO_SUFFIX.match(stem)
    if match:
        names.append(f'{match.group(1)}{suffix}')
    return names


def _preferred_prefix(stored_name: str) -> str:
    if stored_name.startswith('democorp/'):
        return 'democorp/seed/'
    if stored_name.startswith('demolanding/'):
        return 'demolanding/seed/'
    if stored_name.startswith('demoshop/'):
        return 'demoshop/seed/'
    if stored_name.startswith('proposals/'):
        return 'proposal/img/'
    return ''


def static_rel_for(stored_name: str) -> str:
    """Відносний static-шлях за іменем файлу в media, або порожній рядок."""
    if not stored_name:
        return ''
    preferred = _preferred_prefix(stored_name)
    index = _index()
    for filename in _name_variants(stored_name):
        rels = index.get(filename) or []
        for rel in rels:
            if preferred and rel.startswith(preferred):
                return rel
        if rels and not preferred:
            return rels[0]
        if rels and preferred:
            continue
    for filename in _name_variants(stored_name):
        rels = index.get(filename) or []
        if rels:
            return rels[0]
    return ''


def media_if_exists(file_field) -> str:
    name = getattr(file_field, 'name', '') or ''
    if not name:
        return ''
    if (Path(settings.MEDIA_ROOT) / name).is_file():
        return file_field.url
    return ''


def public_file_url(file_field) -> str:
    """URL, який відкривається: media на диску або static seed."""
    direct = media_if_exists(file_field)
    if direct:
        return direct
    name = getattr(file_field, 'name', '') or ''
    rel = static_rel_for(name)
    if rel and (Path(settings.BASE_DIR) / 'static' / rel).is_file():
        return static(rel)
    return ''
