"""Inclusion-теги sales-шару демо-магазину."""
from django import template

from apps.demoshop.sales_notes import (
    ADMIN_MODEL_SCOPE,
    notes_for_admin_scope,
    notes_for_page,
    page_from_url_name,
)

register = template.Library()


@register.inclusion_tag('demoshop/partials/_sales_chrome.html', takes_context=True)
def sales_chrome(context):
    request = context.get('request')
    url_name = ''
    if request is not None and getattr(request, 'resolver_match', None):
        url_name = request.resolver_match.url_name or ''
    page = page_from_url_name(url_name)
    shop = context.get('shop')
    return {
        'notes': notes_for_page(page) if page else (),
        'shop': shop,
        'page': page,
    }


@register.simple_tag
def sales_page_notes(page):
    return notes_for_page(page or '')


@register.simple_tag
def sales_admin_notes(model_name):
    scope = ADMIN_MODEL_SCOPE.get((model_name or '').lower())
    if not scope:
        return ()
    return notes_for_admin_scope(scope)
