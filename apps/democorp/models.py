"""Тенант demo-корпоративного сайту PrometeyLabs."""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.proposal_models import Proposal
from apps.demotenant.models_abstract import AbstractDemoTenant

DEFAULT_THEME_COLORS = {
    'color_primary': '#100D0C',
    'color_primary_hover': '#181412',
    'color_accent': '#C99A44',
    'color_surface': '#100D0C',
    'color_text': '#FCF2EE',
}

LEGACY_THEME_COLORS = {
    '#12313F', '#0D2530', '#C98A3B', '#F4EFE4', '#1A1A1A',
    '#1A3A63', '#142D4D', '#2F7BD1', '#FFFFFF',
}


class CorpSite(AbstractDemoTenant):
    class StylePreset(models.TextChoices):
        EDITORIAL = 'editorial', _('Dark luxury (bark / gold)')
        CLEAN = 'clean', _('Dark luxury (slot contrast)')

    TOKEN_MAP = {
        'color_primary': '--dc-primary',
        'color_primary_hover': '--dc-primary-hover',
        'color_accent': '--dc-accent',
        'color_surface': '--dc-surface',
        'color_text': '--dc-text',
    }
    CACHE_PREFIX = 'democorp_theme_css_v2'

    proposal = models.OneToOneField(
        Proposal,
        on_delete=models.CASCADE,
        related_name='demo_corp',
        verbose_name=_('Комерційна пропозиція'),
    )
    owner_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demo_corp',
        verbose_name=_('Клієнтський логін'),
    )
    style_preset = models.CharField(
        max_length=20, choices=StylePreset.choices, default=StylePreset.EDITORIAL, verbose_name=_('Стиль'),
    )
    has_catalog = models.BooleanField(
        default=False,
        verbose_name=_('Каталог продукції'),
        help_text=_('Без оплат/кошика — кнопка «Купити» відкриває заявку'),
    )
    hero_image = models.ImageField(
        upload_to='democorp/hero/', blank=True, null=True, verbose_name=_('Hero — фото'),
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Демо-сайт (корпоративний)')
        verbose_name_plural = _('Демо-сайти (корпоративні)')

    def get_absolute_url(self) -> str:
        from django.urls import reverse

        return reverse('democorp:home', kwargs={'slug': self.slug})


from .content_models import CorpBlock  # noqa: E402,F401
from .collection_models import (  # noqa: E402,F401
    CorpGalleryImage,
    CorpPartner,
    CorpProductionStep,
    CorpTestimonial,
)
from .catalog_models import CorpCategory, CorpProduct, CorpProductImage  # noqa: E402,F401
from .lead_models import CorpLead  # noqa: E402,F401
