"""Колекції лендінгу: послуги, галерея, до/після, відгуки, партнери."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.i18n_content import localized_text

from .models import LandingSite


class LandingOffer(models.Model):
    tenant = models.ForeignKey(
        LandingSite, on_delete=models.CASCADE, related_name='offers', verbose_name=_('Лендінг'),
    )
    title = models.CharField(max_length=200, verbose_name=_('Назва послуги'))
    title_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (RU)'))
    title_en = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (EN)'))
    title_cs = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (CS)'))
    description = models.TextField(blank=True, verbose_name=_('Опис'))
    description_ru = models.TextField(blank=True, verbose_name=_('Опис (RU)'))
    description_en = models.TextField(blank=True, verbose_name=_('Опис (EN)'))
    description_cs = models.TextField(blank=True, verbose_name=_('Опис (CS)'))
    price_from = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Ціна від'),
    )
    image = models.ImageField(upload_to='demolanding/offers/', blank=True, null=True, verbose_name=_('Фото'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Послуга')
        verbose_name_plural = _('Послуги')

    def __str__(self):
        return self.title

    @property
    def localized_title(self) -> str:
        return localized_text(self.title, self.title_ru, self.title_en, self.title_cs)

    @property
    def localized_description(self) -> str:
        return localized_text(self.description, self.description_ru, self.description_en, self.description_cs)


class LandingGalleryImage(models.Model):
    class Span(models.TextChoices):
        S1X1 = '1x1', '1×1'
        S2X1 = '2x1', '2×1'
        S1X2 = '1x2', '1×2'

    tenant = models.ForeignKey(
        LandingSite, on_delete=models.CASCADE, related_name='gallery_images', verbose_name=_('Лендінг'),
    )
    image = models.ImageField(upload_to='demolanding/gallery/', verbose_name=_('Фото'))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис'))
    caption_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис (RU)'))
    caption_en = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис (EN)'))
    caption_cs = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис (CS)'))
    span = models.CharField(max_length=6, choices=Span.choices, default=Span.S1X1, verbose_name=_('Розмір у сітці'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Фото галереї')
        verbose_name_plural = _('Галерея')

    def __str__(self):
        return self.caption or f'Photo #{self.pk}'

    @property
    def localized_caption(self) -> str:
        return localized_text(self.caption, self.caption_ru, self.caption_en, self.caption_cs)


class LandingBeforeAfter(models.Model):
    tenant = models.ForeignKey(
        LandingSite, on_delete=models.CASCADE, related_name='before_after_pairs', verbose_name=_('Лендінг'),
    )
    title = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис'))
    image_before = models.ImageField(upload_to='demolanding/before_after/', verbose_name=_('До'))
    image_after = models.ImageField(upload_to='demolanding/before_after/', verbose_name=_('Після'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('До / після')
        verbose_name_plural = _('До / після')

    def __str__(self):
        return self.title or f'Before/After #{self.pk}'


class LandingTestimonial(models.Model):
    tenant = models.ForeignKey(
        LandingSite, on_delete=models.CASCADE, related_name='testimonials', verbose_name=_('Лендінг'),
    )
    author_name = models.CharField(max_length=150, verbose_name=_('Автор'))
    role = models.CharField(max_length=150, blank=True, verbose_name=_('Роль / проєкт'))
    text = models.TextField(verbose_name=_('Текст'))
    text_ru = models.TextField(blank=True, verbose_name=_('Текст (RU)'))
    text_en = models.TextField(blank=True, verbose_name=_('Текст (EN)'))
    text_cs = models.TextField(blank=True, verbose_name=_('Текст (CS)'))
    rating = models.PositiveSmallIntegerField(default=5, verbose_name=_('Оцінка'))
    avatar = models.ImageField(upload_to='demolanding/testimonials/', blank=True, null=True, verbose_name=_('Фото'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Відгук')
        verbose_name_plural = _('Відгуки')

    def __str__(self):
        return self.author_name

    @property
    def localized_text(self) -> str:
        return localized_text(self.text, self.text_ru, self.text_en, self.text_cs)


class LandingPartner(models.Model):
    tenant = models.ForeignKey(
        LandingSite, on_delete=models.CASCADE, related_name='partners', verbose_name=_('Лендінг'),
    )
    name = models.CharField(max_length=150, verbose_name=_('Назва'))
    logo = models.ImageField(upload_to='demolanding/partners/', verbose_name=_('Лого'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Партнер')
        verbose_name_plural = _('Партнери')

    def __str__(self):
        return self.name
