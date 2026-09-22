from django import template

from apps.core.public_files import public_file_url

register = template.Library()


@register.filter
def puburl(file_field):
    """media, якщо файл на диску; інакше static seed з тим самим ім'ям."""
    return public_file_url(file_field)


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