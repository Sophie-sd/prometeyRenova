"""Central SEO registry: canonical, hreflang, robots, sitemap languages, meta overrides.

One source of truth, rendered once in ``templates/components/seo_head.html``
(included by ``base.html``) and reused by ``apps.core.sitemaps``.

Rules
-----
* Canonical is always self, absolute, on ``SITE`` and without query params
  (exception: ``/blog/?page=N`` keeps ``?page=N`` for N > 1).
* hreflang is emitted only on indexable language versions and lists only
  languages that have a real translation (``PAGE_LANGUAGES``); x-default = uk.
* A registered page opened in a language without a real translation renders
  ``noindex, follow``, gets no hreflang and is left out of the sitemap.
"""
from __future__ import annotations

import datetime

from django.urls import NoReverseMatch, reverse
from django.utils import translation

SITE = 'https://www.prometeylabs.com'
ORGANIZATION_ID = SITE + '/#organization'
X_DEFAULT_LANG = 'uk'
ALL_LANGS = ('uk', 'ru', 'en')

# url name → languages with a real (translated) version.
PAGE_LANGUAGES: dict[str, tuple[str, ...]] = {
    'home': ALL_LANGS,
    'portfolio': ALL_LANGS,
    'calculator': ALL_LANGS,
    'contacts': ALL_LANGS,
    'blog:blog_list': ALL_LANGS,
    'telegram_bot': ALL_LANGS,
    'corporate_website_v2': ALL_LANGS,
    'tz_generator': ALL_LANGS,
    'offer': ALL_LANGS,
    'privacy': ALL_LANGS,
    'cookies': ALL_LANGS,
    'refund': ALL_LANGS,
    'intellectual_property': ALL_LANGS,
    # RU copy of the monobank page is the untranslated UA text.
    'monobank_chastynamy': ('uk', 'en'),
    # EN copies of these landings are untranslated (UA text) → noindex.
    'internet_shop_v2': ('uk', 'ru'),
    'rozrobka_sajtiv': ('uk', 'ru'),
    'dorobka_sajtu': ('uk', 'ru'),
}

BLOG_DETAIL = 'blog:blog_detail'
BLOG_LIST = 'blog:blog_list'

# Date the static pages' content was last reviewed (sitemap <lastmod>).
STATIC_LASTMOD = datetime.date(2026, 11, 3)

