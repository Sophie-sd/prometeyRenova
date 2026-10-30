"""Спільний канон ДАНИХ КП (CMS-шар) для всіх КП: імпорт і нормалізація наявних.

Що робимо тут (лише дані; розмітку, лічильник, eyebrow-и та RU-підписи рендерить FE):
- lead: без «Кодописн…» як дефолту → «Написаний з нуля…» (UA) / «Написанный с нуля…» (RU);
- highlights: короткий заголовок без крапки в кінці, «Enterprise-безпека» → «Корпоративна безпека»;
- payment: варіанти «50 / 50», «50%/50%», «50 на 50», «50% + 50%» → канонічне «50/50»,
  щоб presenters.pay_figure / payment_amount рахували суми з пакета (без хардкоду);
- recommendations: без пункту-дубля гарантії (той самий критерій, що FE presenters).

Контент конкретного клієнта (напр. apply_copy_corp_budivnytstvo) сюди НЕ входить.
"""
import re

from django.utils.html import strip_tags

from .proposal_presenters import _GUARANTEE, _norm

LANGS = ('', '_ru', '_en', '_cs')

_LEAD_RULES = (
    (re.compile(r'\bКодописн(ий|а|е|і)\b'), {'ий': 'Написаний з нуля', 'а': 'Написана з нуля',
                                              'е': 'Написане з нуля', 'і': 'Написані з нуля'}),
    (re.compile(r'\bкодописн(ий|а|е|і)\b'), {'ий': 'написаний з нуля', 'а': 'написана з нуля',
                                              'е': 'написане з нуля', 'і': 'написані з нуля'}),
    (re.compile(r'\bКодописн(ый|ая|ое|ые)\b'), {'ый': 'Написанный с нуля', 'ая': 'Написанная с нуля',
                                                'ое': 'Написанное с нуля', 'ые': 'Написанные с нуля'}),
    (re.compile(r'\bкодописн(ый|ая|ое|ые)\b'), {'ый': 'написанный с нуля', 'ая': 'написанная с нуля',
                                                'ое': 'написанное с нуля', 'ые': 'написанные с нуля'}),
)
_HIGHLIGHT_TERMS = (
    (re.compile(r'\bEnterprise[- ]безпек', re.I), 'Корпоративна безпек'),
    (re.compile(r'\bEnterprise[- ]безопасност', re.I), 'Корпоративная безопасност'),
)
_FIFTY = re.compile(r'\b50\s?%?\s?(?:/|\+|на|na)\s?50\s?%?(?!\d)', re.I)


def sanitize_lead(text: str) -> str:
    out = text or ''
    for rx, forms in _LEAD_RULES:
        out = rx.sub(lambda m, f=forms: f[m.group(1)], out)
    return out


def normalize_highlight(title: str) -> str:
    out = re.sub(r'\s+', ' ', title or '').strip().rstrip('.')
    for rx, repl in _HIGHLIGHT_TERMS:
        out = rx.sub(repl, out)
    return out


def normalize_payment_text(text: str) -> str:
    return _FIFTY.sub('50/50', text or '')


def is_guarantee_dup_row(title: str, body: str, guarantee_html: str) -> bool:
    """Той самий критерій, що presenters.is_guarantee_duplicate, але для сирих полів."""
    if not guarantee_html:
        return False
    t, b, gua = _norm(title), _norm(body), _norm(guarantee_html)
    if _GUARANTEE.match(t):
        return True
    core = re.sub(r'^(гарантія|гарантия|guarantee|záruka)\s*', '', b)
    return bool(core) and core in gua


def normalize_proposal_data(data: dict) -> list[str]:
    """Нормалізує proposal.json-словник на місці. Повертає список змін (для логу імпорту)."""
    log = []
    for l in LANGS:
        k = f'lead{l}'
        if data.get(k) and sanitize_lead(data[k]) != data[k]:
            data[k] = sanitize_lead(data[k])
            log.append(f'{k}: «Кодописн…» → «Написаний з нуля…»')
    for i, row in enumerate(data.get('highlights') or []):
        for f in ('title',) + tuple(f'title{l}' for l in LANGS[1:]):
            if row.get(f) and normalize_highlight(row[f]) != row[f]:
                row[f] = normalize_highlight(row[f])
                log.append(f'highlights[{i}].{f}: нормалізовано')
    gua = data.get('guarantee_html') or ''
    kept = []
    for row in data.get('specs') or []:
        if row.get('kind') == 'payment':
            for l in LANGS:
                for b in ('title', 'body'):
                    f = f'{b}{l}'
                    if row.get(f) and normalize_payment_text(row[f]) != row[f]:
                        row[f] = normalize_payment_text(row[f])
                        log.append(f'payment.{f}: → 50/50')
        if row.get('kind') == 'recommendation' and is_guarantee_dup_row(
                row.get('title', ''), row.get('body', ''), gua):
            log.append(f'recommendation «{strip_tags(row.get("title", ""))}»: дубль гарантії — прибрано')
            continue
        kept.append(row)
    if 'specs' in data:
        data['specs'] = kept
    return log
