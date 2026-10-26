"""Ads landing views kept out of views.py (file length)."""
from .ads_context import dorobka_ads_context
from .mixins import BasePageView, homepage_portfolio_strip


class DorobkaSajtuView(BasePageView):
    template_name = 'pages/dorobka-sajtu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio_strip'] = homepage_portfolio_strip()
        context.update(dorobka_ads_context())
        return context
