"""Публічна вітрина demo-лендінгу: одна сторінка + lead-форма (HTMX)."""
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from apps.demotenant.content import get_blocks_map, is_visible
from apps.demotenant.views_common import make_admin_access_view, make_admin_login_view, make_theme_css_view

from .block_defaults import BLOCK_REGISTRY
from .forms import LandingLeadForm
from .models import LandingSite


def _get_active_site(slug: str) -> LandingSite:
    return get_object_or_404(LandingSite, slug=slug, is_active=True)


@require_GET
def home(request, slug):
    site = _get_active_site(slug)
    blocks_map = get_blocks_map(site)
    faq_pairs = [(f'faq_{i}_q', f'faq_{i}_a') for i in range(1, 4)]
    process_steps = ['step_1', 'step_2', 'step_3', 'step_4']

    context = {
        'site': site,
        'blocks_map': blocks_map,
        'registry': BLOCK_REGISTRY,
        'faq_pairs': faq_pairs,
        'process_steps': process_steps,
        'offers': site.offers.filter(is_active=True),
        'gallery_images': site.gallery_images.all(),
        'before_after_pairs': site.before_after_pairs.all(),
        'testimonials': site.testimonials.all(),
        'partners': site.partners.all(),
        'lead_form': LandingLeadForm(),
        'stats_visible': is_visible(blocks_map, 'stats', 'stats_visible'),
        'offers_visible': is_visible(blocks_map, 'offers', 'offers_visible'),
        'process_visible': is_visible(blocks_map, 'process', 'process_visible'),
        'gallery_visible': is_visible(blocks_map, 'gallery', 'gallery_visible'),
        'before_after_visible': is_visible(blocks_map, 'before_after', 'before_after_visible'),
        'reviews_visible': is_visible(blocks_map, 'reviews', 'reviews_visible'),
        'faq_visible': is_visible(blocks_map, 'faq', 'faq_visible'),
        'partners_visible': is_visible(blocks_map, 'footer', 'partners_visible'),
    }
    return render(request, 'demolanding/home.html', context)


@require_POST
def lead(request, slug):
    site = _get_active_site(slug)
    if request.POST.get('honeypot'):
        # Тихий success без запису — не підказуємо ботам, що поле розпізнане.
        return render(request, 'demolanding/partials/lead_success.html', {'site': site})

    form = LandingLeadForm(request.POST)
    if form.is_valid():
        lead_obj = form.save(commit=False)
        lead_obj.tenant = site
        lead_obj.save()
        return render(request, 'demolanding/partials/lead_success.html', {'site': site})
    return render(
        request,
        'demolanding/partials/lead_form.html',
        {
            'site': site,
            'lead_form': form,
            'blocks_map': get_blocks_map(site),
            'registry': BLOCK_REGISTRY,
        },
    )


admin_access = make_admin_access_view(
    LandingSite, 'demolanding/admin_access.html', registry=BLOCK_REGISTRY,
)
admin_login = make_admin_login_view(LandingSite)
theme_css = make_theme_css_view(LandingSite)
