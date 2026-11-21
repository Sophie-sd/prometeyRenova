"""Literal TZ copy for ads landings (uk/ru, and en where a landing has it).

Visible FAQ and JSON-LD share these lists. ``lang()`` may return ``en``;
``for_lang`` falls back to ``uk`` for any dict that has no English entry.
"""
from django.utils import translation

SITE = 'https://www.prometeylabs.com'

PROCESS_SITE = {
    'uk': {
        'title': 'Як ми створюємо сайт',
        'note': 'Точний час залежить від складності дизайну та інтеграцій — визначаємо на консультації',
        'steps': [
            ('Збір інформації', 'бриф, цілі, аудиторія'),
            ('Карта сайту', 'структура і навігація'),
            ('Приклад дизайну', 'UI/UX-макети'),
            ('Функціональна модель', 'прототип і логіка форм'),
            ('Допрацювання', 'тестування на пристроях'),
            ('Деплой і передача прав', 'домен, SSL, доступи, інструкції'),
        ],
    },
    'ru': {
        'title': 'Как мы создаём сайт',
        'note': 'Точное время зависит от сложности дизайна и интеграций — определяем на консультации',
        'steps': [
            ('Сбор информации', 'бриф, цели, аудитория'),
            ('Карта сайта', 'структура и навигация'),
            ('Пример дизайна', 'UI/UX-макеты'),
            ('Функциональная модель', 'прототип и логика форм'),
            ('Доработка', 'тестирование на устройствах'),
            ('Деплой и передача прав', 'домен, SSL, доступы, инструкции'),
        ],
    },
}

CONTACTS = {
    'uk': {
        'h2': 'Контакти PrometeyLabs',
        'phone': '+38 (063) 952-05-65',
        'email': 'info@prometeylabs.com',
        'telegram': 'Telegram @prometeylabs',
        'address': 'Київ, бульвар Тараса Шевченка 46а',
        'hours': 'цілодобово',
        'executor': 'Виконавець: ФОП Дмитренко Софія Дмитрівна, публічний договір —',
        'offer_label': '/offer/',
    },
    'ru': {
        'h2': 'Контакты PrometeyLabs',
        'phone': '+38 (063) 952-05-65',
        'email': 'info@prometeylabs.com',
        'telegram': 'Telegram @prometeylabs',
        'address': 'Киев, бульвар Тараса Шевченко 46а',
        'hours': 'круглосуточно',
        'executor': 'Исполнитель: ФЛП Дмитренко София Дмитриевна, публичный договор —',
        'offer_label': '/offer/',
    },
}

CRUMBS = {
    'uk': {'home': 'Головна', 'services': 'Послуги'},
    'ru': {'home': 'Главная', 'services': 'Услуги'},
    'en': {'home': 'Home', 'services': 'Services'},
}

