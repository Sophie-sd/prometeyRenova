"""Заявка з лід-форми корпоративного сайту, опційно привʼязана до товару
(«Купити» на каталозі — не кошик, а заявка з підставленим товаром)."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .catalog_models import CorpProduct
from .models import CorpSite


class CorpLead(models.Model):
    tenant = models.ForeignKey(
        CorpSite, on_delete=models.CASCADE, related_name='leads', verbose_name=_('Сайт'),
    )
    product = models.ForeignKey(
        CorpProduct, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='leads', verbose_name=_('Товар (якщо «Купити»)'),
    )
    name = models.CharField(max_length=150, verbose_name=_('Імʼя'))
    phone = models.CharField(max_length=40, blank=True, verbose_name=_('Телефон'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    message = models.TextField(blank=True, verbose_name=_('Повідомлення'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    is_read = models.BooleanField(default=False, verbose_name=_('Прочитано'))

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Заявка')
        verbose_name_plural = _('Заявки')

    def __str__(self):
        return f'{self.name} · {self.created_at:%d.%m.%Y}'
