"""Фільтри шаблонів demo-корп сайту."""
from django import template
from django.utils.html import conditional_escape, format_html

register = template.Library()


@register.filter
def accent(text, part):
    """Обгортає першу появу `part` у `text` в <span class="dc-accent">. Усе екранується."""
    text = str(text or '')
    part = str(part or '').strip()
    if not part or part not in text:
        return conditional_escape(text)
    before, after = text.split(part, 1)
    return format_html(
        '{}<span class="dc-accent">{}</span>{}', before, part, after,
    )


@register.filter
def lang_label(code):
    """Код мови → підпис у перемикачі (uk → UA, cs → CZ)."""
    return {'uk': 'UA', 'cs': 'CZ'}.get(code, str(code).upper())