SHOP = {
    'uk': {
        'title': 'Створення інтернет-магазину під ключ — ціна від 650 € | PrometeyLabs',
        'description': (
            'Створити або замовити інтернет-магазин під ключ від 650 €: дизайн, код, LiqPay, Mono, '
            'Нова Пошта. Запуск за 3 тижні, 1 рік підтримки безкоштовно.'
        ),
        'h1': 'Створення інтернет-магазину під ключ',
        'line': (
            'Розробка інтернет-магазину від 650 €: запуск за 3 тижні, 1 рік підтримки безкоштовно '
            'і пожиттєва гарантія на код.'
        ),
        'lead': 'Дизайн, код і інтеграції. Без плагінів і без щомісячної абонплати. Магазин залишається вашим.',
        'form_note': 'Телефон потрібен, щоб менеджер передзвонив і назвав орієнтовну вартість.',
        'privacy_before': 'Надсилаючи заявку, ви погоджуєтесь з',
        'privacy_link': 'політикою конфіденційності',
        'trust': (
            '30+ розроблених інтернет-магазинів · Ціна і строк у договорі · '
            'Відповідаємо протягом 15 хвилин · Оплата частинами до 15 платежів'
        ),
        'crumb': 'Інтернет-магазини',
        'prices_h2': 'Скільки коштує створення інтернет-магазину',
        'include_h3': 'Що входить у Base',
        'include': (
            'каталог до 100 товарів, дизайн, мобільна версія, базова SEO, LiqPay і Mono, '
            'Нова Пошта, адмінка, кошик, оплата/доставка-основа, адмінка замовлень'
        ),
        'exclude_h3': 'Що не входить',
        'exclude': 'наповнення товарів, маркетинг, кастомні інтеграції; рекламний бюджет оплачується окремо',
        'process_h2': 'Як ми створюємо інтернет-магазин: від брифу до запуску за 14–21 день',
        'offer_line': 'Гарантію закріплено в публічному договорі (п. 8 оферти)',
        'faq_h2': 'Часті питання про створення інтернет-магазину',
        'faq': [
            (
                'Скільки коштує створити інтернет-магазин?',
                'Базовий магазин (до 100 товарів, дизайн, мобільна версія, LiqPay і Mono, Нова Пошта, адмінка) — від 650 €. '
                'Магазин з CRM, Telegram-сповіщеннями та налаштуванням рекламного кабінету — від 1 500 €. '
                'Магазин з маркетингом і SEO — від 7 000 €. Точну суму і строк фіксуємо в договорі.',
            ),
            (
                'Скільки часу займає розробка інтернет-магазину?',
                'Запуск за 3 тижні (14–21 день) для магазину з каталогом, кошиком, оплатою і доставкою.',
            ),
            (
                'Чи буде щомісячна абонплата або комісія?',
                'Ні. Без плагінів і без щомісячної абонплати, без комісій платформ. Магазин залишається вашим.',
            ),
            (
                'Що з гарантією і підтримкою?',
                'Пожиттєва гарантія на код: технічні баги з нашої вини виправляємо безкоштовно, без обмеження строку. '
                'Плюс 1 рік безкоштовної підтримки: технічні питання, дрібні правки та консультації.',
            ),
            (
                'Чи перенесете товари з Prom, Rozetka, Хорошоп або WooCommerce?',
                'Так. Парсинг з будь-якого сайту, 100 000+ SKU за один прохід, повна міграція за 24 години.',
            ),
            (
                'Чи можна оплатити частинами?',
                'Так, до 15 платежів через «Покупку частинами monobank».',
            ),
            (
                'Чи складно керувати магазином?',
                'Україномовна адмінка: новий менеджер опанує її за 15 хвилин. Оновлення залишків, цін і обробка замовлень — в 1–2 кліки.',
            ),
        ],
    },
    'ru': {
        'title': 'Создание интернет-магазина под ключ — цена от 650 € | PrometeyLabs',
        'description': (
            'Создать или заказать интернет-магазин под ключ от 650 €: дизайн, код, LiqPay, Mono, '
            'Новая Почта. Запуск за 3 недели, 1 год поддержки бесплатно.'
        ),
        'h1': 'Создание интернет-магазина под ключ',
        'line': (
            'Разработка интернет-магазина от 650 €: запуск за 3 недели, 1 год поддержки бесплатно '
            'и пожизненная гарантия на код.'
        ),
        'lead': 'Дизайн, код и интеграции. Без плагинов и без ежемесячной абонплаты. Магазин остаётся вашим.',
        'form_note': 'Телефон нужен, чтобы менеджер перезвонил и назвал ориентировочную стоимость.',
        'privacy_before': 'Отправляя заявку, вы соглашаетесь с',
        'privacy_link': 'политикой конфиденциальности',
        'trust': (
            '30+ разработанных интернет-магазинов · Цена и срок в договоре · '
            'Отвечаем в течение 15 минут · Оплата частями до 15 платежей'
        ),
        'crumb': 'Интернет-магазины',
        'prices_h2': 'Сколько стоит создание интернет-магазина',
        'include_h3': 'Что входит в Base',
        'include': (
            'каталог до 100 товаров, дизайн, мобильная версия, базовое SEO, LiqPay и Mono, '
            'Новая Почта, админка, корзина, оплата/доставка-основа, админка заказов'
        ),
        'exclude_h3': 'Что не входит',
        'exclude': 'наполнение товаров, маркетинг, кастомные интеграции; рекламный бюджет оплачивается отдельно',
        'process_h2': 'Как мы создаём интернет-магазин: от брифа до запуска за 14–21 день',
        'offer_line': 'Гарантию закреплено в публичном договоре (п. 8 оферты)',
        'faq_h2': 'Частые вопросы о создании интернет-магазина',
        'faq': [
            (
                'Сколько стоит создать интернет-магазин?',
                'Базовый магазин (до 100 товаров, дизайн, мобильная версия, LiqPay и Mono, Новая Почта, админка) — от 650 €. '
                'Магазин с CRM, Telegram-уведомлениями и настройкой рекламного кабинета — от 1 500 €. '
                'Магазин с маркетингом и SEO — от 7 000 €. Точную сумму и срок фиксируем в договоре.',
            ),
            (
                'Сколько времени занимает разработка интернет-магазина?',
                'Запуск за 3 недели (14–21 день) для магазина с каталогом, корзиной, оплатой и доставкой.',
            ),
            (
                'Будет ли ежемесячная абонплата или комиссия?',
                'Нет. Без плагинов и без ежемесячной абонплаты, без комиссий платформ. Магазин остаётся вашим.',
            ),
            (
                'Что с гарантией и поддержкой?',
                'Пожизненная гарантия на код: технические баги по нашей вине исправляем бесплатно, без ограничения срока. '
                'Плюс 1 год бесплатной поддержки: технические вопросы, мелкие правки и консультации.',
            ),
            (
                'Перенесёте товары с Prom, Rozetka, Хорошоп или WooCommerce?',
                'Да. Парсинг с любого сайта, 100 000+ SKU за один проход, полная миграция за 24 часа.',
            ),
            (
                'Можно оплатить частями?',
                'Да, до 15 платежей через «Покупку частями monobank».',
            ),
            (
                'Сложно ли управлять магазином?',
                'Украиноязычная админка: новый менеджер освоит её за 15 минут. Обновление остатков, цен и обработка заказов — в 1–2 клика.',
            ),
        ],
    },
    'en': {
        'title': 'Turnkey online store development — price from €650 | PrometeyLabs',
        'description': (
            'Create or order a turnkey online store from €650: design, code, LiqPay, Mono, '
            'Nova Poshta. Launch in 3 weeks, 1 year of free support.'
        ),
        'h1': 'Turnkey online store development',
        'line': (
            'Online store development from €650 · launch in 3 weeks · 1 year of free support · '
            'lifetime code warranty.'
        ),
        'lead': 'Design, code and integrations. No plugins and no monthly fees. The store stays yours.',
        'crumb': 'E-commerce stores',
        'prices_h2': 'How much does it cost to create an online store',
        'offer_line': 'The warranty is set out in the public contract (clause 8 of the offer)',
        'faq_h2': 'Frequently asked questions about creating an online store',
        'faq': [
            (
                'How much does it cost to create an online store?',
                'A basic store (up to 100 products, design, mobile version, LiqPay and Mono, Nova Poshta, admin panel) — from €650. '
                'A store with CRM, Telegram notifications and ad account setup — from €1,500. '
                'A store with marketing and SEO — from €7,000. The exact amount and deadline are fixed in the contract.',
            ),
            (
                'How long does online store development take?',
                'Launch in 3 weeks (14–21 days) for a store with a catalog, cart, payment and delivery.',
            ),
            (
                'Will there be a monthly subscription fee or commission?',
                'No. No plugins, no monthly subscription fee, and no platform commissions. The store remains yours.',
            ),
            (
                'What about the warranty and support?',
                'Lifetime code warranty: technical bugs caused by us are fixed free of charge, with no time limit. '
                'Plus 1 year of free support: technical questions, minor edits and consultations.',
            ),
            (
                'Will you migrate products from Prom, Rozetka, Horoshop or WooCommerce?',
                'Yes. Parsing from any website, 100,000+ SKU in a single pass, full migration in 24 hours.',
            ),
            (
                'Can I pay in instalments?',
                'Yes, up to 15 payments through monobank «Pay in Parts».',
            ),
            (
                'Is the store hard to manage?',
                'We build the admin panel ourselves, in any language you need — English, Ukrainian or another: '
                'a new manager will master it in 15 minutes. Stock and price updates and order processing — in 1–2 clicks.',
            ),
        ],
    },
}

