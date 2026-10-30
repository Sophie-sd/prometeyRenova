"""Views для standalone-сторінок комерційних пропозицій."""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView

from apps.core.proposal_models import Proposal, ProposalSpec
from apps.core.proposal_presenters import hero_responsive, prepare_payment_items, section_numbers, visible_recommendations
from apps.core.utils import get_site_contact_settings


class ProposalDetailView(DetailView):
    """Публічна сторінка КП за slug (лише is_published=True і без deleted_at)."""

    model = Proposal
    template_name = 'proposal/detail.html'
    context_object_name = 'proposal'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return (
            Proposal.visible_objects()
            .select_related('demo_shop', 'demo_corp', 'demo_landing')
            .prefetch_related(
                'modules',
                'packages',
                'specs',
                'highlights',
                'arch_nodes',
            )
        )

    def get_object(self, queryset=None):
        qs = queryset if queryset is not None else self.get_queryset()
        return get_object_or_404(qs, slug=self.kwargs.get(self.slug_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal = self.object
        specs = list(proposal.specs.all())
        arch_nodes = list(proposal.arch_nodes.all())
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
            'highlights': list(proposal.highlights.all()),
            'arch_root': arch_nodes[0] if arch_nodes else None,
            'arch_branches': arch_nodes[1:] if arch_nodes else [],
            'spec_items': [s for s in specs if s.kind == ProposalSpec.Kind.SPEC],
            'payment_items': prepare_payment_items(
                [s for s in specs if s.kind == ProposalSpec.Kind.PAYMENT],
                list(proposal.packages.all()),
            ),
            # Секцію «Рекомендації» не показуємо, якщо в ній лише гарантія, що вже є в секції 07
            'recommendation_items': visible_recommendations(
                [s for s in specs if s.kind == ProposalSpec.Kind.RECOMMENDATION],
                proposal.get_localized_guarantee_html(),
            ),
        })
        context['hero_srcset'], context['hero_wh'] = hero_responsive(proposal.hero_public_url)
        context['pay_has_amounts'] = any(i.pay_amount for i in context['payment_items'])
        context['secnum'] = section_numbers({
            'arch': bool(arch_nodes),
            'intro': bool(proposal.get_safe_intro()),
            'modules': bool(context['modules']),
            'specs': bool(context['spec_items']),
            'expert': bool(context['recommendation_items']),
            'packages': bool(context['packages']),
            'guarantee': bool(proposal.get_safe_guarantee()),
            'payment': bool(context['payment_items']),
        })
        return context
