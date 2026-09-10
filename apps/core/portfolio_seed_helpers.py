"""Компактний конструктор запису портфоліо для seed-файлів."""


def card(
    *,
    slug,
    title,
    subtitle,
    title_ru,
    subtitle_ru,
    desc,
    desc_ru,
    tags,
    site_url,
    order,
    locale='uk-UA',
    show_on_portfolio=True,
):
    return {
        'slug': slug,
        'title': title,
        'subtitle': subtitle,
        'title_ru': title_ru,
        'subtitle_ru': subtitle_ru,
        'card_description': desc,
        'card_description_ru': desc_ru,
        'integrations': '\n'.join(tags),
        'card_image_alt': f'{title} — {subtitle.lower()}',
        'card_image_alt_ru': f'{title_ru} — {subtitle_ru.lower()}',
        'site_url': site_url,
        'capture_locale': locale,
        'static_card': f'images/portfolio/screens/{slug}-desktop.webp',
        'static_card_mobile': f'images/portfolio/screens/{slug}-mobile.webp',
        'order': order,
        'home_order': 99,
        'show_on_portfolio': show_on_portfolio,
        'show_on_homepage': False,
    }


SHOP_TAGS = (
    'каталог товарів',
    'кошик і оформлення замовлення',
    'онлайн-оплата',
    'доставка по Україні',
)
CATALOG_TAGS = (
    'каталог продукції',
    'заявка на прорахунок',
    'галерея робіт',
    'контакти',
)
LANDING_TAGS = (
    'лендінг',
    'заявка / CTA',
    'опис послуги',
    'контакти',
)
CORP_TAGS = (
    'корпоративний сайт',
    'послуги та про компанію',
    'форма зворотного зв’язку',
    'контакти',
)
