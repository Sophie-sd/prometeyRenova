"""Каталог продукції — опційний (`CorpSite.has_catalog`). Без цін до оплати:
кнопка «Купити» на PDP відкриває заявку (не кошик, не checkout).
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.i18n_content import localized_text

from .models import CorpSite


class CorpCategory(models.Model):
    tenant = models.ForeignKey(
        CorpSite, on_delete=models.CASCADE, related_name='categories', verbose_name=_('Сайт'),
    )
    name = models.CharField(max_length=150, verbose_name=_('Назва'))
    name_ru = models.CharField(max_length=150, blank=True, verbose_name=_('Назва (RU)'))
    name_en = models.CharField(max_length=150, blank=True, verbose_name=_('Назва (EN)'))
    name_cs = models.CharField(max_length=150, blank=True, verbose_name=_('Назва (CS)'))
    slug = models.SlugField(max_length=160, allow_unicode=True, verbose_name=_('Slug'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        unique_together = ('tenant', 'slug')
        ordering = ('order', 'id')
        verbose_name = _('Категорія каталогу')
        verbose_name_plural = _('Категорії каталогу')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)[:160]
        super().save(*args, **kwargs)

    @property
    def localized_name(self) -> str:
        return localized_text(self.name, self.name_ru, self.name_en, self.name_cs)


class CorpProduct(models.Model):
    tenant = models.ForeignKey(
        CorpSite, on_delete=models.CASCADE, related_name='products', verbose_name=_('Сайт'),
    )
    category = models.ForeignKey(
        CorpCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name=_('Категорія'),
    )
    name = models.CharField(max_length=200, verbose_name=_('Назва'))
    name_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (RU)'))
    name_en = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (EN)'))
    name_cs = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (CS)'))
    slug = models.SlugField(max_length=220, allow_unicode=True, verbose_name=_('Slug'))
    excerpt = models.TextField(blank=True, verbose_name=_('Короткий опис'))
    excerpt_ru = models.TextField(blank=True, verbose_name=_('Короткий опис (RU)'))
    excerpt_en = models.TextField(blank=True, verbose_name=_('Короткий опис (EN)'))
    excerpt_cs = models.TextField(blank=True, verbose_name=_('Короткий опис (CS)'))
    specs = models.TextField(blank=True, verbose_name=_('Характеристики'))
    specs_ru = models.TextField(blank=True, verbose_name=_('Характеристики (RU)'))
    specs_en = models.TextField(blank=True, verbose_name=_('Характеристики (EN)'))
    specs_cs = models.TextField(blank=True, verbose_name=_('Характеристики (CS)'))
    price_from = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Ціна від'),
    )
    is_featured = models.BooleanField(default=False, verbose_name=_('Популярний'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        unique_together = ('tenant', 'slug')
        ordering = ('order', 'id')
        verbose_name = _('Товар каталогу')
        verbose_name_plural = _('Товари каталогу')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)[:220]
        super().save(*args, **kwargs)

    @property
    def localized_name(self) -> str:
        return localized_text(self.name, self.name_ru, self.name_en, self.name_cs)

    @property
    def localized_excerpt(self) -> str:
        return localized_text(self.excerpt, self.excerpt_ru, self.excerpt_en, self.excerpt_cs)

    @property
    def localized_specs(self) -> str:
        return localized_text(self.specs, self.specs_ru, self.specs_en, self.specs_cs)


class CorpProductImage(models.Model):
    product = models.ForeignKey(
        CorpProduct, on_delete=models.CASCADE, related_name='images', verbose_name=_('Товар'),
    )
    image = models.ImageField(upload_to='democorp/products/', verbose_name=_('Фото'))
    is_main = models.BooleanField(default=False, verbose_name=_('Головне фото'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('-is_main', 'order', 'id')
        verbose_name = _('Фото товару')
        verbose_name_plural = _('Фото товару')

    def __str__(self):
        return f'{self.product_id}:{self.pk}'
