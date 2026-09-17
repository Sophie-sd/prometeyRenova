"""CMS-блок лендінгу. Реєстр ключів — `block_defaults.BLOCK_REGISTRY`.

НЕ має окремого CRUD ModelAdmin (admin_cms_blocks_skill §14) — редагування
лише через проксі «Мій лендінг» у `content_admin.py`.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.demotenant.models_abstract import AbstractTenantBlock

from .models import LandingSite


class LandingBlock(AbstractTenantBlock):
    tenant = models.ForeignKey(
        LandingSite, on_delete=models.CASCADE, related_name='blocks', verbose_name=_('Лендінг'),
    )
    value_image = models.ImageField(
        upload_to='demolanding/blocks/', blank=True, null=True, verbose_name=_('Зображення'),
    )

    class Meta:
        unique_together = ('tenant', 'page', 'key')
        ordering = ('page', 'order', 'id')
        verbose_name = _('Блок контенту')
        verbose_name_plural = _('Блоки контенту')