RS = {
    'uk': {
        'title': 'Створити сайт під ключ — розробка сайтів від 150 € | PrometeyLabs',
        'description': (
            'Розробка і створення сайтів під ключ: лендінги 150–300 €, корпоративні 350–500 €, '
            'магазини від 650 €. Ціна і строк у договорі, рік підтримки безкоштовно.'
        ),
        'crumb': 'Розробка сайтів',
        'types_h2': 'Створити сайт для бізнесу: який тип обрати',
        'types': [
            (
                'Лендінг',
                'Одна сторінка під рекламу: офер, форма, швидкий запуск, 150–300 €, 3–7 днів.',
                'corporate',
            ),
            (
                'Корпоративний',
                'Структура компанії, послуги і SEO-основа, 350–500 €, 7–14 днів.',
                'corporate',
            ),
            (
                'Інтернет-магазин',
                'Каталог, оплата, доставка, замовлення в адмінці, від 650 €, 14–21 день.',
                'shop',
            ),
            (
                'Платформа',
                'Кабінети, ролі, інтеграції, 1 500–5 000 €, 14–30 днів.',
                'corporate',
            ),
        ],
        'guarantee_h2': 'Гарантія і підтримка',
        'guarantee': (
            'Пожиттєва гарантія на код і рік безкоштовної підтримки. Включає: виправлення технічних помилок, '
            'підтримку працездатності коду, реакцію на критичні технічні збої, відповідність функціоналу ТЗ. '
            'Не включає: нові функції, оновлення дизайну, інтеграції з новими сервісами.'
        ),
        'faq_h2': 'Часті питання про розробку сайтів',
        'faq': [
            (
                'Скільки коштує створити сайт?',
                'Лендінги 150–300 €, корпоративні 350–500 €, магазини від 650 €, платформи 1 500–5 000 €. Точну суму і строк фіксуємо в договорі.',
            ),
            (
                'Скільки часу займає розробка сайту?',
                'Лендінг 3–7 днів, корпоративний сайт 7–14 днів, інтернет-магазин 14–21 день, платформа 14–30 днів.',
            ),
            (
                'Що входить у вартість?',
                'У сумі: макет, верстка, форма, адаптив (лендінг); структура сторінок, CMS-основа, адаптив, базова SEO (корпоративний); каталог, кошик, оплата/доставка-основа, адмінка замовлень (магазин); узгоджений MVP за брифом у діапазоні (платформа). Не входить: реклама, тексти з нуля, сторонні API, наповнення контентом, наповнення товарів, маркетинг, кастомні інтеграції, нові модулі після здачі, сторонні ліцензії.',
            ),
            (
                'Чи можна оплатити частинами або етапами?',
                'Так, розбиття оплати на етапи — без переплат та прихованих умов. Для магазинів і корпоративних сайтів — до 15 платежів.',
            ),
            (
                'Чи зможу я сам змінювати сайт?',
                'Так, самі. У адміністративній панелі можна змінювати заголовки, тексти, фото й, у магазині, товари, акції та промокоди. Заявки приходять у міні-CRM. Розробник потрібен тоді, коли ви додаєте нову функцію або змінюєте логіку сайту, а не щоб виправити ціну чи замінити картинку.',
            ),
            (
                'Чому не зробити сайт у конструкторі? Це ж швидше.',
                'Для простої візитки — так, часто швидше. Якщо потрібні своя структура, окрема адмінка, оплата, фіди чи нестандартні сценарії, конструктор починає обмежувати. Тоді доопрацювання коштують часу, а частини речей там не зробити взагалі. Для сайту, який має приводити заявки й продажі, вигідніше одразу зробити його під задачу.',
            ),
            (
                'Що буде з сайтом після запуску? Чи не «прив’яжете» ви його до себе?',
                'Сайт ваш: ви отримуєте код і доступ, без обов’язкової щомісячної плати конструктору. Після запуску можна залишитись на супроводі студії — для правок, оновлень і консультацій — або вести контент самостійно. Це не оренда чужої платформи, з якої сайт потім не забрати.',
            ),
            (
                'Яка гарантія?',
                'Пожиттєва гарантія на код і рік безкоштовної підтримки. Включає: виправлення технічних помилок, підтримку працездатності коду, реакцію на критичні технічні збої, відповідність функціоналу ТЗ. Не включає: нові функції, оновлення дизайну, інтеграції з новими сервісами.',
            ),
        ],
    },
    'ru': {
        'title': 'Создать сайт под ключ — разработка сайтов от 150 € | PrometeyLabs',
        'description': (
            'Разработка и создание сайтов под ключ: лендинги 150–300 €, корпоративные 350–500 €, '
            'магазины от 650 €. Цена и срок в договоре, год поддержки бесплатно.'
        ),
        'crumb': 'Разработка сайтов',
        'types_h2': 'Создать сайт для бизнеса: какой тип выбрать',
        'types': [
            (
                'Лендинг',
                'Одна страница под рекламу: офер, форма, быстрый запуск, 150–300 €, 3–7 дней.',
                'corporate',
            ),
            (
                'Корпоративный',
                'Структура компании, услуги и SEO-основа, 350–500 €, 7–14 дней.',
                'corporate',
            ),
            (
                'Интернет-магазин',
                'Каталог, оплата, доставка, заказы в админке, от 650 €, 14–21 день.',
                'shop',
            ),
            (
                'Платформа',
                'Кабинеты, роли, интеграции, 1 500–5 000 €, 14–30 дней.',
                'corporate',
            ),
        ],
        'guarantee_h2': 'Гарантия и поддержка',
        'guarantee': (
            'Пожизненная гарантия на код и год бесплатной поддержки. Включает: исправление технических ошибок, '
            'поддержку работоспособности кода, реакцию на критические технические сбои, соответствие функционала ТЗ. '
            'Не включает: новые функции, обновление дизайна, интеграции с новыми сервисами.'
        ),
        'faq_h2': 'Частые вопросы о разработке сайтов',
        'faq': [
            (
                'Сколько стоит создать сайт?',
                'Лендинги 150–300 €, корпоративные 350–500 €, магазины от 650 €, платформы 1 500–5 000 €. Точную сумму и срок фиксируем в договоре.',
            ),
            (
                'Сколько времени занимает разработка сайта?',
                'Лендинг 3–7 дней, корпоративный сайт 7–14 дней, интернет-магазин 14–21 день, платформа 14–30 дней.',
            ),
            (
                'Что входит в стоимость?',
                'В сумме: макет, вёрстка, форма, адаптив (лендинг); структура страниц, CMS-основа, адаптив, базовое SEO (корпоративный); каталог, корзина, оплата/доставка-основа, админка заказов (магазин); согласованный MVP по брифу в диапазоне (платформа). Не входит: реклама, тексты с нуля, сторонние API, наполнение контентом, наполнение товаров, маркетинг, кастомные интеграции, новые модули после сдачи, сторонние лицензии.',
            ),
            (
                'Можно оплатить частями или этапами?',
                'Да, разбиение оплаты на этапы — без переплат и скрытых условий. Для магазинов и корпоративных сайтов — до 15 платежей.',
            ),
            (
                'Смогу ли я сам менять сайт?',
                'Да, сами. В административной панели можно менять заголовки, тексты, фото и, в магазине, товары, акции и промокоды. Заявки приходят в мини-CRM. Разработчик нужен тогда, когда вы добавляете новую функцию или меняете логику сайта, а не чтобы исправить цену или заменить картинку.',
            ),
            (
                'Почему не сделать сайт в конструкторе? Это же быстрее.',
                'Для простой визитки — да, часто быстрее. Если нужны своя структура, отдельная админка, оплата, фиды или нестандартные сценарии, конструктор начинает ограничивать. Тогда доработки стоят времени, а часть вещей там не сделать вообще. Для сайта, который должен приводить заявки и продажи, выгоднее сразу сделать его под задачу.',
            ),
            (
                'Что будет с сайтом после запуска? Вы не «привяжете» его к себе?',
                'Сайт ваш: вы получаете код и доступ, без обязательной ежемесячной платы конструктору. После запуска можно остаться на сопровождении студии — для правок, обновлений и консультаций — или вести контент самостоятельно. Это не аренда чужой платформы, с которой сайт потом не забрать.',
            ),
            (
                'Какая гарантия?',
                'Пожизненная гарантия на код и год бесплатной поддержки. Включает: исправление технических ошибок, поддержку работоспособности кода, реакцию на критические технические сбои, соответствие функционала ТЗ. Не включает: новые функции, обновление дизайна, интеграции с новыми сервисами.',
            ),
        ],
    },
    'en': {
        'title': 'Turnkey website development in Ukraine | PrometeyLabs',
        'description': (
            'Turnkey websites: landing pages 150–300 €, corporate sites 350–500 €, '
            'online stores from 650 €. Price and deadline are fixed in the contract. '
            'Lifetime code warranty and 1 year of free support.'
        ),
        'crumb': 'Website development',
        'faq_h2': 'Common questions about website development',
        'faq': [
            (
                'How much does it cost to build a website?',
                'Landing pages 150–300 €, corporate sites 350–500 €, online stores from 650 €, platforms 1,500–5,000 €. We fix the exact amount and deadline in the contract.',
            ),
            (
                'How long does website development take?',
                'A landing page takes 3–7 days, a corporate site 7–14 days, an online store 14–21 days, a platform 14–30 days.',
            ),
            (
                'What is included in the price?',
                'In the total: a layout, markup, a form, and a responsive version (landing page); page structure, a CMS base, a responsive version, and basic SEO (corporate site); a catalog, a cart, a payment and delivery base, and an order admin panel (store); an agreed MVP from the brief within the range (platform). Not included: advertising, copy written from scratch, third-party APIs, filling in content, filling in products, marketing, custom integrations, new modules after delivery, third-party licenses.',
            ),
            (
                'Can I pay in parts or by stages?',
                'Yes. Payment is split into stages, with no overpayment and no hidden terms. For stores and corporate sites — up to 15 payments.',
            ),
            (
                'Will I be able to change the site myself?',
                'Yes. In the admin panel you can change headlines, texts, and photos and, in a store, products, promotions, and promo codes. Inquiries arrive in a mini-CRM. A developer is needed when you add a new function or change the site logic, not to fix a price or replace a picture.',
            ),
            (
                'Why not build the site in a website builder? Isn’t that faster?',
                'For a simple calling card, yes, it is often faster. If you need your own structure, a separate admin panel, payment, feeds, or unusual scenarios, a website builder starts to limit you. Rework then costs time, and some things cannot be done there at all. For a site that should bring inquiries and sales, it is better to build it for the task from the start.',
            ),
            (
                'What happens to the site after launch? Will you lock it to yourselves?',
                'The site is yours: you receive the code and access, with no required monthly fee to a website builder. After launch you can stay on studio support — for edits, updates, and consultations — or manage the content yourself. This is not a rental of someone else’s platform that you cannot take the site away from.',
            ),
            (
                'What is the warranty?',
                'Lifetime code warranty and 1 year of free support. It includes fixing technical errors, keeping the code working, a response to critical technical failures, and matching the specification. It does not include new functions, design updates, or integrations with new services.',
            ),
        ],
    },
}


def lang():
    code = (translation.get_language() or 'uk').split('-')[0]
    return code if code in ('uk', 'ru', 'en') else 'uk'


def for_lang(mapping):
    """Return mapping[lang], or uk when this dict has no entry for the language."""
    code = lang()
    if code in mapping:
        return mapping[code]
    return mapping['uk']


def faq_pairs(items):
    return [{'q': q, 'a': a} for q, a in items]


def shop_copy():
    return for_lang(SHOP)


def rs_copy():
    return for_lang(RS)


def contacts_copy():
    return for_lang(CONTACTS)


def crumbs_copy():
    return for_lang(CRUMBS)


def process_site_copy():
    return for_lang(PROCESS_SITE)
