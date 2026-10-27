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
    'shop': {
        'target': '#zayavka',
        'uk': {
            'label': 'Розрахувати вартість магазину',
            'sticky': 'Розрахувати ціну магазину',
            'micro': '4 питання · 1 хвилина · підберемо пакет від 800 €',
        },
        'ru': {
            'label': 'Рассчитать стоимость магазина',
            'sticky': 'Рассчитать цену магазина',
            'micro': '4 вопроса · 1 минута · подберём пакет от 800 €',
        },
    },
    'corp': {
        'target': '#calculator',
        'uk': {
            'label': 'Розрахувати вартість сайту',
            'micro': '5 питань · 2 хвилини · підберемо пакет під ваш бізнес',
        },
        'ru': {
            'label': 'Рассчитать стоимость сайта',
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