# (url name, lang) → (title, description). None keeps the template value.
# Titles 50–60 chars, keyword first; descriptions 150–160 chars (tests enforce).
META_OVERRIDES: dict[tuple[str, str], tuple[str | None, str | None]] = {
    ('home', 'uk'): (
        'Розробка сайтів під ключ і Telegram-ботів | PrometeyLabs',
        'Сайти під ключ: лендінги, корпоративні сайти, магазини та Telegram-боти. '
        'Ціна і строк у договорі, пожиттєва гарантія на код і 1 рік безкоштовної підтримки.',
    ),
    ('home', 'ru'): (
        'Разработка сайтов под ключ и Telegram-ботов | PrometeyLabs',
        'Сайты под ключ: лендинги, корпоративные сайты, магазины и Telegram-боты. '
        'Цена и срок в договоре, пожизненная гарантия на код и 1 год бесплатной поддержки.',
    ),
    ('home', 'en'): (
        'Turnkey Website Development & Telegram Bots | PrometeyLabs',
        'Turnkey websites: landing pages, corporate sites, online stores and Telegram bots. '
        'Fixed price and deadline, lifetime code warranty and 1 year of free support.',
    ),
    ('internet_shop_v2', 'uk'): ('Інтернет-магазин під ключ від 650 € — запуск за 3 тижні', None),
    ('internet_shop_v2', 'ru'): ('Интернет-магазин под ключ от 650 € — запуск за 3 недели', None),
    ('corporate_website_v2', 'uk'): (
        'Корпоративний сайт під ключ від 350 €, лендінг від 150 €',
        'Корпоративні сайти та лендінги під ключ: лендінг 150–300 € за 3–7 днів, сайт 350–500 € '
        'за 7–14 днів. Пожиттєва гарантія на код і 1 рік безкоштовної підтримки.',
    ),
    ('corporate_website_v2', 'ru'): (
        'Корпоративный сайт под ключ от 350 €, лендинг от 150 €',
        'Корпоративные сайты и лендинги под ключ: лендинг 150–300 € за 3–7 дней, сайт 350–500 € '
        'за 7–14 дней. Пожизненная гарантия на код и 1 год бесплатной поддержки.',
    ),
    ('corporate_website_v2', 'en'): (
        'Turnkey Corporate Website & Landing Pages | PrometeyLabs',
        'Turnkey corporate websites and landing pages: landing €150–300 in 3–7 days, website '
        '€350–500 in 7–14 days. Lifetime code warranty and 1 year of free support.',
    ),
    ('telegram_bot', 'uk'): (
        'Розробка Telegram-бота під ключ для бізнесу | PrometeyLabs',
        'Розробка Telegram-бота під ключ: заявки, онлайн-запис, CRM та оплата в чаті. '
        'Індивідуальний кошторис після брифу, запуск від 7 днів, підтримка після релізу.',
    ),
    ('telegram_bot', 'ru'): (
        'Разработка Telegram-бота под ключ для бизнеса | PrometeyLabs',
        'Разработка Telegram-бота под ключ: заявки, онлайн-запись, CRM и оплата в чате. '
        'Индивидуальная смета после брифа, запуск от 7 дней, поддержка после релиза.',
    ),
    ('telegram_bot', 'en'): (
        'Telegram Bot Development for Business | PrometeyLabs',
        'Turnkey Telegram bot development: lead capture, online booking, CRM integration and '
        'in-chat payments. Individual quote after a brief, support after launch.',
    ),
    ('rozrobka_sajtiv', 'uk'): ('Розробка сайтів під ключ від 150 € — створення сайту', None),
    ('rozrobka_sajtiv', 'ru'): ('Разработка сайтов под ключ от 150 € — создание сайта', None),
    ('dorobka_sajtu', 'uk'): ('Доопрацювання сайту: редизайн і прискорення | PrometeyLabs', None),
    ('dorobka_sajtu', 'ru'): ('Доработка сайта: редизайн, ускорение, перенос | PrometeyLabs', None),
    ('portfolio', 'uk'): (
        'Портфоліо PrometeyLabs: сайти під ключ для бізнесу',
        'Портфоліо PrometeyLabs: корпоративні сайти, лендінги та інтернет-магазини під ключ для '
        'бізнесу з України та Європи. Реальні кейси, дизайн і результати проєктів.',
    ),
    ('portfolio', 'ru'): (
        'Портфолио PrometeyLabs: сайты под ключ для бизнеса',
        'Портфолио PrometeyLabs: корпоративные сайты, лендинги и интернет-магазины под ключ для '
        'бизнеса из Украины и Европы. Реальные кейсы, дизайн и результаты работ.',
    ),
    ('portfolio', 'en'): (
        'PrometeyLabs Portfolio: Turnkey Websites for Business',
        'PrometeyLabs portfolio: turnkey corporate websites, landing pages and online stores for '
        'businesses in Ukraine and Europe. Real case studies, design and results.',
    ),
    ('contacts', 'uk'): ('Контакти PrometeyLabs — замовити розробку сайту в Києві', None),
    ('contacts', 'ru'): ('Контакты PrometeyLabs — заказать разработку сайта в Киеве', None),
    ('contacts', 'en'): ('Contact PrometeyLabs — Order Website Development in Kyiv', None),
    ('blog:blog_list', 'uk'): (
        'Блог про розробку сайтів, SEO і Telegram-боти — PrometeyLabs',
        'Блог PrometeyLabs: практичні статті про розробку сайтів під ключ, SEO, інтернет-магазини, '
        'Telegram-ботів і AI для бізнесу. Реальні кейси, ціни та поради.',
    ),
    ('blog:blog_list', 'ru'): (
        'Блог: разработка сайтов, SEO и Telegram-боты — PrometeyLabs',
        'Блог PrometeyLabs: практические статьи о разработке сайтов под ключ, SEO, '
        'интернет-магазинах, Telegram-ботах и AI для бизнеса. Реальные кейсы, цены и советы.',
    ),
    ('blog:blog_list', 'en'): (
        'Blog: Web Development, SEO & Telegram Bots | PrometeyLabs',
        'PrometeyLabs blog: practical articles on turnkey website development, SEO, online stores, '
        'Telegram bots and AI for business. Real case studies, prices and tips.',
    ),
    ('monobank_chastynamy', 'uk'): (
        None,
        'Оплата розробки сайту частинами через monobank | Universal Bank: умови послуги «Покупка '
        'частинами», кількість платежів, оформлення та юридична інформація.',
    ),
    ('monobank_chastynamy', 'en'): (
        None,
        'Pay for website development in instalments with monobank | Universal Bank: Pay in Parts '
        'terms, number of payments, how to apply and legal information.',
    ),
    ('refund', 'uk'): (
        None,
        'Політика повернення коштів PrometeyLabs: умови, строки та порядок повернення оплати за '
        'розробку сайтів, Telegram-ботів і рекламу. Як подати заявку онлайн.',
    ),
    ('refund', 'ru'): (
        None,
        'Политика возврата средств PrometeyLabs: условия, сроки и порядок возврата оплаты за '
        'разработку сайтов, Telegram-ботов и рекламу. Как подать заявку на возврат.',
    ),
}


