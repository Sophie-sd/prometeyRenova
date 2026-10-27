"""JSON-LD builders for ads landings. FAQ text comes from the same Python lists as the visible FAQ."""
import json

from django.utils.safestring import mark_safe

from .ads_copy import SITE, lang
from .utils import SITE_CONTACT_DEFAULTS, get_site_contact_settings

LOCALITY = {'uk': 'Київ', 'ru': 'Kyiv'}


def dumps(obj):
    return mark_safe(json.dumps(obj, ensure_ascii=False, separators=(',', ':')))


def breadcrumb_ld(items):
    # Google requires `item` on every ListItem except the last one, so
    # intermediate crumbs without a URL (e.g. «Послуги») stay visible only.
    items = [
        item for pos, item in enumerate(items, start=1)
        if item.get('url') or pos == len(items)
    ]
    elements = []
    for index, item in enumerate(items, start=1):
        entry = {
            '@type': 'ListItem',
            'position': index,
            'name': item['name'],
        }
        if item.get('url'):
            entry['item'] = item['url']
        elements.append(entry)
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': elements,
    }


def faq_ld(pairs):
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': item['q'],
                'acceptedAnswer': {'@type': 'Answer', 'text': item['a']},
            }
            for item in pairs
        ],
    }


def _same_as(contact):
    urls = []
    for attr, fallback in (
        ('instagram_url', SITE_CONTACT_DEFAULTS['instagram_url']),
        ('facebook_url', SITE_CONTACT_DEFAULTS['facebook_url']),
        ('linkedin_url', SITE_CONTACT_DEFAULTS['linkedin_url']),
        ('tiktok_url', SITE_CONTACT_DEFAULTS['tiktok_url']),
        ('telegram_url', SITE_CONTACT_DEFAULTS['telegram_url']),
    ):
        value = (getattr(contact, attr, None) or fallback or '').strip()
        if value:
            urls.append(value)
    return urls


def organization_ld():
    contact = get_site_contact_settings()
    code = lang()
    return {
        '@context': 'https://schema.org',
        '@type': ['Organization', 'ProfessionalService'],
        'name': 'PrometeyLabs',
        'url': SITE + '/',
        'email': 'info@prometeylabs.com',
        'telephone': '+380639520565',
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': 'бульвар Тараса Шевченка 46а',
            'addressLocality': LOCALITY.get(code, 'Kyiv'),
            'addressCountry': 'UA',
        },
        'sameAs': _same_as(contact),
    }


def hreflang_urls(uk_path, ru_path):
    uk = SITE + uk_path
    ru = SITE + ru_path
    current = ru if lang() == 'ru' else uk
    return {
        'canonical': current,
        'uk': uk,
        'ru': ru,
        'x_default': uk,
    }


def schema_scripts(breadcrumbs, faq_pairs=None):
    blocks = [dumps(breadcrumb_ld(breadcrumbs)), dumps(organization_ld())]
    if faq_pairs:
        blocks.append(dumps(faq_ld(faq_pairs)))
    return blocks
