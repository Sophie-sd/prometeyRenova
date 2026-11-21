"""POST-перемикач валюти. HTMX міняє фрагменти цін, інакше редірект."""
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import translation
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from apps.core.fx import CURRENCY_COOKIE, CURRENCY_COOKIE_AGE, normalize_currency
from apps.core.i18n_views import _redirect_target

_REGIONS = {'home', 'shop', 'proposal', 'soft'}


def _with_cookie(response, code):
    response.set_cookie(
        CURRENCY_COOKIE,
        code,
        max_age=CURRENCY_COOKIE_AGE,
        path=getattr(settings, 'LANGUAGE_COOKIE_PATH', '/') or '/',
        domain=getattr(settings, 'LANGUAGE_COOKIE_DOMAIN', None),
        secure=getattr(settings, 'LANGUAGE_COOKIE_SECURE', False),
        httponly=True,
        samesite=getattr(settings, 'LANGUAGE_COOKIE_SAMESITE', 'Lax') or 'Lax',
    )
    return response


def _fragment_lang(request):
    """Language of the page that sent the HTMX swap.

    ``set_currency`` lives at ``/i18n/set_currency/`` (no language prefix), so the
    request language is always Ukrainian. The page path is in POST ``next``,
    with ``HX-Current-URL`` as a fallback.
    """
    allowed = {code for code, _label in settings.LANGUAGES}
    sources = (
        request.POST.get('next') or '',
        request.headers.get('HX-Current-URL') or '',
    )
    for raw in sources:
        path = urlparse(raw).path if '://' in raw else raw
        code = translation.get_language_from_path(path or '')
        if code in allowed:
            return code
    return 'uk'


def _proposal_swap_context(proposal):
    from apps.core.proposal_models import ProposalSpec
    from apps.core.proposal_presenters import prepare_payment_items

    packages = list(proposal.packages.all())
    pay = prepare_payment_items(
        list(proposal.specs.filter(kind=ProposalSpec.Kind.PAYMENT).order_by('order', 'pk')), packages
    )
    return {'proposal': proposal, 'packages': packages,
            'payment_items': pay, 'pay_has_amounts': any(i.pay_amount for i in pay)}


def _hx_fragment(request, region):
    with translation.override(_fragment_lang(request)):
        if region == 'proposal':
            from apps.core.proposal_models import Proposal

            proposal = (
                Proposal.objects.filter(
                    slug=request.POST.get('slug') or '',
                    is_published=True,
                )
                .prefetch_related('packages')
                .first()
            )
            if proposal is None:
                return HttpResponse(status=404)
            return render(
                request,
                'fx/swap_proposal.html',
                _proposal_swap_context(proposal),
            )
        return render(request, f'fx/swap_{region}.html')


@never_cache
@require_POST
def set_currency(request):
    code = normalize_currency(request.POST.get('currency'))
    request.COOKIES[CURRENCY_COOKIE] = code
    if request.headers.get('HX-Request') == 'true':
        region = request.POST.get('region') or ''
        if region not in _REGIONS:
            return _with_cookie(HttpResponse(status=400), code)
        return _with_cookie(_hx_fragment(request, region), code)
    next_url = _redirect_target(request, request.POST.get('next')) or '/'
    return _with_cookie(HttpResponseRedirect(next_url), code)
