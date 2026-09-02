"""
Міксини та базові класи для оптимізації коду views
"""
from django.views.generic import TemplateView
from django.utils import timezone

from apps.core.models import Client, PortfolioProject, PortfolioFeatureBlock


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
    projects = list(
        published_portfolio_queryset()
        .filter(show_on_portfolio=True)
        .order_by('order', 'title')
    )
    for index, project in enumerate(projects):
        project.snap_index = index
        project.snap_tone = PortfolioProject.get_snap_tone(index)
        project.snap_layout = project.get_layout_modifier(index)
    return projects


def homepage_clients():
    return Client.objects.filter(is_active=True).order_by('order', 'name')


def feature_blocks():
    return PortfolioFeatureBlock.objects.filter(is_published=True).order_by('order')