def current_lang() -> str:
    code = (translation.get_language() or X_DEFAULT_LANG).split('-')[0]
    return code if code in ALL_LANGS else X_DEFAULT_LANG


def localized_path(name: str, lang: str, kwargs: dict | None = None) -> str | None:
    try:
        with translation.override(lang):
            return reverse(name, kwargs=kwargs or None)
    except NoReverseMatch:
        return None


def blog_post_languages(post) -> tuple[str, ...]:
    """uk always; ru only when the post has its own RU title and body. No EN copy exists."""
    langs = ['uk']
    if (getattr(post, 'title_ru', '') or '').strip() and (getattr(post, 'content_ru', '') or '').strip():
        langs.append('ru')
    return tuple(langs)


def languages_for(name: str, obj=None) -> tuple[str, ...]:
    if name == BLOG_DETAIL:
        return blog_post_languages(obj) if obj is not None else ('uk',)
    return PAGE_LANGUAGES.get(name, ())


def is_registered(name: str | None) -> bool:
    return bool(name) and (name in PAGE_LANGUAGES or name == BLOG_DETAIL)


def _page_suffix(request, name: str) -> str:
    if name != BLOG_LIST:
        return ''
    raw = request.GET.get('page', '')
    try:
        number = int(raw)
    except (TypeError, ValueError):
        return ''
    return f'?page={number}' if number > 1 else ''


def build_seo(request, obj=None) -> dict | None:
    """SEO head data for the current request, or None for unregistered pages."""
    if getattr(request, 'urlconf', None):
        return None  # proposal console (k/<key>) — own urlconf, never indexed
    match = getattr(request, 'resolver_match', None)
    if match is None:
        return None
    name = match.view_name
    if not is_registered(name):
        return None
    lang = current_lang()
    kwargs = match.kwargs or None
    langs = languages_for(name, obj)
    suffix = _page_suffix(request, name)

    path = localized_path(name, lang, kwargs) or request.path
    canonical = SITE + path + suffix
    indexable = lang in langs
    alternates = []
    if indexable:
        for code in ALL_LANGS:
            if code not in langs:
                continue
            alt_path = localized_path(name, code, kwargs)
            if alt_path:
                alternates.append((code, SITE + alt_path + suffix))
        x_default = localized_path(name, X_DEFAULT_LANG, kwargs)
        if x_default and X_DEFAULT_LANG in langs:
            alternates.append(('x-default', SITE + x_default + suffix))
    title, description = META_OVERRIDES.get((name, lang), (None, None))
    return {
        'name': name,
        'lang': lang,
        'canonical': canonical,
        'robots': 'index, follow' if indexable else 'noindex, follow',
        'indexable': indexable,
        'alternates': alternates,
        'title': title,
        'description': description,
    }


def sitemap_entries():
    """(lang, url name) for every indexable static page version."""
    out = []
    for name, langs in PAGE_LANGUAGES.items():
        for lang in langs:
            if localized_path(name, lang):
                out.append((lang, name))
    return out
