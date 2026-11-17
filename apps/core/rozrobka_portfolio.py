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


# Ukrainian /rozrobka-sajtiv/ replacement (handoff/TEXTS.md). Russian keeps RS_PORTFOLIO.
_SHOWCASE_CASES = (
    {
        'slug': 'fpsu',
        'title': 'Федерація профспілок України',
        'url': 'https://www.fpsu.org.ua/',
        'line': 'Офіційний портал ФПУ: новини, документи, звернення',
        'badge': '30 днів',
        'image': 'images/portfolio/screens/fpsu-desktop-720.webp',
        'width': 720,
        'height': 1233,
        'task': 'Зробити офіційний сайт Федерації профспілок України: великій організації потрібен портал, де видно структуру, документи, новини й можливість звертатись до ФПУ.',
        'done': 'Зібрано багаторівневий корпоративний портал: розділи про організацію та керівництво, напрями діяльності, архів документів і постанов, стрічка й архів новин, пошук по сайту, опитування, форма зворотного зв’язку, матеріали правових консультацій. Є англійська версія інтерфейсу. Клієнт оновлює заголовки, тексти й матеріали через адміністративну панель і бачить заявки в міні-CRM.',
        'result': 'Сайт працює як офіційний майданчик ФПУ: новини публікуються, документи й структура організації доступні відвідувачу, звернення можна надіслати з сайту. Клієнт сам оновлює контент через адмінку.',
    },
    {
        'slug': 'ajeres',
        'title': 'AJERES',
        'url': 'https://ajeres.uz/',
        'line': 'Сайт дистриб’ютора для Узбекистану: три мови, каталог, заявки',
        'badge': '21 день',
        'image': 'images/portfolio/screens/ajeres-desktop-720.webp',
        'width': 720,
        'height': 1480,
        'task': 'Зробити корпоративний сайт дистриб’ютора продуктів харчування для ринку Узбекистану: представити компанію, асортимент і зібрати звернення від мереж, опту та HoReCa.',
        'done': 'Корпоративний сайт трьома мовами (російська, узбецька, англійська) зі сторінками про компанію й партнерів, каталогом продукції за категоріями та формою заявки. У футері сайту вказано розробку PrometeyLabs. Контент і заявки клієнт веде через адмінку та міні-CRM.',
        'result': 'Сайт працює для міжнародного B2B-клієнта трьома мовами, каталог і форма заявки доступні відвідувачу. Клієнт сам оновлює контент і бачить звернення в одній панелі.',
    },
    {
        'slug': 'pokrivlya',
        'title': 'Покрівля під ключ',
        'url': 'https://pokrivlya.com.ua/',
        'line': 'Сайт покрівельного підрядника: послуги, об’єкти, заявка на кошторис',
        'badge': '14 днів',
        'image': 'images/portfolio/screens/pokrivlya-desktop-720.webp',
        'width': 720,
        'height': 2498,
        'task': 'Зробити сайт підрядної компанії з монтажу та реконструкції покрівлі, щоб відвідувач бачив послуги й об’єкти та міг залишити заявку на кошторис.',
        'done': 'Сайт послуг із розділами робіт, портфоліо реалізованих об’єктів, графіком і контактами, чатом і формою безкоштовного кошторису (населений пункт, тип робіт, площа, поверховість, матеріал, телефон). Контент і заявки клієнт веде через адмінку та міні-CRM.',
        'result': 'Заявку на кошторис можна залишити з сайту, об’єкти й умови роботи компанії зібрані в одному місці. Клієнт сам оновлює послуги й портфоліо та бачить звернення в панелі.',
    },
)

_SHOWCASE_TILES = (
    ('elit-fasad', 'Еліт-Фасад Девелопмент', 'https://elit-fasad-development.com.ua/', 'images/portfolio/screens/elit-fasad-desktop-720.webp', 720, 3000),
    ('ucvn', 'UCVN', 'https://ucvn.com.ua/', 'images/portfolio/screens/ucvn-desktop-720.webp', 720, 3000),
    ('ofion', 'OFION', 'https://ofion.com.ua/', 'images/portfolio/screens/ofion-desktop-720.webp', 720, 2490),
    ('droproom', 'DropRoom', 'https://droproom.com.ua/', 'images/portfolio/screens/droproom-desktop-720.webp', 720, 3000),
    ('varvarova', 'VARVAROVA', 'https://varvarova-bridal.com/', 'images/rozrobka/portfolio/tile-varvarova.webp', 1200, 685),
    ('sonjashnyk', 'Соняшник', 'https://sonjashnik.ua/', 'images/rozrobka/portfolio/tile-sonjashnyk.webp', 1200, 685),
    ('nanesi', 'NANESI', 'https://nanesi.com.ua/', 'images/rozrobka/portfolio/tile-nanesi.webp', 1200, 684),
    ('arktyka', 'Арктика', 'https://arctica.od.ua/', 'images/rozrobka/portfolio/tile-arktyka.webp', 1200, 683),
)


def rozrobka_showcase():
    """Ukrainian portfolio replacement: 3 cases with details and 8 external tiles."""
    cases = []
    for item in _SHOWCASE_CASES:
        cases.append({
            **item,
            'src': static_url(item['image']),
            'alt': item['title'],
        })
    tiles = []
    for slug, title, url, image, width, height in _SHOWCASE_TILES:
        tiles.append({
            'slug': slug,
            'title': title,
            'url': url,
            'src': static_url(image),
            'alt': title,
            'width': width,
            'height': height,
        })
    return {'cases': cases, 'tiles': tiles}
