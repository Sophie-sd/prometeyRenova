"""Каталог і контент демо-магазину меблів (static SVG, без media-завантажень)."""
from decimal import Decimal

ROOMS = [
    ('room-living', 'living', 'Вітальня'),
    ('room-bedroom', 'bedroom', 'Спальня'),
    ('room-kitchen', 'kitchen', 'Кухня та їдальня'),
    ('room-office', 'office', 'Кабінет'),
    ('room-kids', 'kids', 'Дитяча'),
]

THEME = {
    'color_primary': '#D9CBB8',
    'color_primary_hover': '#CBBBA5',
    'color_accent': '#6B2D2D',
    'color_surface': '#F6F1EA',
    'color_text': '#1F1B17',
}

UPHOLSTERY = [
    {'label': 'Тканина', 'delta': 0},
    {'label': 'Велюр', 'delta': 2800},
    {'label': 'Шкіра', 'delta': 11500},
]
FABRIC_COLORS = [
    {'label': 'Льон', 'code': 'ivory', 'delta': 0},
    {'label': 'Шавлія', 'code': 'sage', 'delta': 0},
    {'label': 'Графіт', 'code': 'graphite', 'delta': 0},
    {'label': 'Бордо', 'code': 'oxblood', 'delta': 400},
]
WOOD_COLORS = [
    {'label': 'Дуб натуральний', 'code': 'oak', 'delta': 0},
    {'label': 'Горіх', 'code': 'walnut', 'delta': 1500},
    {'label': 'Попіл', 'code': 'ash', 'delta': 0},
]


KIDS_COLORS = [
    {'label': 'Слонова кістка', 'code': 'ivory', 'delta': 0},
    {'label': 'Шавлія', 'code': 'sage', 'delta': 0},
    {'label': 'Попіл', 'code': 'ash', 'delta': 0},
]


def _sizes(*pairs):
    return [{'label': label, 'delta': delta} for label, delta in pairs]


# (slug, room, name, short, price, material, color, width_cm, image, featured, options)
PRODUCTS = [
    ('divan-nord', 'living', 'Диван «Норд»',
     'Модульний диван із глибоким сидінням і масивною опорою з бука.',
     32900, 'Тканина, масив бука', 'Льон', 180, 'sofa', True,
     {'upholstery': UPHOLSTERY, 'color': FABRIC_COLORS,
      'size': _sizes(('2-місний 180 см', 0), ('3-місний 220 см', 6500), ('Кутовий 280 см', 14000))}),
    ('krislo-lumi', 'living', 'Крісло «Люмі»',
     'Крісло з високою спинкою та каркасом із масиву дуба.',
     14900, 'Велюр, масив дуба', 'Шавлія', 80, 'armchair', True,
     {'upholstery': UPHOLSTERY, 'color': FABRIC_COLORS}),
    ('stolyk-arka', 'living', 'Журнальний столик «Арка»',
     'Низький столик із м’якими обрисами та натуральним шпоном.',
     8900, 'Масив дуба', 'Дуб натуральний', 90, 'coffee', False,
     {'color': WOOD_COLORS, 'size': _sizes(('90 см', 0), ('110 см', 2200))}),
    ('lizhko-sidar', 'bedroom', 'Ліжко «Сідар»',
     'Ліжко з м’яким узголів’ям і каркасом із масиву дуба.',
     27900, 'Масив дуба, тканина', 'Дуб натуральний', 160, 'bed', True,
     {'upholstery': UPHOLSTERY, 'color': WOOD_COLORS,
      'size': _sizes(('160×200', 0), ('180×200', 2800), ('200×200', 4200))}),
    ('shafa-lira', 'bedroom', 'Шафа «Ліра»',
     'Двостулкова шафа з тихим доведенням і продуманим внутрішнім наповненням.',
     38500, 'МДФ, шпон дуба', 'Дуб натуральний', 240, 'wardrobe', False,
     {'color': WOOD_COLORS, 'size': _sizes(('240 см', 0), ('280 см', 7000))}),
    ('tumba-milk', 'bedroom', 'Тумба «Мілк»',
     'Приліжкова тумба з двома шухлядами та плавним ходом.',
     6900, 'Шпон дуба', 'Попіл', 45, 'nightstand', False,
     {'color': WOOD_COLORS}),
    ('stil-dubrava', 'kitchen', 'Обідній стіл «Дубрава»',
     'Обідній стіл зі стільницею з масиву та тонкою обв’язкою.',
     24900, 'Масив дуба', 'Дуб натуральний', 160, 'dining', True,
     {'color': WOOD_COLORS, 'size': _sizes(('160 см', 0), ('180 см', 3500), ('220 см', 7800))}),
    ('stilets-rio', 'kitchen', 'Стілець «Ріо»',
     'Легкий стілець із ергономічною спинкою для щоденного користування.',
     4900, 'Масив дуба, тканина', 'Графіт', 45, 'chair', False,
     {'upholstery': UPHOLSTERY, 'color': FABRIC_COLORS}),
    ('stil-atlas', 'office', 'Письмовий стіл «Атлас»',
     'Робочий стіл зі шпону дуба, прихованою прокладкою кабелів і шухлядою.',
     17900, 'Шпон дуба, метал', 'Дуб натуральний', 140, 'desk', True,
     {'color': WOOD_COLORS, 'size': _sizes(('140 см', 0), ('160 см', 1800))}),
    ('shafa-liniya', 'office', 'Книжкова шафа «Лінія»',
     'Відкрита шафа з регульованими полицями для книжок і предметів інтер’єру.',
     21500, 'МДФ, шпон ясена', 'Попіл', 120, 'bookcase', False,
     {'color': WOOD_COLORS, 'size': _sizes(('120 см', 0), ('160 см', 4500))}),
    ('lizhko-misiats', 'kids', 'Дитяче ліжко «Місяць»',
     'Безпечне ліжко з масиву бука із заокругленими кутами.',
     15900, 'Масив бука', 'Слонова кістка', 90, 'kidsbed', True,
     {'color': KIDS_COLORS, 'size': _sizes(('80×160', 0), ('90×190', 1200))}),
    ('stil-horishok', 'kids', 'Дитячий стіл «Горішок»',
     'Компактний стіл для занять, що росте разом із дитиною.',
     7900, 'Фанера, масив бука', 'Дуб натуральний', 110, 'kidsdesk', False,
     {'color': WOOD_COLORS}),
]

