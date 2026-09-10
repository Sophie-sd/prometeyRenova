"""Runtime-читання CMS-блоків тенанта у view/template (реєстр з `registry.py`)."""
from __future__ import annotations

from django.utils.translation import get_language

from .registry import get_entry


def get_blocks_map(tenant) -> dict:
    return {f'{b.page}__{b.key}': b for b in tenant.blocks.all()}


def _entry_default(entry: dict, lang: str) -> str:
    if lang == 'en' and entry.get('default_en'):
        return entry['default_en']
    if lang == 'ru' and entry.get('default_ru'):
        return entry['default_ru']
    if lang == 'cs' and entry.get('default_cs'):
        return entry['default_cs']
    return entry.get('default', '')


def get_text(blocks_map: dict, registry: list[dict], page: str, key: str) -> str:
    block = blocks_map.get(f'{page}__{key}')
    if block and block.localized_value:
        return block.localized_value
    entry = get_entry(registry, page, key)
    if not entry:
        return ''
    return _entry_default(entry, get_language())


def get_image_url(blocks_map: dict, page: str, key: str) -> str | None:
    block = blocks_map.get(f'{page}__{key}')
    if block and block.value_image:
        return block.value_image.url
    return None


def is_visible(blocks_map: dict, page: str, key: str, *, default: bool = True) -> bool:
    """`key` — зазвичай `*_visible`. Немає запису = дефолт (секція показана)."""
    block = blocks_map.get(f'{page}__{key}')
    if block is None:
        return default
    return block.value_text != '0'
