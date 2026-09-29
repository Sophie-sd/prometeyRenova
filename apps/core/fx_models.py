"""Єдиний курс: скільки одиниць валюти за 1 євро."""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExchangeRateSettings(models.Model):
    uah_per_eur = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('Гривень за 1 €'),
        help_text=_('Нуль ховає кнопку гривні на сайті.'),
    )
    usd_per_eur = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('Доларів за 1 €'),
        help_text=_('Нуль ховає кнопку долара на сайті.'),
    )
    czk_per_eur = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('Крон за 1 €'),
        help_text=_('Нуль ховає кнопку крони на сайті.'),
    )

    class Meta:
        verbose_name = _('Курс валют')
        verbose_name_plural = _('Курс валют')

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return str(_('Курс валют'))
