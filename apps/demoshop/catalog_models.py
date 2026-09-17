"""Каталог демо-магазину: категорії, товари, фото товару, відгуки."""
from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.i18n_content import localized_text

from .models import DemoShop


class ShopCategory(models.Model):
    shop = models.ForeignKey(
        DemoShop, on_delete=models.CASCADE, related_name='categories', verbose_name=_('Магазин'),
    )
    name = models.CharField(max_length=120, verbose_name=_('Назва'))
    name_ru = models.CharField(max_length=120, blank=True, verbose_name=_('Назва (RU)'))
    name_en = models.CharField(max_length=120, blank=True, verbose_name=_('Назва (EN)'))
    name_cs = models.CharField(max_length=120, blank=True, verbose_name=_('Назва (CS)'))
    slug = models.SlugField(max_length=140, blank=True, allow_unicode=True, verbose_name=_('Slug'))
    icon = models.CharField(max_length=8, blank=True, verbose_name=_('Іконка (emoji)'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        unique_together = ('shop', 'slug')
        ordering = ('order', 'name')
        verbose_name = _('Категорія')
        verbose_name_plural = _('Категорії')

    def __str__(self):
        return self.name

    @property
    def localized_name(self):
        return localized_text(self.name, self.name_ru, self.name_en, self.name_cs)

    def save(self, *args, **kwargs):
        if not self.slug:
            # allow_unicode=True — інакше slugify() з чисто кириличної назви
            # повертає '' і всі категорії/товари магазину зіштовхуються на
            # unique_together (shop, slug).
            self.slug = slugify(self.name, allow_unicode=True)[:140]
        super().save(*args, **kwargs)


class ShopProduct(models.Model):
    shop = models.ForeignKey(
        DemoShop, on_delete=models.CASCADE, related_name='products', verbose_name=_('Магазин'),
    )
    category = models.ForeignKey(
        ShopCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name=_('Категорія'),
    )
    name = models.CharField(max_length=200, verbose_name=_('Назва'))
    name_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (RU)'))
    name_en = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (EN)'))
    name_cs = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (CS)'))
    slug = models.SlugField(max_length=220, blank=True, allow_unicode=True, verbose_name=_('Slug'))
    short_description = models.CharField(max_length=240, blank=True, verbose_name=_('Короткий опис'))
    short_description_ru = models.CharField(max_length=240, blank=True, verbose_name=_('Короткий опис (RU)'))
    short_description_en = models.CharField(max_length=240, blank=True, verbose_name=_('Короткий опис (EN)'))
    short_description_cs = models.CharField(max_length=240, blank=True, verbose_name=_('Короткий опис (CS)'))
    description = models.TextField(blank=True, verbose_name=_('Опис'))
    description_ru = models.TextField(blank=True, verbose_name=_('Опис (RU)'))
    description_en = models.TextField(blank=True, verbose_name=_('Опис (EN)'))
    description_cs = models.TextField(blank=True, verbose_name=_('Опис (CS)'))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Ціна'))
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Стара ціна'),
    )
    sale_end_date = models.DateTimeField(
        blank=True, null=True, verbose_name=_('Кінець акції (таймер)'),
    )
    gift_promo_text = models.CharField(
        max_length=200, blank=True, verbose_name=_('Подарунок до замовлення'),
    )
    gift_promo_text_ru = models.CharField(
        max_length=200, blank=True, verbose_name=_('Подарунок до замовлення (RU)'),
    )
    gift_promo_text_en = models.CharField(
        max_length=200, blank=True, verbose_name=_('Подарунок до замовлення (EN)'),
    )
    gift_promo_text_cs = models.CharField(
        max_length=200, blank=True, verbose_name=_('Подарунок до замовлення (CS)'),
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Хіт'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))

    class Meta:
        unique_together = ('shop', 'slug')
        ordering = ('order', '-created_at')
        verbose_name = _('Товар')
        verbose_name_plural = _('Товари')

    def __str__(self):
        return self.name

    @property
    def localized_name(self):
        return localized_text(self.name, self.name_ru, self.name_en, self.name_cs)

    @property
    def localized_short_description(self):
        return localized_text(
            self.short_description, self.short_description_ru,
            self.short_description_en, self.short_description_cs,
        )

    @property
    def localized_description(self):
        return localized_text(self.description, self.description_ru, self.description_en, self.description_cs)

    @property
    def localized_gift_promo_text(self):
        return localized_text(
            self.gift_promo_text, self.gift_promo_text_ru,
            self.gift_promo_text_en, self.gift_promo_text_cs,
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'demoshop:product_detail',
            kwargs={'shop_slug': self.shop.slug, 'product_slug': self.slug},
        )

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - self.price / self.old_price) * 100)
        return None

    @property
    def sale_timer_active(self) -> bool:
        if not self.sale_end_date:
            return False
        return self.sale_end_date > timezone.now()

    @property
    def has_gift_promo(self) -> bool:
        return bool((self.gift_promo_text or '').strip())

    @property
    def main_image(self):
        return self.images.filter(is_main=True).first() or self.images.first()


class ShopProductImage(models.Model):
    product = models.ForeignKey(
        ShopProduct, on_delete=models.CASCADE, related_name='images', verbose_name=_('Товар'),
    )
    image = models.ImageField(upload_to='demoshop/products/', verbose_name=_('Фото'))
    alt = models.CharField(max_length=200, blank=True, verbose_name=_('Alt-текст'))
    is_main = models.BooleanField(default=False, verbose_name=_('Головне фото'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('-is_main', 'order', 'id')
        verbose_name = _('Фото товару')
        verbose_name_plural = _('Фото товару')

    def __str__(self):
        return self.alt or f'Image #{self.pk}'


class ShopReview(models.Model):
    shop = models.ForeignKey(
        DemoShop, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Магазин'),
    )
    product = models.ForeignKey(
        ShopProduct, on_delete=models.CASCADE, related_name='reviews',
        null=True, blank=True, verbose_name=_('Товар'),
    )
    author_name = models.CharField(max_length=120, verbose_name=_('Автор'))
    rating = models.PositiveSmallIntegerField(default=5, verbose_name=_('Оцінка'))
    text = models.TextField(blank=True, verbose_name=_('Текст'))
    is_approved = models.BooleanField(default=True, verbose_name=_('Опубліковано'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Відгук')
        verbose_name_plural = _('Відгуки')

    def __str__(self):
        return f'{self.author_name} — {self.rating}★'
