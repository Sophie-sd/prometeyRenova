from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DemotenantConfig(AppConfig):
    """Спільний фундамент для demo-тенантів (shop/corp/landing).

    Без власних моделей у БД (лише абстрактні бази + сервіси) — не потребує
    міграцій. `default_auto_field` заданий для консистентності з іншими apps.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.demotenant'
    verbose_name = _('Демо-тенанти (фундамент)')
