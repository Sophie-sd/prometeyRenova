"""Views для standalone-сторінок комерційних пропозицій."""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView

from apps.core.proposal_models import Proposal, ProposalSpec
from apps.core.utils import get_site_contact_settings


class ProposalDetailView(DetailView):
    """Публічна сторінка КП за slug (лише is_published=True)."""

    model = Proposal
    template_name = 'proposal/detail.html'
    context_object_name = 'proposal'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return (
            Proposal.objects.filter(is_published=True)
            .prefetch_related('modules', 'packages', 'specs')
        )

    def get_object(self, queryset=None):
        qs = queryset if queryset is not None else self.get_queryset()
        return get_object_or_404(qs, slug=self.kwargs.get(self.slug_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal = self.object
        specs = list(proposal.specs.all())
        title = proposal.get_localized_title()
        lead = proposal.get_localized_lead()
        context.update({
            'page_title': title,
            'meta_description': (lead or title)[:160],
            'og_title': title,
            'keywords': '',
            'current_year': timezone.now().year,
            'contacts': get_site_contact_settings(),
            'modules': proposal.modules.all(),
            'packages': proposal.packages.all(),
            'spec_items': [s for s in specs if s.kind == ProposalSpec.Kind.SPEC],
            'payment_items': [s for s in specs if s.kind == ProposalSpec.Kind.PAYMENT],
            'recommendation_items': [
                s for s in specs if s.kind == ProposalSpec.Kind.RECOMMENDATION
            ],
        })
        return context
