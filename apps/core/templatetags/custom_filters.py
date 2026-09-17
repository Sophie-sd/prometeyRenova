from django import template

register = template.Library()


@register.filter
def split(value, arg):
    """
    Розділяє рядок на список за роздільником
    Використання: {{ value|split:"," }}
    """
    if value:
        return [item.strip() for item in value.split(arg)]
    return []


@register.filter
def has_any_permission(items):
    """Чи є хоч один пункт із has_permission=True (Unfold sidebar групи)."""
    return any(item.get('has_permission') for item in items or []) 