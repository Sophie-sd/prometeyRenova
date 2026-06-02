"""URL зображень портфоліо: media, якщо файл є на диску, інакше static fallback."""
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static as static_url

from apps.core.portfolio_seed_data import IMAGE_FIELD_MAP, PORTFOLIO_PROJECTS


def _static_paths_for_slug(slug: str) -> dict[str, str]:
    for item in PORTFOLIO_PROJECTS:
        if item['slug'] == slug:
            return {
                field_name: (item.get(static_key) or '')
                for static_key, field_name in IMAGE_FIELD_MAP
            }
    return {}


def resolve_static_portfolio_url(project, field_name: str) -> str:
    """URL зі static (collectstatic) — стабільно на проді без media disk."""
    static_rel = _static_paths_for_slug(project.slug).get(field_name, '')
    if static_rel:
        return static_url(static_rel)
    return ''


def resolve_portfolio_image_url(project, field_name: str) -> str:
    """Повертає URL зображення або порожній рядок."""
    field = getattr(project, field_name, None)
    if field and getattr(field, 'name', None):
        media_path = Path(settings.MEDIA_ROOT) / field.name
        if media_path.is_file():
            return field.url

    return resolve_static_portfolio_url(project, field_name)


def portfolio_image_available(project, field_name: str) -> bool:
    return bool(resolve_portfolio_image_url(project, field_name))
