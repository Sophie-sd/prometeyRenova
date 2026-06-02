"""
Міксини та базові класи для оптимізації коду views
"""
from django.views.generic import TemplateView
from django.utils import timezone

from apps.core.models import PortfolioProject


class BasePageView(TemplateView):
    """Базовий клас для всіх сторінок сайту"""
    page_title = ""
    meta_description = ""
    og_title = ""
    keywords = ""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': self.page_title,
            'meta_description': self.meta_description,
            'og_title': self.og_title or self.page_title,
            'keywords': self.keywords,
            'current_year': timezone.now().year,
        })
        return context


def published_portfolio_queryset():
    """Опубліковані проєкти портфоліо."""
    return PortfolioProject.objects.filter(is_published=True)


def portfolio_page_projects():
    return (
        published_portfolio_queryset()
        .filter(show_on_portfolio=True)
        .order_by('order', 'title')
    )


def homepage_portfolio_stories():
    return (
        published_portfolio_queryset()
        .filter(show_on_homepage=True)
        .order_by('home_order', 'title')
    )
