"""SSOT: головна помаранчева кнопка-квіз «Розрахувати…» на рекламних посадкових.

Одна дія на першому екрані (ads_page_structure_skill rule 2–3), текст = дія з
оголошення + об'єкт (ads_page_copy_skill: «Дієслово + результат»), мікротекст =
що буде після натиску (кроки, час, результат). Тільки правда про квіз:
ніде не обіцяємо «ціну одразу» чи «без дзвінка» — телефон квіз просить у кінці.

target:
  * '#…'        — квіз на цій самій сторінці (shop-v2 #zayavka, corp-v2 #calculator);
  * 'calculator' — сторінка /calculator/ (та /ru/calculator/) з автостартом тесту.
"""

CALC_CTA = {
    'home': {
        'target': 'calculator',
        'uk': {
            'label': 'Розрахувати вартість сайту',
            'micro': '5 питань · 2 хвилини · безкоштовно, без зобов’язань',
        },
        'ru': {
            'label': 'Рассчитать стоимость сайта',
            'micro': '5 вопросов · 2 минуты · бесплатно, без обязательств',
        },
    },
    # ТЗ 27.10.2026: тест вбудовано на сторінку (#pl-rs-calc); sticky — і на десктопі,
    # без стрілки, з власною подією sticky_cta_click (не конверсія).
    'rozrobka': {
        'target': '#pl-rs-calc',
        'sticky_desktop': True,
        'sticky_arrow': False,
        'sticky_event': 'sticky_cta_click',
        'uk': {
            'label': 'Розрахувати вартість онлайн',
            'sticky': 'Розрахуйте вартість онлайн',
            'micro': '5 питань · 2 хвилини · безкоштовно, без зобов’язань',
        },
        'ru': {
            'label': 'Рассчитать стоимость онлайн',
            'sticky': 'Рассчитайте стоимость онлайн',
            'micro': '5 вопросов · 2 минуты · бесплатно, без обязательств',
        },
    },
    # ТЗ 27.10.2026 (shop-v2) п. 4.2 / 4.16 / 4.17: тест перенесено на 3-тє місце (#zayavka);
    # sticky — і на десктопі, без стрілки, sticky_cta_click (як на /rozrobka-sajtiv/).
    'shop': {
        'target': '#zayavka',
        'sticky_desktop': True,
        'sticky_arrow': False,
        'sticky_event': 'sticky_cta_click',
        'uk': {
            'label': 'Розрахувати вартість магазину',
            'sticky': 'Розрахуйте вартість онлайн',
            'micro': 'Пройдіть тест за 1 хвилину',
        },
        'ru': {
            'label': 'Рассчитать стоимость магазина',
            'sticky': 'Рассчитайте стоимость онлайн',
            'micro': 'Пройдите тест за 1 минуту',
        },
    },
    # ТЗ Софії 28.10.2026 п. 3.1: sticky і на десктопі, текст як на /rozrobka-sajtiv/;
    # ціль/data-calc-cta/data-calc-page без змін, подію (data-calc-event) не додаємо.
    'corp': {
        'target': '#calculator',
        'sticky_desktop': True,
        'sticky_arrow': False,
        'uk': {
            'label': 'Розрахувати вартість сайту',
            'sticky': 'Розрахуйте вартість онлайн',
            'micro': '5 питань · 2 хвилини · підберемо пакет під ваш бізнес',
        },
        'ru': {
            'label': 'Рассчитать стоимость сайта',
            'sticky': 'Рассчитайте стоимость онлайн',
            'micro': '5 вопросов · 2 минуты · подберём пакет под ваш бизнес',
        },
    },
    'dorobka': {
        'target': 'calculator',
        'uk': {
            'label': 'Розрахувати вартість робіт',
            'micro': '5 питань · 2 хвилини · безкоштовно, без зобов’язань',
        },
        'ru': {
            'label': 'Рассчитать стоимость работ',
            'micro': '5 вопросов · 2 минуты · бесплатно, без обязательств',
        },
    },
}

CALC_START_QUERY = '?start=1'


def calc_cta_copy(page, lang):
    """Return {'label', 'sticky', 'micro', 'target', 'sticky_*'} for page × lang (uk fallback)."""
    entry = CALC_CTA[page]
    lang = 'ru' if (lang or '').startswith('ru') else 'uk'
    data = dict(entry[lang])
    data['target'] = entry['target']
    # sticky options (shared component): defaults = mobile-only bar with arrow, cta_calc_click
    data['sticky_desktop'] = entry.get('sticky_desktop', False)
    data['sticky_arrow'] = entry.get('sticky_arrow', True)
    data['sticky_event'] = entry.get('sticky_event', '')
    # коротший текст для мобільного sticky (кнопка ~290px поруч із FAB) — без «…»
    data.setdefault('sticky', data['label'])
    return data
