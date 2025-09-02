"""
Міксини та базові класи для оптимізації коду views
"""
from django.views.generic import TemplateView
from django.utils import timezone


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
