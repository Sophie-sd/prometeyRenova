"""Тенант demo-лендінгу PrometeyLabs, згенерований з `Proposal`."""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.proposal_models import Proposal
from apps.demotenant.models_abstract import AbstractDemoTenant

DEFAULT_THEME_COLORS = {
    'color_primary': '#16181A',
    'color_primary_hover': '#33383C',
    'color_accent': '#DFF250',
    'color_surface': '#F7F6F4',
    'color_text': '#16181A',
}


class LandingSite(AbstractDemoTenant):
    class StylePreset(models.TextChoices):
        DARK_PREMIUM = 'dark_premium', _('Kontur+ Dark (ink canvas)')
        MIXED = 'mixed', _('Kontur+ Mixed (cream + photo hero)')
        LIGHT_MINIMAL = 'light_minimal', _('Kontur+ Light')

    class HeroMode(models.TextChoices):
        CINEMATIC = 'cinematic', _('Кінематографічне фото')
        SCROLL_VIDEO = 'scroll_video', _('Scroll-scrubbed відео')

    TOKEN_MAP = {
        'color_primary': '--dl-primary',
        'color_primary_hover': '--dl-primary-hover',
        'color_accent': '--dl-accent',
        'color_surface': '--dl-surface',
        'color_text': '--dl-text',
    }
    CACHE_PREFIX = 'demolanding_theme_css_v3'

    proposal = models.OneToOneField(
        Proposal,
        on_delete=models.CASCADE,
        related_name='demo_landing',
        verbose_name=_('Комерційна пропозиція'),
    )
    owner_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demo_landing',
        verbose_name=_('Клієнтський логін'),
    )
    style_preset = models.CharField(
        max_length=20, choices=StylePreset.choices, default=StylePreset.MIXED, verbose_name=_('Стиль'),
    )
    hero_mode = models.CharField(
        max_length=20, choices=HeroMode.choices, default=HeroMode.CINEMATIC, verbose_name=_('Режим hero'),
    )
    hero_image = models.ImageField(
        upload_to='demolanding/hero/', blank=True, null=True, verbose_name=_('Hero — фото (широке)'),
    )
    hero_image_narrow = models.ImageField(
        upload_to='demolanding/hero/', blank=True, null=True, verbose_name=_('Hero — фото (мобільне)'),
    )
    hero_video = models.FileField(
        upload_to='demolanding/hero/', blank=True, null=True, verbose_name=_('Hero — відео (scroll-video)'),
    )
    hero_poster = models.ImageField(
        upload_to='demolanding/hero/', blank=True, null=True, verbose_name=_('Hero — poster для відео'),
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Демо-лендінг')
        verbose_name_plural = _('Демо-лендінги')

    def get_absolute_url(self) -> str:
        from django.urls import reverse

        return reverse('demolanding:home', kwargs={'slug': self.slug})


from .content_models import LandingBlock  # noqa: E402,F401
from .collection_models import (  # noqa: E402,F401
    LandingBeforeAfter,
    LandingGalleryImage,
    LandingOffer,
    LandingPartner,
    LandingTestimonial,
)
from .lead_models import LandingLead  # noqa: E402,F401
