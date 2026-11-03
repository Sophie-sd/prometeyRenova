from django import template

from apps.core.seo import BLOG_DETAIL, build_seo

register = template.Library()


@register.simple_tag(takes_context=True)
def seo_data(context):
    """Central canonical / hreflang / robots / meta overrides (see apps.core.seo)."""
    request = context.get('request')
    if request is None:
        return None
    obj = None
    match = getattr(request, 'resolver_match', None)
    if match is not None and match.view_name == BLOG_DETAIL:
        obj = context.get('post')
    return build_seo(request, obj)


@register.simple_tag
def organization_json_ld():
    """The one Organization node (with @id) for every page."""
    from apps.core.ads_schema import dumps, organization_ld

    return dumps(organization_ld())
