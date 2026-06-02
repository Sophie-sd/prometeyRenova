"""Початкові дані портфоліо для seed_portfolio_projects."""

PORTFOLIO_PROJECTS = [
    {
        'slug': 'speakup',
        'title': 'SPEAK UP',
        'subtitle': 'EDUCATIONAL PLATFORM',
        'card_description': (
            "Корпоративний сайт, інтерактивна онлайн-платформа для вивчення англійської мови, "
            "що об'єднує студентів та викладачів в єдину екосистему. Автоматизація навчального "
            "процесу, від тестування рівня знань до отримання сертифікату."
        ),
        'integrations': (
            "інтеграція платіжних систем\n"
            "мультимовність\n"
            "LMS-система\n"
            "особистий кабінет студента"
        ),
        'card_image_alt': 'Speak Up - Educational Platform',
        'home_story_label': 'SpeakUp',
        'order': 0,
        'home_order': 1,
        'show_on_portfolio': True,
        'show_on_homepage': True,
        'static_card': 'images/portfolio_page/speakup.png',
        'static_card_mobile': 'images/portfolio_page/speakup_card_mb.png',
        'static_home': 'images/portfolio/speakup.png',
        'static_modal_hero': 'images/portfolio_page/speakup_desc.png',
        'static_modal_mobile': 'images/portfolio_page/speakup_mb.png',
        'static_modal_tablet': 'images/portfolio_page/speakup_tab.png',
        'static_modal_laptop': 'images/portfolio_page/speakup_lap.png',
        'modal_content': (
            '<p class="portfolio-modal-text">Масштабна освітня платформа (LMS) з адаптивним '
            'інтерфейсом та особистими кабінетами для різних ролей: студент, викладач, '
            'адміністратор. Рішення забезпечує повний цикл навчання: онлайн-уроки, '
            'інтерактивні домашні завдання, трекінг успішності та автоматизовану систему '
            'оцінювання.</p>'
            '<p class="portfolio-modal-integrations-title">ІНТЕГРАЦІЇ:</p>'
            '<ul class="portfolio-modal-integrations-list">'
            '<li>безпечні онлайн-платежі та рекурентні списання (підписки)</li>'
            '<li>інтерактивний календар та букінг занять</li>'
            '<li>система сповіщень (e-mail/push) про уроки</li>'
            '<li>модуль відеозв\'язку для проведення занять</li>'
            '</ul>'
            '<p class="portfolio-modal-text">Платформа включає потужну адміністративну панель, '
            'реалізовану як універсальний інструмент для керування розкладом, базою студентів, '
            'фінансовою звітністю та контентом курсів без необхідності залучення розробників.</p>'
            '<p class="portfolio-modal-text">Підтримує мультимовність інтерфейсу та автоматичну '
            'конвертацію валют, що дозволяє працювати на міжнародних ринках. Система побудована '
            'на модульній архітектурі, що гарантує високу швидкість роботи при великих '
            'навантаженнях та можливість легкого додавання нових навчальних інструментів або '
            'мовних курсів без зміни ядра.</p>'
        ),
    },
    {
        'slug': 'coresync',
        'title': 'CoreSync',
        'subtitle': 'AI Spa & Wellness',
        'card_description': (
            'Корпоративний сайт і мобільний застосунок із повністю ШІ-керованим сервісом: '
            'онлайн-бронювання, iOS/Android застосунок і планшетна панель для персоналу.'
        ),
        'integrations': (
            'центральний AI-агент\n'
            'AI-кол-центр\n'
            'AI-бронювання\n'
            'внутрішня CRM'
        ),
        'card_image_alt': 'CoreSync - AI Spa & Wellness Platform',
        'home_story_label': 'Coresync',
        'order': 1,
        'home_order': 0,
        'show_on_portfolio': True,
        'show_on_homepage': True,
        'static_card': 'images/portfolio_page/coresync.png',
        'static_card_mobile': 'images/portfolio_page/coresync_card_mb.png',
        'static_home': 'images/portfolio/coresync.png',
        'static_modal_hero': 'images/portfolio_page/coresync_desc.png',
        'static_modal_mobile': 'images/portfolio_page/coresync_mob.png',
        'static_modal_tablet': 'images/portfolio_page/coresync_tab.png',
        'static_modal_laptop': 'images/portfolio_page/coresync_lap.png',
        'modal_content': (
            '<p class="portfolio-modal-text">Корпоративний сайт та мобільний застосунок із '
            'повністю ШІ-керованим сервісом: онлайн-бронюванням, застосунками для iOS/Android '
            'і планшетною панеллю персоналу. Платформа автоматизує роботу салону та забезпечує '
            'клієнтську підтримку 24/7.</p>'
            '<p class="portfolio-modal-integrations-title">Інтеграції:</p>'
            '<ul class="portfolio-modal-integrations-list">'
            '<li>центральний AI-агент</li>'
            '<li>AI-кол-центр (голос/текст)</li>'
            '<li>AI-бронювання за типами послуг</li>'
            '<li>AI-контроль атмосфери (світло, температура, музика)</li>'
            '<li>внутрішня CRM</li>'
            '</ul>'
            '<p class="portfolio-modal-text">Рішення об\'єднує сайт, мобільні застосунки та '
            'робочу систему персоналу в єдину екосистему.</p>'
            '<p class="portfolio-modal-text">AI-агенти забезпечують швидке обслуговування, '
            'точну комунікацію та автоматизацію всіх операцій — від дзвінків до push-сповіщень. '
            'Платформа адаптована під мобільні, планшетні й десктопні пристрої та містить '
            'аналітику для управління завантаженістю й оптимізацією процесів.</p>'
        ),
    },
    {
        'slug': 'playvision',
        'title': 'PlayVision',
        'subtitle': 'PWA',
        'card_description': (
            'Футбольна освітня платформа з PWA-додатком і особистими кабінетами для гравців, '
            'тренерів та батьків, включно із системою курсів та івентів.'
        ),
        'integrations': (
            'персональний AI-помічник\n'
            'CRM оплат і підписок\n'
            'аналітика\n'
            'e-mail/SMS-сповіщення'
        ),
        'card_image_alt': 'PlayVision - футбольна освітня платформа',
        'home_story_label': 'Play Vision',
        'order': 2,
        'home_order': 2,
        'show_on_portfolio': True,
        'show_on_homepage': True,
        'static_card': 'images/portfolio_page/play_vision.png',
        'static_card_mobile': 'images/portfolio_page/play_vision_card_mb.png',
        'static_home': 'images/portfolio/playvision.png',
        'static_modal_hero': 'images/portfolio_page/play_vision_desc.png',
        'static_modal_mobile': 'images/portfolio_page/play_vision_mb.png',
        'static_modal_tablet': 'images/portfolio_page/play_vision_tab.png',
        'static_modal_laptop': 'images/portfolio_page/play_vision_lap.png',
        'modal_content': (
            '<p class="portfolio-modal-text">Футбольна освітня платформа з PWA-додатком і '
            'особистими кабінетами для гравців, тренерів та батьків. Рішення охоплює курси, '
            'івенти, контент та інструменти для комплексного розвитку у футбольній індустрії.</p>'
            '<p class="portfolio-modal-integrations-title">Інтеграції:</p>'
            '<ul class="portfolio-modal-integrations-list">'
            '<li>персональний AI-помічник</li>'
            '<li>CRM оплати та підписок</li>'
            '<li>аналітика прогресу</li>'
            '<li>e-mail/SMS-сповіщення</li>'
            '</ul>'
            '<p class="portfolio-modal-text">Платформа включає веб-додаток і мобільну версію, '
            'реалізована як універсальний конструктор для управління контентом, структурою '
            'сторінок, курсами та івентами без участі розробників.</p>'
            '<p class="portfolio-modal-text">Підтримує темну/світлу теми, адаптивну навігацію '
            'та ролі з тарифами, що формують гнучкий доступ для різних категорій користувачів.</p>'
        ),
    },
    {
        'slug': 'beautyshop',
        'title': 'BEAUTYSHOP',
        'subtitle': 'ОНЛАЙН-МАГАЗИН КОСМЕТИКИ',
        'card_description': (
            'Онлайн-магазин косметики з власною CRM, особистим кабінетом клієнта та гнучкою '
            'системою цін, промокодів і акцій.'
        ),
        'integrations': (
            'онлайн-оплати\n'
            'промокоди та акції\n'
            'аналітика замовлень\n'
            'e-mail/SMS-нотифікації'
        ),
        'card_image_alt': 'BeautyShop - онлайн-магазин косметики',
        'home_story_label': 'BeautyShop',
        'order': 3,
        'home_order': 3,
        'show_on_portfolio': True,
        'show_on_homepage': True,
        'static_card': 'images/portfolio_page/beauty_shop.png',
        'static_card_mobile': 'images/portfolio_page/beauty_shop_card_mb.png',
        'static_home': 'images/portfolio/beautyshop.png',
        'static_modal_hero': 'images/portfolio_page/beauty_shop_desc.png',
        'static_modal_mobile': 'images/portfolio_page/beauty_shop_mb.png',
        'static_modal_tablet': 'images/portfolio_page/beauty_shop_tab.png',
        'static_modal_laptop': 'images/portfolio_page/beauty_shop_lap.png',
        'modal_content': (
            '<p class="portfolio-modal-text">E-commerce платформа з CRM, особистим кабінетом '
            'та гнучкими механіками цін, промокодів та акцій. Рішення створене для '
            'персоналізованого досвіду покупки та автоматизації роботи адміністратора.</p>'
            '<p class="portfolio-modal-integrations-title">Інтеграції:</p>'
            '<ul class="portfolio-modal-integrations-list">'
            '<li>онлайн-оплати</li>'
            '<li>промокоди та акційні правила</li>'
            '<li>аналітика замовлень і поведінки</li>'
            '<li>e-mail/SMS-нотифікації</li>'
            '</ul>'
            '<p class="portfolio-modal-text">Система поєднує магазин і CRM-адмінку для '
            'керування товарами, категоріями, залишками й замовленнями.</p>'
            '<p class="portfolio-modal-text">Платформа підтримує сегментацію користувачів, '
            'персональні рекомендації та різні цінові групи, що підвищує конверсію.</p>'
        ),
    },
    {
        'slug': 'redrabbit',
        'title': 'REDRABBIT',
        'subtitle': 'E-COMMERCE 18+',
        'card_description': (
            'Інтернет-магазин із 18+ age-gate, розширеною адмін-панеллю та CRM-аналітикою.'
        ),
        'integrations': (
            'платіжна система\n'
            'промокоди та акції\n'
            'CRM-аналітика\n'
            'автооновлюваний каталог товарів'
        ),
        'card_image_alt': 'RedRabbit - e-commerce 18+',
        'home_story_label': 'RedRabbit',
        'order': 4,
        'home_order': 5,
        'show_on_portfolio': True,
        'show_on_homepage': True,
        'static_card': 'images/portfolio_page/redrabbit.png',
        'static_card_mobile': 'images/portfolio_page/redrabbit_card_mb.png',
        'static_home': 'images/portfolio/redrabbit.png',
        'static_modal_hero': 'images/portfolio_page/redrabbit_desc.png',
        'static_modal_mobile': 'images/portfolio_page/redrabbit_mb.png',
        'static_modal_tablet': 'images/portfolio_page/redrabbit_tab.png',
        'static_modal_laptop': 'images/portfolio_page/redrabbit_lap.png',
        'modal_content': (
            '<p class="portfolio-modal-text">Інтернет-магазин із 18+ age-gate, розширеною '
            'адмін-панеллю та CRM-аналітикою. Платформа розроблена для великих товарних обсягів, '
            'категорій і різних акційних моделей.</p>'
            '<p class="portfolio-modal-integrations-title">Інтеграції:</p>'
            '<ul class="portfolio-modal-integrations-list">'
            '<li>платіжна система</li>'
            '<li>промокоди та акційні сценарії</li>'
            '<li>CRM-аналітика</li>'
            '<li>автоматичні нотифікації</li>'
            '<li>автооновлюваний каталог товарів (синхронізація кожні 2 години)</li>'
            '</ul>'
            '<p class="portfolio-modal-text">Платформа включає сайт із захищеним доступом, '
            'рольову систему та інструменти управління товарами, замовленнями й маркетингом.</p>'
            '<p class="portfolio-modal-text">Age-gate забезпечує відповідність 18+ та захист '
            'контенту. Система надає деталізовану статистику акцій, конверсій та поведінки '
            'користувачів.</p>'
        ),
    },
    {
        'slug': 'sunpannel',
        'title': 'SUNPANNEL',
        'subtitle': 'СОНЯЧНІ ПАНЕЛІ ТА ЕНЕРГОРІШЕННЯ',
        'card_description': (
            'Корпоративний сайт і інтернет-магазин із технічним каталогом, що автоматично '
            'оновлюється.'
        ),
        'integrations': (
            'автооновлення каталогу\n'
            'онлайн-оплати та рахунки\n'
            'заявка на комерційну пропозицію\n'
            'e-mail менеджерам'
        ),
        'card_image_alt': 'SunPannel - сонячні панелі та енергорішення',
        'home_story_label': 'SunPannel',
        'order': 5,
        'home_order': 99,
        'show_on_portfolio': True,
        'show_on_homepage': False,
        'static_card': 'images/portfolio_page/greensolar.png',
        'static_card_mobile': 'images/portfolio_page/greensolar_card_mb.png',
        'static_home': '',
        'static_modal_hero': 'images/portfolio_page/greensolar_desc.png',
        'static_modal_mobile': 'images/portfolio_page/greensolar_mb.png',
        'static_modal_tablet': 'images/portfolio_page/greensolar_tab.png',
        'static_modal_laptop': 'images/portfolio_page/greensolar_lap.png',
        'modal_content': (
            '<p class="portfolio-modal-text">Корпоративний сайт і інтернет-магазин з '
            'технічним каталогом, що автоматично оновлюється. Рішення призначене для продажу '
            'сонячних комплектів, панелей, інверторів та енергосистем.</p>'
            '<p class="portfolio-modal-integrations-title">Інтеграції:</p>'
            '<ul class="portfolio-modal-integrations-list">'
            '<li>автооновлення каталогу</li>'
            '<li>онлайн-оплати та рахунки</li>'
            '<li>заявка на комерційну пропозицію</li>'
            '<li>e-mail менеджерам</li>'
            '<li>керування контентом, товарами та маркетинговими сторінками</li>'
            '</ul>'
            '<p class="portfolio-modal-text">Платформа поєднує маркетингові сторінки, каталог, '
            'фільтри й кошик у єдину систему.</p>'
            '<p class="portfolio-modal-text">Технічні фільтри дозволяють зібрати комплект за '
            'параметрами (потужність, інвертор, кількість панелей).</p>'
        ),
    },
    {
        'slug': 'adiabatic',
        'title': 'Adiabatic',
        'subtitle': '',
        'card_description': 'Корпоративний веб-проєкт PrometeyLabs.',
        'integrations': '',
        'card_image_alt': 'Adiabatic',
        'home_story_label': 'Adiabatic',
        'order': 99,
        'home_order': 4,
        'show_on_portfolio': False,
        'show_on_homepage': True,
        'static_card': 'images/portfolio/adiabatic.png',
        'static_card_mobile': '',
        'static_home': 'images/portfolio/adiabatic.png',
        'static_modal_hero': '',
        'static_modal_mobile': '',
        'static_modal_tablet': '',
        'static_modal_laptop': '',
        'modal_content': '',
    },
    {
        'slug': 'polygraph',
        'title': 'Polygraph',
        'subtitle': '',
        'card_description': 'Корпоративний веб-проєкт PrometeyLabs.',
        'integrations': '',
        'card_image_alt': 'Polygraph',
        'home_story_label': 'Polygraph',
        'order': 99,
        'home_order': 6,
        'show_on_portfolio': False,
        'show_on_homepage': True,
        'static_card': 'images/portfolio/polygraph.png',
        'static_card_mobile': '',
        'static_home': 'images/portfolio/polygraph.png',
        'static_modal_hero': '',
        'static_modal_mobile': '',
        'static_modal_tablet': '',
        'static_modal_laptop': '',
        'modal_content': '',
    },
    {
        'slug': 'pulvas-store',
        'title': 'Pulvas Store',
        'subtitle': '',
        'card_description': 'Корпоративний веб-проєкт PrometeyLabs.',
        'integrations': '',
        'card_image_alt': 'Pulvas Store',
        'home_story_label': 'Pulvas Store',
        'order': 99,
        'home_order': 7,
        'show_on_portfolio': False,
        'show_on_homepage': True,
        'static_card': 'images/portfolio/pulvas_store.png',
        'static_card_mobile': '',
        'static_home': 'images/portfolio/pulvas_store.png',
        'static_modal_hero': '',
        'static_modal_mobile': '',
        'static_modal_tablet': '',
        'static_modal_laptop': '',
        'modal_content': '',
    },
    {
        'slug': 'airinua',
        'title': 'Airinua',
        'subtitle': '',
        'card_description': 'Корпоративний веб-проєкт PrometeyLabs.',
        'integrations': '',
        'card_image_alt': 'Airinua',
        'home_story_label': 'Airinua',
        'order': 99,
        'home_order': 8,
        'show_on_portfolio': False,
        'show_on_homepage': True,
        'static_card': 'images/portfolio/airinua.png',
        'static_card_mobile': '',
        'static_home': 'images/portfolio/airinua.png',
        'static_modal_hero': '',
        'static_modal_mobile': '',
        'static_modal_tablet': '',
        'static_modal_laptop': '',
        'modal_content': '',
    },
]

IMAGE_FIELD_MAP = (
    ('static_card', 'card_image'),
    ('static_card_mobile', 'card_image_mobile'),
    ('static_home', 'home_story_image'),
    ('static_modal_hero', 'modal_hero'),
    ('static_modal_mobile', 'modal_mobile'),
    ('static_modal_tablet', 'modal_tablet'),
    ('static_modal_laptop', 'modal_laptop'),
)
