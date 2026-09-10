from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DemoshopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.demoshop'
    verbose_name = _('Демо-магазини')
