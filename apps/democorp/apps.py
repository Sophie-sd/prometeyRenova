from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DemocorpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.democorp'
    verbose_name = _('Демо-сайти (корпоративні)')
