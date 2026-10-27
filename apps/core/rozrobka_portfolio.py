"""«Наші роботи» on /rozrobka-sajtiv/ (ТЗ 27.10.2026 п. 3.6): a fixed set of 10 cases.

Mostly landings and corporate sites (that is what the page's queries are about),
one shop, two platforms. Names, niches and alts come from the same seed data as
/portfolio/ (uk + ru); screenshots are the same static full-page shots with the
720w preview variant. Cards link only to /portfolio/ — no client-site URLs.
"""
from types import SimpleNamespace

from django.templatetags.static import static as static_url
from django.utils import translation

from apps.core.portfolio_categories import (
    CATEGORY_CORPORATE,
    CATEGORY_LANDING,
    CATEGORY_PLATFORM,
    CATEGORY_SHOP,
    card_label,
)
from apps.core.portfolio_images import resolve_static_portfolio_srcset
from apps.core.portfolio_seed_data import PORTFOLIO_PROJECTS

# Order = order of the cards in the slider.
RS_PORTFOLIO = (
    ('fpsu', CATEGORY_CORPORATE),
    ('elit-fasad', CATEGORY_LANDING),
    ('diodi', CATEGORY_CORPORATE),
    ('grand-oblik', CATEGORY_LANDING),
    ('playvision', CATEGORY_PLATFORM),
    ('phoenixvet', CATEGORY_CORPORATE),
    ('queendrive', CATEGORY_LANDING),
    ('beauty-opt', CATEGORY_SHOP),
    ('znomax', CATEGORY_PLATFORM),
    ('fortprint', CATEGORY_CORPORATE),
)


def rozrobka_portfolio_cards():
    """List of card dicts: slug, title, niche, type_label, alt, src, srcset."""
    ru = (translation.get_language() or '').startswith('ru')
    seeds = {item['slug']: item for item in PORTFOLIO_PROJECTS}
    cards = []
    for slug, category in RS_PORTFOLIO:
        item = seeds.get(slug)
        if not item or not item.get('static_card'):
            continue

        def pick(key):
            return (ru and item.get(f'{key}_ru')) or item.get(key) or ''

        cards.append({
            'slug': slug,
            'title': pick('title'),
            'niche': pick('subtitle'),
            'type_label': card_label(category),
            'alt': pick('card_image_alt') or pick('title'),
            'src': static_url(item['static_card']),
            'srcset': resolve_static_portfolio_srcset(SimpleNamespace(slug=slug), 'card_image'),
        })
    return cards
