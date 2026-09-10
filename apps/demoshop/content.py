"""Хелпери читання CMS-блоків демо-магазину для шаблонів вітрини."""
from django.utils import translation

from .block_defaults import BLOCK_REGISTRY


def get_blocks_map(shop) -> dict:
    """{'home__hero_title': ShopBlock, ...} — прямий доступ за page__key."""
    return {f'{block.page}__{block.key}': block for block in shop.blocks.all()}


def get_text(blocks_map: dict, page: str, key: str, default: str = '') -> str:
    lang = translation.get_language()
    block = blocks_map.get(f'{page}__{key}')
    if block:
        return block.localized_value

    for entry in BLOCK_REGISTRY:
        if entry['page'] == page and entry['key'] == key:
            if lang == 'en' and entry.get('default_en'):
                return entry['default_en']
            if lang == 'cs' and entry.get('default_cs'):
                return entry['default_cs']
            if lang == 'ru' and entry.get('default_ru'):
                return entry['default_ru']
            return entry.get('default', default)
    return default


def get_image_url(blocks_map: dict, page: str, key: str):
    block = blocks_map.get(f'{page}__{key}')
    if block and block.value_image:
        return block.value_image.url
    return None
