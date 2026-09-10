"""Seed-колекції demo-лендінгу PrometeyLabs (UA/EN/CS/RU)."""

OFFERS = [
    {
        'title': 'Усі потрібні блоки й меню',
        'title_en': 'All the blocks and menu you need',
        'title_cs': 'Všechny potřebné bloky a menu',
        'title_ru': 'Все нужные блоки и меню',
        'description': 'Головний екран, переваги, приклади, відгуки, питання й форма. Людина не заблукає.',
        'description_en': 'Main screen, benefits, examples, reviews, questions and a form. Nobody gets lost.',
        'description_cs': 'Hlavní obrazovka, výhody, příklady, recenze, otázky a formulář. Člověk se neztratí.',
        'description_ru': 'Главный экран, преимущества, примеры, отзывы, вопросы и форма. Человек не заблудится.',
        'price_from': None, 'image': 'offers/turnkey.webp',
    },
    {
        'title': 'Соцмережі та заявки',
        'title_en': 'Socials and requests',
        'title_cs': 'Sítě a poptávky',
        'title_ru': 'Соцсети и заявки',
        'description': 'Кнопки в Instagram, Facebook і Telegram. Заявка з сайту приходить вам.',
        'description_en': 'Buttons to Instagram, Facebook and Telegram. A request from the site comes to you.',
        'description_cs': 'Tlačítka na Instagram, Facebook a Telegram. Poptávka ze webu přijde vám.',
        'description_ru': 'Кнопки в Instagram, Facebook и Telegram. Заявка с сайта приходит вам.',
        'price_from': None, 'image': 'offers/renovation.webp',
    },
    {
        'title': 'Самі правите сайт',
        'title_en': 'You edit the site yourself',
        'title_cs': 'Web upravujete sami',
        'title_ru': 'Сами правите сайт',
        'description': 'Тексти, фото й кольори в простій адмінці. Без програміста на кожне «змініть слово».',
        'description_en': 'Texts, photos and colors in a simple admin. No developer for every “change this word”.',
        'description_cs': 'Texty, fotky a barvy v jednoduchém adminu. Bez programátora na každé «změňte slovo».',
        'description_ru': 'Тексты, фото и цвета в простой админке. Без программиста на каждое «измените слово».',
        'price_from': None, 'image': 'offers/facade.webp',
    },
    {
        'title': 'Швидко і зручно з телефону',
        'title_en': 'Fast and easy on the phone',
        'title_cs': 'Rychle a pohodlně v telefonu',
        'title_ru': 'Быстро и удобно с телефона',
        'description': 'Відкривається одразу. Реклама менше зливається, бо сторінка не відлякує.',
        'description_en': 'It opens right away. Ads waste less money because the page does not scare people away.',
        'description_cs': 'Otevře se hned. Reklama míň utíká, protože stránka lidi neodrazuje.',
        'description_ru': 'Открывается сразу. Реклама меньше сливается, потому что страница не отпугивает.',
        'price_from': None, 'image': 'offers/roof.webp',
    },
]

TESTIMONIALS = [
    {
        'author_name': 'Олена К.', 'role': 'Салон краси, Львів', 'rating': 5,
        'text': 'Люди пишуть самі, я більше не пояснюю послуги в Direct по десять разів.',
        'text_en': 'People write themselves — I no longer explain services in Direct ten times.',
        'text_cs': 'Lidé píšou sami, už desetkrát nevysvětluju služby v Directu.',
        'text_ru': 'Люди пишут сами, я больше не объясняю услуги в Direct по десять раз.',
    },
    {
        'author_name': 'Ігор М.', 'role': 'Кавʼярня, Київ', 'rating': 5,
        'text': 'З телефону все одразу зрозуміло. Заявки на каву йдуть навіть вночі.',
        'text_en': 'Everything is clear on the phone. Coffee orders come even at night.',
        'text_cs': 'V telefonu je vše hned jasné. Poptávky na kávu chodí i v noci.',
        'text_ru': 'С телефона всё сразу понятно. Заявки на кофе идут даже ночью.',
    },
    {
        'author_name': 'Петро С.', 'role': 'Репетитор', 'rating': 5,
        'text': 'Одна сторінка замість трьох зошитів у Instagram.',
        'text_en': 'One page instead of three notebooks in Instagram.',
        'text_cs': 'Jedna stránka místo tří sešitů na Instagramu.',
        'text_ru': 'Одна страница вместо трёх тетрадей в Instagram.',
    },
    {
        'author_name': 'Марина Т.', 'role': 'Клініка', 'rating': 5,
        'text': 'Заявки в одній адмінці, тексти міняю сама за хвилину.',
        'text_en': 'Requests in one admin — I change the texts myself in a minute.',
        'text_cs': 'Poptávky v jednom adminu, texty měním sama za minutu.',
        'text_ru': 'Заявки в одной админке, тексты меняю сама за минуту.',
    },
    {
        'author_name': 'Дмитро В.', 'role': 'Магазин', 'rating': 5,
        'text': 'Реклама стала дешевша: менше людей тікає зі сторінки.',
        'text_en': 'Ads got cheaper: fewer people run away from the page.',
        'text_cs': 'Reklama je levnější: míň lidí utíká ze stránky.',
        'text_ru': 'Реклама стала дешевле: меньше людей убегает со страницы.',
    },
]

PARTNERS = ['Google', 'TikTok', 'Viber', 'YouTube', 'WhatsApp', 'Maps']

GALLERY = [
    {'image': 'gallery/site-1.webp', 'span': '1x1',
     'caption': 'Картки, що нахиляються', 'caption_en': 'Cards that tilt',
     'caption_cs': 'Karty, které se naklánějí', 'caption_ru': 'Карточки, которые наклоняются'},
    {'image': 'gallery/site-2.webp', 'span': '1x1',
     'caption': 'До і після одним пальцем', 'caption_en': 'Before and after with one finger',
     'caption_cs': 'Před a po jedním prstem', 'caption_ru': 'До и после одним пальцем'},
    {'image': 'gallery/site-3.webp', 'span': '1x1',
     'caption': 'Стрічка, що їде сама', 'caption_en': 'A strip that moves by itself',
     'caption_cs': 'Páska, která jede sama', 'caption_ru': 'Лента, которая едет сама'},
    {'image': 'gallery/site-4.webp', 'span': '1x1',
     'caption': 'Меню, зручне з телефону', 'caption_en': 'A menu that works on the phone',
     'caption_cs': 'Menu pohodlné v telefonu', 'caption_ru': 'Меню, удобное с телефона'},
    {'image': 'gallery/site-5.webp', 'span': '1x1',
     'caption': 'Цифри, що рахуються', 'caption_en': 'Numbers that count up',
     'caption_cs': 'Čísla, která se načítají', 'caption_ru': 'Цифры, которые считаются'},
    {'image': 'gallery/site-6.webp', 'span': '1x1',
     'caption': 'Форма, після якої вам пишуть', 'caption_en': 'A form after which people write to you',
     'caption_cs': 'Formulář, po kterém vám napíšou', 'caption_ru': 'Форма, после которой вам пишут'},
]

BEFORE_AFTER = [
    {'title': 'Сторінка з конструктора → зібрана під вас',
     'before': 'before_after/facade-before.webp',
     'after': 'before_after/facade-after.webp'},
    {'title': 'З телефону незручно → зручно з першого дотику',
     'before': 'before_after/roof-before.webp',
     'after': 'before_after/roof-after.webp'},
]
