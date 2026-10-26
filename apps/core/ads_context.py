"""Context for ads landings: copy + breadcrumbs + JSON-LD from one source."""
from django.urls import reverse
from django.utils import translation

from .ads_copy import (
    SITE,
    SHOP_SLUGS,
    contacts_copy,
    crumbs_copy,
    faq_pairs,
    lang,
    process_site_copy,
    rs_copy,
    shop_copy,
)
from .ads_copy_dorobka import dorobka_copy
from .ads_schema import hreflang_urls, schema_scripts
from .mixins import published_portfolio_queryset


def _abs(path):
    return SITE + path


def _reverse(name, language):
    with translation.override(language):
        return reverse(name)


def hreflang_for(name):
    return hreflang_urls(_reverse(name, 'uk'), _reverse(name, 'ru'))


def _crumbs(last_name, last_url):
    labels = crumbs_copy()
    return [
        {'name': labels['home'], 'url': _abs(_reverse('home', lang()))},
        {'name': labels['services'], 'url': ''},
        {'name': last_name, 'url': last_url},
    ]


def shop_portfolio_projects():
    found = {
        project.slug: project
        for project in published_portfolio_queryset().filter(slug__in=SHOP_SLUGS)
    }
    return [found[slug] for slug in SHOP_SLUGS if slug in found]


def _seo_only(name):
    return {
        'ads_tz': False,
        'ads_copy': {'faq_h2': '', 'types': (), 'types_h2': '', 'guarantee_h2': '', 'guarantee': '',
                     'process_h2': '', 'prices_h2': '', 'include_h3': '', 'include': '', 'exclude_h3': '',
                     'exclude': '', 'portfolio_h2': '', 'shops_note': '', 'all_works': '', 'line': '',
                     'form_note': '', 'trust': '', 'offer_line': '', 'crumb': ''},
        'ads_faq': [],
        'ads_contacts': contacts_copy(),
        'ads_crumbs': [],
        'ads_seo': hreflang_for(name),
        'ads_process': {'title': '', 'note': '', 'steps': ()},
        'ads_json_ld': [],
        'shop_portfolio': [],
    }


def shop_ads_context():
    seo = hreflang_for('internet_shop_v2')
    if lang() not in ('uk', 'ru'):
        ctx = _seo_only('internet_shop_v2')
        ctx['ads_seo'] = seo
        return ctx
    copy = shop_copy()
    faq = faq_pairs(copy['faq'])
    crumbs = _crumbs(copy['crumb'], seo['canonical'])
    process = process_site_copy()
    return {
        'ads_tz': True,
        'ads_copy': copy,
        'ads_faq': faq,
        'ads_contacts': contacts_copy(),
        'ads_crumbs': crumbs,
        'ads_seo': seo,
        'ads_process': process,
        'ads_json_ld': schema_scripts(crumbs, faq),
        'shop_portfolio': shop_portfolio_projects(),
        'page_title': copy['title'],
        'meta_description': copy['description'],
        'og_title': copy['title'],
    }


def rs_ads_context():
    seo = hreflang_for('rozrobka_sajtiv')
    if lang() not in ('uk', 'ru'):
        ctx = _seo_only('rozrobka_sajtiv')
        ctx['ads_seo'] = seo
        return ctx
    copy = rs_copy()
    faq = faq_pairs(copy['faq'])
    crumbs = _crumbs(copy['crumb'], seo['canonical'])
    return {
        'ads_tz': True,
        'ads_copy': copy,
        'ads_faq': faq,
        'ads_contacts': contacts_copy(),
        'ads_crumbs': crumbs,
        'ads_seo': seo,
        'ads_process': process_site_copy(),
        'ads_json_ld': schema_scripts(crumbs, faq),
        'page_title': copy['title'],
        'meta_description': copy['description'],
        'og_title': copy['title'],
    }


def dorobka_ads_context():
    copy = dorobka_copy()
    seo = hreflang_for('dorobka_sajtu')
    faq = faq_pairs(copy['faq'])
    crumbs = _crumbs(copy['crumb'], seo['canonical'])
    return {
        'ads_copy': copy,
        'ads_faq': faq,
        'ads_contacts': contacts_copy(),
        'ads_crumbs': crumbs,
        'ads_seo': seo,
        'ads_json_ld': schema_scripts(crumbs, faq),
        'page_title': copy['title'],
        'meta_description': copy['description'],
        'og_title': copy['title'],
        'hide_developer_modal': True,
        'hide_lang_suggest': True,
    }


def corporate_ads_context():
    seo = hreflang_for('corporate_website_v2')
    labels = crumbs_copy()
    last = 'Корпоративні сайти та лендінги' if lang() == 'uk' else 'Корпоративные сайты и лендинги'
    crumbs = _crumbs(last, seo['canonical'])
    return {
        'ads_crumbs': crumbs,
        'ads_seo': seo,
        'ads_contacts': contacts_copy(),
        'ads_json_ld': schema_scripts(crumbs),
    }


def home_hreflang_context():
    return {'ads_seo': hreflang_for('home')}