HERO_TITLE = 'Меблі, у яких хочеться жити'
HERO_SUBTITLE = 'Масив дуба, тканини та шкіра. Обирайте оббивку, колір і розмір та одразу бачте ціну.'
HERO_CTA = 'Переглянути каталог'

BLOCKS = {
    ('header', 'shop_name'): 'Дім і Дуб · демо',
    ('header', 'announcement_text'): (
        'Доставка габаритних меблів до під’їзду · Консультація дизайнера · '
        'Збірка за домовленістю'
    ),
    ('home', 'about_title'): 'Інтер’єр, який збирається під вас',
    ('home', 'about_text'): (
        'Підбираємо оббивку, колір і габарити під ваш простір. '
        'Доставляємо великі меблі та допомагаємо з рішенням у кілька кліків.'
    ),
    ('home', 'stat_orders'): '1 200+',
    ('home', 'stat_clients'): '950+',
    ('home', 'stat_rating'): '4.9 / 5',
    ('catalog', 'catalog_title'): 'Каталог меблів',
    ('catalog', 'catalog_subtitle'): 'Оберіть кімнату, розмір або матеріал',
    ('pdp', 'delivery_text'): (
        'Вантажні відділення перевізників або кур’єрська доставка до під’їзду чи квартири. '
        'Вартість розраховується в кошику. Демо: реальні замовлення не обробляються.'
    ),
    ('footer', 'footer_text'): 'Демо-магазин меблів від PrometeyLabs. Не версія вашого сайту.',
    ('footer', 'footer_phone'): '+38 (050) 000-00-00',
    ('footer', 'footer_email'): 'hello@example.com',
}


def _all_langs(text: str) -> dict:
    return {
        'value_text': text,
        'value_text_ru': text,
        'value_text_en': text,
        'value_text_cs': text,
    }


def seed_catalog(shop, stdout=None) -> int:
    """Ідемпотентно: оновлює свої записи, прибирає чужі generic-seed (за slug)."""
    from apps.demoshop.catalog_models import ShopCategory, ShopProduct, ShopReview
    from apps.demoshop.content_models import ShopBlock, ShopHeroSlide

    cat_slugs = [slug for slug, _room, _name in ROOMS]
    prod_slugs = [row[0] for row in PRODUCTS]
    ShopProduct.objects.filter(shop=shop).exclude(slug__in=prod_slugs).delete()
    ShopCategory.objects.filter(shop=shop).exclude(slug__in=cat_slugs).delete()
    ShopReview.objects.filter(shop=shop).delete()
    ShopHeroSlide.objects.filter(shop=shop).delete()

    for (page, key), text in BLOCKS.items():
        ShopBlock.objects.update_or_create(
            shop=shop, page=page, key=key,
            defaults={**_all_langs(text), 'block_type': 'text'},
        )
    # Прибираємо зображення «Про нас» зі старого generic seed: hero і картки статичні
    ShopBlock.objects.filter(shop=shop, page='home', key='about_image').delete()

    ShopHeroSlide.objects.create(
        shop=shop,
        title=HERO_TITLE, title_ru=HERO_TITLE, title_en=HERO_TITLE, title_cs=HERO_TITLE,
        subtitle=HERO_SUBTITLE, subtitle_ru=HERO_SUBTITLE,
        subtitle_en=HERO_SUBTITLE, subtitle_cs=HERO_SUBTITLE,
        cta_label=HERO_CTA, cta_label_ru=HERO_CTA, cta_label_en=HERO_CTA, cta_label_cs=HERO_CTA,
        order=0, is_active=True,
    )

    categories = {}
    for idx, (slug, _room, name) in enumerate(ROOMS):
        categories[_room], _ = ShopCategory.objects.update_or_create(
            shop=shop, slug=slug,
            defaults={
                'name': name, 'name_ru': name, 'name_en': name, 'name_cs': name,
                'icon': '', 'order': idx, 'is_active': True,
            },
        )

    for order, (slug, room, name, short, price, material, color, width, image, featured, options) in enumerate(PRODUCTS):
        description = (
            f'{short} Матеріал: {material}. '
            'Оберіть оббивку, колір і розмір: ціна оновиться одразу.'
        )
        ShopProduct.objects.update_or_create(
            shop=shop, slug=slug,
            defaults={
                'category': categories[room],
                'name': name, 'name_ru': name, 'name_en': name, 'name_cs': name,
                'short_description': short, 'short_description_ru': short,
                'short_description_en': short, 'short_description_cs': short,
                'description': description, 'description_ru': description,
                'description_en': description, 'description_cs': description,
                'price': Decimal(price),
                'old_price': None,
                'sale_end_date': None,
                'gift_promo_text': '',
                'material': material,
                'room': room,
                'color': color,
                'width_cm': width,
                'static_image': f'demoshop/seed/furniture/{image}.svg',
                'variant_options': options,
                'is_featured': featured,
                'is_active': True,
                'order': order,
            },
        )
    return len(PRODUCTS)
