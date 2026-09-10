"""Публічна вітрина demo-корпоративного сайту: home/production/about/contacts
(+ catalog/category/product, лише якщо `has_catalog`). Каталог без оплат —
«Купити» відкриває HTMX-заявку з підставленим товаром, не кошик."""
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from apps.demotenant.content import get_blocks_map, is_visible
from apps.demotenant.views_common import make_admin_access_view, make_admin_login_view, make_theme_css_view

from .block_defaults import BLOCK_REGISTRY
from .catalog_models import CorpCategory, CorpProduct
from .forms import CorpLeadForm
from .models import CorpSite


def _get_active_site(slug: str) -> CorpSite:
    return get_object_or_404(CorpSite, slug=slug, is_active=True)


def _require_catalog(site: CorpSite) -> None:
    if not site.has_catalog:
        raise Http404('Каталог вимкнено для цього сайту')


def _base_context(site, **extra):
    blocks_map = get_blocks_map(site)
    context = {
        'site': site,
        'blocks_map': blocks_map,
        'registry': BLOCK_REGISTRY,
        'lead_form': CorpLeadForm(),
        'partners': site.partners.all(),
        'footer_partners_visible': is_visible(blocks_map, 'footer', 'partners_visible'),
    }
    context.update(extra)
    return context


@require_GET
def home(request, slug):
    site = _get_active_site(slug)
    blocks_map = get_blocks_map(site)
    context = _base_context(
        site,
        process_steps=site.production_steps.all(),
        testimonials=site.testimonials.all(),
        featured_products=(
            site.products.filter(is_active=True, is_featured=True)[:8] if site.has_catalog else []
        ),
        reviews_visible=is_visible(blocks_map, 'home', 'reviews_visible'),
        partners_visible=is_visible(blocks_map, 'home', 'partners_visible'),
    )
    return render(request, 'democorp/home.html', context)


@require_GET
def production(request, slug):
    site = _get_active_site(slug)
    blocks_map = get_blocks_map(site)
    context = _base_context(
        site,
        process_steps=site.production_steps.all(),
        gallery_images=site.gallery_images.filter(kind='production'),
        certificates=site.gallery_images.filter(kind='certificate'),
        certificates_visible=is_visible(blocks_map, 'production', 'certificates_visible'),
    )
    return render(request, 'democorp/production.html', context)


@require_GET
def about(request, slug):
    site = _get_active_site(slug)
    return render(
        request,
        'democorp/about.html',
        _base_context(
            site,
            about_fallback=site.gallery_images.filter(kind='production').first(),
        ),
    )


@require_GET
def contacts(request, slug):
    site = _get_active_site(slug)
    return render(request, 'democorp/contacts.html', _base_context(site))


@require_GET
def catalog(request, slug):
    site = _get_active_site(slug)
    _require_catalog(site)
    categories = site.categories.filter(is_active=True)
    products = site.products.filter(is_active=True).select_related('category').prefetch_related('images')
    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    return render(
        request, 'democorp/catalog.html',
        _base_context(site, categories=categories, products=products, active_category=category_slug),
    )


@require_GET
def product_detail(request, slug, product_slug):
    site = _get_active_site(slug)
    _require_catalog(site)
    product = get_object_or_404(
        CorpProduct.objects.select_related('category').prefetch_related('images'),
        tenant=site, slug=product_slug, is_active=True,
    )
    return render(request, 'democorp/product_detail.html', _base_context(site, product=product))


@require_POST
def lead(request, slug):
    site = _get_active_site(slug)
    if request.POST.get('honeypot'):
        return render(request, 'democorp/partials/lead_success.html', {'site': site})

    form = CorpLeadForm(request.POST)
    product = None
    product_slug = request.POST.get('product_slug', '')
    if site.has_catalog and product_slug:
        product = CorpProduct.objects.filter(tenant=site, slug=product_slug).first()
    if form.is_valid():
        lead_obj = form.save(commit=False)
        lead_obj.tenant = site
        lead_obj.product = product
        lead_obj.save()
        return render(request, 'democorp/partials/lead_success.html', {'site': site})
    return render(
        request,
        'democorp/partials/lead_form.html',
        _base_context(site, lead_form=form, product=product),
        status=400,
    )


admin_access = make_admin_access_view(
    CorpSite, 'democorp/admin_access.html', registry=BLOCK_REGISTRY,
)
admin_login = make_admin_login_view(CorpSite)
theme_css = make_theme_css_view(CorpSite)
