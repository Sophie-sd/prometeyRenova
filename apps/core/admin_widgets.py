"""Віджети адмінки для зображень портфоліо з fallback на static."""
from unfold.widgets import UnfoldAdminImageFieldWidget


class PortfolioImageWidget(UnfoldAdminImageFieldWidget):
    """Прев’ю в адмінці: media, якщо файл є, інакше static з seed."""

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        resolved = ''
        instance = getattr(value, 'instance', None) if value else None
        if instance and getattr(instance, 'pk', None):
            from apps.core.portfolio_images import resolve_portfolio_image_url

            resolved = resolve_portfolio_image_url(instance, name)
        context['widget']['resolved_preview_url'] = resolved
        return context
