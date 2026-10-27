"""Початкові дані портфоліо для seed_portfolio_projects.

Кожен проєкт — реальний сайт клієнта PrometeyLabs (`site_url`). Знімки головної
сторінки (`static_card` / `static_card_mobile`) генеруються локально командою
`capture_portfolio_screens` (Playwright) і кладуться у
`static/images/portfolio/screens/<slug>-desktop.webp` / `-mobile.webp`.
"""
from apps.core.portfolio_seed_projects_1 import PORTFOLIO_PROJECTS_1
from apps.core.portfolio_seed_projects_2 import PORTFOLIO_PROJECTS_2
from apps.core.portfolio_seed_projects_3 import PORTFOLIO_PROJECTS_3

PORTFOLIO_PROJECTS = PORTFOLIO_PROJECTS_1 + PORTFOLIO_PROJECTS_2 + PORTFOLIO_PROJECTS_3

# ~6 сильних кейсів зі скрінами на головну (show_on_homepage). Інші лишаються False.
HOMEPAGE_SHOWCASE = {
    'fpsu': 1,
    'elit-fasad': 2,
    'playvision': 3,
    'beauty-opt': 4,
    'beautycake': 5,
    'fortprint': 6,
}
for _p in PORTFOLIO_PROJECTS:
    if _p['slug'] in HOMEPAGE_SHOWCASE:
        _p['show_on_homepage'] = True
        _p['home_order'] = HOMEPAGE_SHOWCASE[_p['slug']]
    else:
        _p['show_on_homepage'] = False

IMAGE_FIELD_MAP = (
    ('static_card', 'card_image'),
    ('static_card_mobile', 'card_image_mobile'),
)
