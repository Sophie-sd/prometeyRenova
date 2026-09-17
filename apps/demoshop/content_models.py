"""CMS-контент демо-магазину: тексти/фото по секціях + hero-слайди.

Реєстр ключів — `block_defaults.BLOCK_REGISTRY`. Ці моделі НЕ мають окремого
CRUD ModelAdmin (admin_cms_blocks_skill §14) — редагування лише через проксі
«Мій магазин» у `content_admin.py`.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.i18n_content import localized_text

from .models import DemoShop


class ShopBlock(models.Model):
    class BlockType(models.TextChoices):
        TEXT = 'text', _('Текст')
        IMAGE = 'image', _('Зображення')

    shop = models.ForeignKey(
        DemoShop, on_delete=models.CASCADE, related_name='blocks', verbose_name=_('Магазин'),
    )
    page = models.CharField(max_length=40, db_index=True, verbose_name=_('Сторінка'))
    key = models.CharField(max_length=60, verbose_name=_('Ключ'))
    block_type = models.CharField(
        max_length=10, choices=BlockType.choices, default=BlockType.TEXT, verbose_name=_('Тип'),
    )
    label = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис для адмінки'))
    value_text = models.TextField(blank=True, verbose_name=_('Текст'))
    value_text_ru = models.TextField(blank=True, verbose_name=_('Текст (RU)'))
    value_text_en = models.TextField(blank=True, verbose_name=_('Текст (EN)'))
    value_text_cs = models.TextField(blank=True, verbose_name=_('Текст (CS)'))
    value_image = models.ImageField(
        upload_to='demoshop/blocks/', blank=True, null=True, verbose_name=_('Зображення'),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        unique_together = ('shop', 'page', 'key')
        ordering = ('page', 'order', 'id')
        verbose_name = _('Блок контенту')
        verbose_name_plural = _('Блоки контенту')

    def __str__(self):
        return f'{self.shop_id}:{self.page}:{self.key}'

    @property
    def localized_value(self):
        return localized_text(self.value_text, self.value_text_ru, self.value_text_en, self.value_text_cs)


class ShopHeroSlide(models.Model):
    shop = models.ForeignKey(
        DemoShop, on_delete=models.CASCADE, related_name='hero_slides', verbose_name=_('Магазин'),
    )
    image = models.ImageField(upload_to='demoshop/hero/', verbose_name=_('Фото (широке)'))
    image_narrow = models.ImageField(
        upload_to='demoshop/hero/', blank=True, verbose_name=_('Фото (вузьке / мобільне)'),
    )
    title = models.CharField(max_length=200, blank=True, verbose_name=_('Заголовок'))
    title_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Заголовок (RU)'))
    title_en = models.CharField(max_length=200, blank=True, verbose_name=_('Заголовок (EN)'))
    title_cs = models.CharField(max_length=200, blank=True, verbose_name=_('Заголовок (CS)'))
    subtitle = models.CharField(max_length=300, blank=True, verbose_name=_('Підзаголовок'))
    subtitle_ru = models.CharField(max_length=300, blank=True, verbose_name=_('Підзаголовок (RU)'))
    subtitle_en = models.CharField(max_length=300, blank=True, verbose_name=_('Підзаголовок (EN)'))
    subtitle_cs = models.CharField(max_length=300, blank=True, verbose_name=_('Підзаголовок (CS)'))
    cta_label = models.CharField(max_length=80, blank=True, verbose_name=_('Текст кнопки'))
    cta_label_ru = models.CharField(max_length=80, blank=True, verbose_name=_('Текст кнопки (RU)'))
    cta_label_en = models.CharField(max_length=80, blank=True, verbose_name=_('Текст кнопки (EN)'))
    cta_label_cs = models.CharField(max_length=80, blank=True, verbose_name=_('Текст кнопки (CS)'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Слайд головної')
        verbose_name_plural = _('Слайди головної')

    def __str__(self):
        return self.title or f'Slide #{self.pk}'

    @property
    def localized_title(self):
        return localized_text(self.title, self.title_ru, self.title_en, self.title_cs)

    @property
    def localized_subtitle(self):
        return localized_text(self.subtitle, self.subtitle_ru, self.subtitle_en, self.subtitle_cs)

    @property
    def localized_cta_label(self):
        return localized_text(self.cta_label, self.cta_label_ru, self.cta_label_en, self.cta_label_cs)
