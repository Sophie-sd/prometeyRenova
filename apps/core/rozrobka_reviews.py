"""Six Google review bodies on /rozrobka-sajtiv/. Names stay in the template."""
from django.utils import translation

_BODIES = {
    'uk': (
        'Робили повний редизайн та перенесення нашого старого сайту запчастин для авто, який постійно ламався і гальмував. PrometeyLabs повністю оновили код, прискорили завантаження і налаштували зручні фільтри за марками машин. Продажі помітно зросли, бо тепер покупці тепер не виходять із сайту через довге очікування.',
        'Замовляв у PrometeyLabs корпоративний сайт для компанії по монтажу сонячних панелей. Команда чудово розібралася в специфіці, запропонувала зручну структуру з калькулятором потужності та розрахунком економії. Загалом, сайт дуже інформативний і зрозумілий.',
        'Ця компанія нам робила сайт під ключ для нашої невеликої домашньої пекарні. Адмінка дуже проста, навіть я зі своїм мінімальним досвідом можу сам оновлювати меню та акції. Замовлення клієнтів тепер теж краще видно, не губляться.',
        'Переносили старий сайт на нову платформу через проблеми з безпекою. Команда PrometeyLabs виконала все акуратно. Головне, що позиції в пошуку не просіли, а швидкість завантаження помітно виросла.',
        'Дуже вдячні за швидкість виконання! Запускали доставку квітів, терміни горіли, а ребята з Прометею встигли зробити буквально за день дедлайну! Молодці.',
        'Усе чітко за договором, ціна як і домовлялися. Роботу здали навіть на кілька днів раніше обіцяного терміну.',
    ),
    'ru': (
        'Делали полный редизайн и перенос нашего старого сайта запчастей для авто, который постоянно ломался и тормозил. PrometeyLabs полностью обновили код, ускорили загрузку и настроили удобные фильтры по маркам машин. Продажи заметно выросли, потому что покупатели больше не уходят с сайта из-за долгого ожидания.',
        'Заказывал в PrometeyLabs корпоративный сайт для компании по монтажу солнечных панелей. Команда отлично разобралась в специфике и предложила удобную структуру с калькулятором мощности и расчётом экономии. В целом сайт очень информативный и понятный.',
        'Эта компания делала нам сайт под ключ для небольшой домашней пекарни. Админка очень простая: даже я с минимальным опытом могу сам обновлять меню и акции. Заказы клиентов теперь тоже лучше видно, они не теряются.',
        'Переносили старый сайт на новую платформу из-за проблем с безопасностью. Команда PrometeyLabs сделала всё аккуратно. Главное, что позиции в поиске не просели, а скорость загрузки заметно выросла.',
        'Очень благодарны за скорость! Запускали доставку цветов, сроки горели, а ребята из Прометея успели сделать буквально в день дедлайна. Молодцы.',
        'Всё чётко по договору, цена как и договаривались. Работу сдали даже на несколько дней раньше обещанного срока.',
    ),
    'en': (
        'They did a full redesign and moved our old auto-parts site, which kept breaking and running slowly. PrometeyLabs rewrote the code, sped up loading, and set up convenient filters by car brand. Sales grew noticeably, because buyers no longer leave the site while waiting.',
        'I ordered a corporate website from PrometeyLabs for a solar-panel installation company. The team understood the specifics and proposed a clear structure with a capacity calculator and a savings estimate. Overall, the site is informative and easy to follow.',
        'This company built a turnkey site for our small home bakery. The admin panel is very simple: even with minimal experience I can update the menu and promotions myself. Customer orders are easier to see now and do not get lost.',
        'We moved the old site to a new platform because of security problems. The PrometeyLabs team did it carefully. Search positions did not drop, and loading speed grew noticeably.',
        'Thank you for the speed. We were launching flower delivery, the deadline was tight, and the Prometey team finished on the day of the deadline. Well done.',
        'Everything matched the contract, and the price was as agreed. They delivered the work a few days before the promised date.',
    ),
}


def rozrobka_review_bodies():
    """Six paragraphs for the active language. ru/en are never filled from Ukrainian."""
    code = (translation.get_language() or 'uk').split('-')[0]
    if code not in _BODIES:
        code = 'uk'
    return _BODIES[code]
