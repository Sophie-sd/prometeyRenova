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


# Same showcase on uk, ru and en. Ukrainian strings stay on the case dicts.
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


_CASE_I18N = {
    'ru': {
        'fpsu': {
            'title': 'Федерация профсоюзов Украины',
            'line': 'Официальный портал ФПУ: новости, документы, обращения',
            'badge': '30 дней',
            'task': 'Сделать официальный сайт Федерации профсоюзов Украины: крупной организации нужен портал, где видны структура, документы, новости и возможность обратиться в ФПУ.',
            'done': 'Собран многоуровневый корпоративный портал: разделы об организации и руководстве, направления деятельности, архив документов и постановлений, лента и архив новостей, поиск по сайту, опросы, форма обратной связи, материалы правовых консультаций. Есть английская версия интерфейса. Клиент обновляет заголовки, тексты и материалы через административную панель и видит заявки в мини-CRM.',
            'result': 'Сайт работает как официальная площадка ФПУ: новости публикуются, документы и структура организации доступны посетителю, обращение можно отправить с сайта. Клиент сам обновляет контент через админку.',
        },
        'ajeres': {
            'title': 'AJERES',
            'line': 'Сайт дистрибьютора для Узбекистана: три языка, каталог, заявки',
            'badge': '21 день',
            'task': 'Сделать корпоративный сайт дистрибьютора продуктов питания для рынка Узбекистана: представить компанию, ассортимент и собрать обращения от сетей, опта и HoReCa.',
            'done': 'Корпоративный сайт на трёх языках (русский, узбекский, английский) со страницами о компании и партнёрах, каталогом продукции по категориям и формой заявки. В футере сайта указана разработка PrometeyLabs. Контент и заявки клиент ведёт через админку и мини-CRM.',
            'result': 'Сайт работает для международного B2B-клиента на трёх языках, каталог и форма заявки доступны посетителю. Клиент сам обновляет контент и видит обращения в одной панели.',
        },
        'pokrivlya': {
            'title': 'Кровля под ключ',
            'line': 'Сайт кровельного подрядчика: услуги, объекты, заявка на смету',
            'badge': '14 дней',
            'task': 'Сделать сайт подрядной компании по монтажу и реконструкции кровли, чтобы посетитель видел услуги и объекты и мог оставить заявку на смету.',
            'done': 'Сайт услуг с разделами работ, портфолио реализованных объектов, графиком и контактами, чатом и формой бесплатной сметы (населённый пункт, тип работ, площадь, этажность, материал, телефон). Контент и заявки клиент ведёт через админку и мини-CRM.',
            'result': 'Заявку на смету можно оставить с сайта, объекты и условия работы компании собраны в одном месте. Клиент сам обновляет услуги и портфолио и видит обращения в панели.',
        },
    },
    'en': {
        'fpsu': {
            'title': 'Federation of Trade Unions of Ukraine',
            'line': 'Official FPU portal: news, documents, inquiries',
            'badge': '30 days',
            'task': 'Build the official website of the Federation of Trade Unions of Ukraine: a large organization needs a portal that shows its structure, documents, news, and a way to contact the FPU.',
            'done': 'A multi-level corporate portal: sections about the organization and leadership, areas of work, an archive of documents and resolutions, a news feed and archive, site search, polls, a feedback form, and legal consultation materials. The interface has an English version. The client updates headlines, texts, and materials in the admin panel and sees inquiries in a mini-CRM.',
            'result': 'The site works as the official FPU platform: news is published, documents and the organization structure are available to visitors, and an inquiry can be sent from the site. The client updates the content in the admin panel.',
        },
        'ajeres': {
            'title': 'AJERES',
            'line': 'A distributor site for Uzbekistan: three languages, a catalog, inquiries',
            'badge': '21 days',
            'task': 'Build a corporate website for a food distributor in Uzbekistan: present the company and the range, and collect inquiries from retail chains, wholesale, and HoReCa.',
            'done': 'A corporate site in three languages (Russian, Uzbek, and English) with pages about the company and partners, a product catalog by category, and an inquiry form. The footer credits PrometeyLabs. The client manages content and inquiries in the admin panel and mini-CRM.',
            'result': 'The site serves an international B2B client in three languages. The catalog and inquiry form are available to visitors. The client updates the content and sees inquiries in one panel.',
        },
        'pokrivlya': {
            'title': 'Turnkey roofing',
            'line': "A roofing contractor's site: services, projects, an estimate request",
            'badge': '14 days',
            'task': 'Build a site for a contractor that installs and rebuilds roofs, so a visitor can see the services and projects and request an estimate.',
            'done': 'A services site with work sections, a portfolio of completed projects, schedule and contacts, a chat, and a free estimate form (locality, type of work, area, number of floors, material, phone). The client manages content and inquiries in the admin panel and mini-CRM.',
            'result': 'An estimate request can be sent from the site. Projects and the company terms are in one place. The client updates services and the portfolio and sees inquiries in the panel.',
        },
    },
}

_TILE_I18N = {
    'ru': {
        'elit-fasad': 'Элит-Фасад Девелопмент',
        'ucvn': 'UCVN',
        'ofion': 'OFION',
        'droproom': 'DropRoom',
        'varvarova': 'VARVAROVA',
        'sonjashnyk': 'Соняшник',
        'nanesi': 'NANESI',
        'arktyka': 'Арктика',
    },
    'en': {
        'elit-fasad': 'Elit-Fasad Development',
        'ucvn': 'UCVN',
        'ofion': 'OFION',
        'droproom': 'DropRoom',
        'varvarova': 'VARVAROVA',
        'sonjashnyk': 'Соняшник',
        'nanesi': 'NANESI',
        'arktyka': 'Арктика',
    },
}


def _showcase_lang():
    code = (translation.get_language() or 'uk').split('-')[0]
    return code if code in ('uk', 'ru', 'en') else 'uk'


def _case_text(item, key):
    """Language pair with no Ukrainian fallback for ru/en."""
    code = _showcase_lang()
    if code == 'uk':
        return item[key]
    return _CASE_I18N[code][item['slug']][key]


def _tile_title(slug, title):
    code = _showcase_lang()
    if code == 'uk':
        return title
    return _TILE_I18N[code][slug]


def rozrobka_showcase():
    """3 cases and 8 tiles. ru/en copy is required; it is never filled from Ukrainian."""
    cases = []
    for item in _SHOWCASE_CASES:
        title = _case_text(item, 'title')
        cases.append({
            'slug': item['slug'],
            'url': item['url'],
            'image': item['image'],
            'width': item['width'],
            'height': item['height'],
            'title': title,
            'line': _case_text(item, 'line'),
            'badge': _case_text(item, 'badge'),
            'task': _case_text(item, 'task'),
            'done': _case_text(item, 'done'),
            'result': _case_text(item, 'result'),
            'src': static_url(item['image']),
            'alt': title,
        })
    tiles = []
    for slug, title, url, image, width, height in _SHOWCASE_TILES:
        localized = _tile_title(slug, title)
        tiles.append({
            'slug': slug,
            'title': localized,
            'url': url,
            'src': static_url(image),
            'alt': localized,
            'width': width,
            'height': height,
        })
    return {'cases': cases, 'tiles': tiles}
