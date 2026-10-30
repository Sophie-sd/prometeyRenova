"""Підготовка блоків КП до рендеру (лише відображення; дані в БД не змінюються).

- Умови оплати: ключова цифра (сума / % / 50/50) окремо від заголовка, без дубля заголовка в тексті.
- Рекомендації: без пунктів, що повторюють гарантію з секції 07.
"""
import re

from django.utils.html import strip_tags

_MONEY = re.compile(
    r'(?:від\s+|от\s+|from\s+|od\s+)?'
    r'(?:[€$₴]\s?\d[\d\s.,]*(?:\s?[–-]\s?\d[\d\s.,]*)?'
    r'|\d[\d\s.,]*(?:\s?[–-]\s?\d[\d\s.,]*)?\s?(?:€|EUR|грн|₴|\$|USD|Kč|CZK))'
    r'(?:\s?/\s?(?:міс|мес|mo|month|měs)\.?)?',
    re.IGNORECASE,
)
_RATIO = re.compile(r'\b\d{1,3}\s?/\s?\d{1,3}\b')
_PCT = re.compile(r'\d{1,3}\s?%')
_GUARANTEE = re.compile(r'^\s*(гарант|guarant|záruk)', re.IGNORECASE)


def _norm(text):
    return re.sub(r'[\W_]+', ' ', strip_tags(text or '').lower()).strip()


def pay_figure(title, body):
    """Лише цифра пункту оплати: «50/50», «0%», «30%». Без цифри — '' (рядок не рендеримо)."""
    for rx in (_RATIO, _PCT):
        for src in (title or '', body or ''):
            m = rx.search(src)
            if m:
                return re.sub(r'\s+', '', m.group(0))
    return ''


def has_money(text):
    m = _MONEY.search(text or '')
    return bool(m and re.search(r'\d', m.group(0)))


def _eur(lo, hi):
    lo, hi = int(lo), int(hi)
    return f'{lo} €' if lo == hi else f'{lo}–{hi} €'


def _single_eur_price(packages):
    """(lo, hi) ціни, якщо в КП рівно один пакет у EUR з ціною; інакше None."""
    if not packages or len(packages) != 1:
        return None
    pk = packages[0]
    if not pk.price or (getattr(pk, 'currency', '') or 'EUR').strip().upper() not in ('EUR', '€'):
        return None
    return pk.price, (pk.price_high or pk.price)


_INSTALMENTS = re.compile(r'(\d{1,2})\s*(?:платеж|платіж|платеж|payment|splát)', re.I)
_PER_MONTH = re.compile(r'(\d[\d ]*)\s?(?:[–-]\s?(\d[\d ]*))?\s?€\s?/\s?(?:міс|мес|mo|month|měs)', re.I)


def payment_amount(title, body, figure, price):
    """Суми лише з даних КП: 50/50 — половина ціни пакета; розстрочка — N × платіж/міс і разом. Нічого не вигадуємо."""
    from django.utils.translation import gettext as _

    if figure == '50/50' and price:
        lo, hi = price[0] / 2, price[1] / 2
        if lo == int(lo) and hi == int(hi):
            return f"{_eur(lo, hi)} {_('передоплата')} + {_eur(lo, hi)} {_('після тестування')}"
    if has_money(title):
        return ''  # сума вже в назві (дані КП) — не дублюємо
    pct = re.fullmatch(r'(\d{1,3})%', figure or '')
    if pct and price and 0 < int(pct.group(1)) < 100:
        k = int(pct.group(1))
        lo, hi = price[0] * k / 100, price[1] * k / 100
        if lo == int(lo) and hi == int(hi):
            return _eur(lo, hi)
    n, m = _INSTALMENTS.search(body or ''), _PER_MONTH.search(body or '')
    if n and m:
        cnt = int(n.group(1))
        lo = int(re.sub(r'\D', '', m.group(1)))
        hi = int(re.sub(r'\D', '', m.group(2))) if m.group(2) else lo
        return f"{cnt} × {_eur(lo, hi)}/{_('міс')}, {_('разом')} {_eur(cnt * lo, cnt * hi)}"
    return ''


def prepare_payment_items(items, packages=None):
    """pay_figure — лише цифра; pay_amount — суми (EUR, конвертує перемикач валют); pay_body — опис.
    Заголовок не дублюється ні в цифрі, ні в описі."""
    price = _single_eur_price(packages)
    for item in items:
        title, body = item.get_localized_title(), item.get_localized_body()
        item.pay_figure = pay_figure(title, body)
        if _norm(item.pay_figure) == _norm(title):
            item.pay_figure = ''
        if _norm(body) == _norm(title):
            body = ''
        item.pay_amount = payment_amount(title, body, item.pay_figure, price)
        item.pay_body = body
    return items


# Нумеровані секції КП (канон Design Lead): 01 Структура … 08 Оплата, 09 CTA. Hero і демо-віджет не нумеруються.
_SECTIONS = ('arch', 'intro', 'modules', 'specs', 'expert', 'packages', 'guarantee', 'payment', 'cta')


def section_numbers(present):
    """Наскрізна нумерація лише наявних секцій: {'arch': '01', ...}; відсутні не займають номер."""
    out, n = {}, 0
    for key in _SECTIONS:
        if present.get(key, key == 'cta'):
            n += 1
            out[key] = f'{n:02d}'
    return out


def is_guarantee_duplicate(item, guarantee_text):
    """Пункт рекомендацій лише повторює гарантію (заголовок «Гарантія…» або текст уже є в секції 07)."""
    if not guarantee_text:
        return False
    title, body = _norm(item.get_localized_title()), _norm(item.get_localized_body())
    gua = _norm(guarantee_text)
    if _GUARANTEE.match(title):
        return True
    core = re.sub(r'^(гарантія|гарантия|guarantee|záruka)\s*', '', body)
    return bool(core) and core in gua


def visible_recommendations(items, guarantee_text):
    return [i for i in items if not is_guarantee_duplicate(i, guarantee_text)]


# Попередньо стиснені варіанти статичних hero (static/proposal/img/*-{w}w.webp); media-фото без варіантів — як є.
_HERO_VARIANTS = {
    'proposal/img/seal-on-dark.webp': ((360, 600, 900), (897, 901)),
}


def hero_responsive(url):
    """(srcset, (w, h)) для відомого статичного hero, інакше ('', None)."""
    from django.templatetags.static import static

    for path, (widths, wh) in _HERO_VARIANTS.items():
        if url and url.split('?')[0].endswith(path):
            stem = path.rsplit('.', 1)[0]
            return ', '.join(f'{static(f"{stem}-{w}w.webp")} {w}w' for w in widths), wh
    return '', None
