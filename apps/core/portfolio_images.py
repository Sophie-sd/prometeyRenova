"""URL зображень портфоліо: static screens з репо, інакше media на диску."""
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static as static_url

from apps.core.portfolio_seed_data import HOME_LOGO_STATIC, IMAGE_FIELD_MAP, PORTFOLIO_PROJECTS

# Мобільний варіант повносторінкових знімків (static/images/portfolio/screens/*-desktop-720.webp).
MOBILE_SCREEN_WIDTH = 720


def _static_paths_for_slug(slug: str) -> dict[str, str]:
    for item in PORTFOLIO_PROJECTS:
        if item['slug'] == slug:
            return {
                field_name: (item.get(static_key) or '')
                for static_key, field_name in IMAGE_FIELD_MAP
            }
    return {}


def _static_file_exists(rel_path: str) -> bool:
    """Файл фізично є у static/ (джерело — завжди в репо, на відміну від staticfiles/)."""
    return (Path(settings.BASE_DIR) / 'static' / rel_path).is_file()


def resolve_static_portfolio_url(project, field_name: str) -> str:
    """URL зі static (collectstatic) — стабільно на проді без media disk.

    Перевіряє існування файлу: для проєкту без згенерованого знімку
    (сайт клієнта тимчасово недоступний під час capture_portfolio_screens)
    повертає '' замість URL на неіснуючий файл — картка рендерить плейсхолдер.
    """
    static_rel = _static_paths_for_slug(project.slug).get(field_name, '')
    if static_rel and _static_file_exists(static_rel):
        return static_url(static_rel)
    return ''


@lru_cache(maxsize=256)
def _static_image_width(rel_path: str) -> int:
    """Ширина static-зображення (читає лише заголовок файлу; кеш на процес)."""
    try:
        from PIL import Image

        with Image.open(Path(settings.BASE_DIR) / 'static' / rel_path) as img:
            return int(img.width)
    except Exception:
        return 0


def resolve_static_portfolio_srcset(project, field_name: str, width: int = MOBILE_SCREEN_WIDTH) -> str:
    """srcset для повносторінкового знімка: `<slug>-desktop-720.webp 720w, <оригінал> 1440w`.

    720w — ~2× ширини картки (358 px), тож телефони/десктоп DPR≤2 тягнуть файл
    у 3–4 рази легший без зміни вигляду (той самий знімок, пропорції ті самі —
    scroll-on-hover / ping-pong рахує ту саму висоту). Порожньо, якщо варіанта немає.
    """
    static_rel = _static_paths_for_slug(project.slug).get(field_name, '')
    if not static_rel.endswith('.webp') or not _static_file_exists(static_rel):
        return ''
    small_rel = f'{static_rel[:-len(".webp")]}-{width}.webp'
    if not _static_file_exists(small_rel):
        return ''
    full_width = _static_image_width(static_rel)
    if full_width <= width:
        return ''
    return f'{static_url(small_rel)} {width}w, {static_url(static_rel)} {full_width}w'


def resolve_portfolio_image_url(project, field_name: str) -> str:
    """Картки: static screens (collectstatic), щоб прод не показував leftover media.

    Media лише якщо static-файлу для slug немає (адмінський аплоад без seed-знімку).
    """
    static_url_value = resolve_static_portfolio_url(project, field_name)
    if static_url_value:
        return static_url_value

    field = getattr(project, field_name, None)
    if field and getattr(field, 'name', None):
        media_path = Path(settings.MEDIA_ROOT) / field.name
        if media_path.is_file():
            return field.url
    return ''


def portfolio_image_available(project, field_name: str) -> bool:
    return bool(resolve_portfolio_image_url(project, field_name))


def _static_home_for_client_name(name: str) -> str:
    """Лого клієнта для секції «Наші клієнти» — незалежно від PORTFOLIO_PROJECTS."""
    return HOME_LOGO_STATIC.get(name.strip(), '')


def resolve_client_logo_url(client) -> str:
    """Головна: спочатку static (collectstatic), потім media якщо файл є на диску."""
    static_rel = _static_home_for_client_name(client.name)
    if static_rel:
        return static_url(static_rel)

    field = getattr(client, 'logo', None)
    if field and getattr(field, 'name', None):
        media_path = Path(settings.MEDIA_ROOT) / field.name
        if media_path.is_file():
            return field.url
    return ''


def resolve_client_logo_webp_url(client, width: int) -> str:
    """Похідний WebP поруч із PNG у static/images/portfolio/ — лише якщо файл є."""
    static_rel = _static_home_for_client_name(client.name)
    if not static_rel.endswith('.png'):
        return ''
    webp_rel = f'{static_rel[:-4]}-{width}.webp'
    if _static_file_exists(webp_rel):
        return static_url(webp_rel)
    return ''
