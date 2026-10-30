"""POST-перемикач валюти. HTMX міняє фрагменти цін, інакше редірект."""
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
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
        from django.utils import translation

        # HX-запит іде на неперекладений URL: мову фрагментів беремо з next (/ru/proposal/…)
        lang = translation.get_language_from_path(request.POST.get('next') or '') or translation.get_language()
        with translation.override(lang):
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
