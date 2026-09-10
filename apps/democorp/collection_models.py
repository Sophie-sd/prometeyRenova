"""Колекції корпоративного сайту: етапи роботи, галерея, відгуки, партнери."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.i18n_content import localized_text

from .models import CorpSite


class CorpProductionStep(models.Model):
    tenant = models.ForeignKey(
        CorpSite, on_delete=models.CASCADE, related_name='production_steps', verbose_name=_('Сайт'),
    )
    title = models.CharField(max_length=200, verbose_name=_('Назва етапу'))
    title_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (RU)'))
    title_en = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (EN)'))
    title_cs = models.CharField(max_length=200, blank=True, verbose_name=_('Назва (CS)'))
    description = models.TextField(blank=True, verbose_name=_('Опис'))
    description_ru = models.TextField(blank=True, verbose_name=_('Опис (RU)'))
    description_en = models.TextField(blank=True, verbose_name=_('Опис (EN)'))
    description_cs = models.TextField(blank=True, verbose_name=_('Опис (CS)'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Етап роботи')
        verbose_name_plural = _('Етапи роботи')

    def __str__(self):
        return self.title

    @property
    def localized_title(self) -> str:
        return localized_text(self.title, self.title_ru, self.title_en, self.title_cs)

    @property
    def localized_description(self) -> str:
        return localized_text(self.description, self.description_ru, self.description_en, self.description_cs)


class CorpGalleryImage(models.Model):
    class Kind(models.TextChoices):
        PRODUCTION = 'production', _('Приклади')
        CERTIFICATE = 'certificate', _('Ще екрани')

    tenant = models.ForeignKey(
        CorpSite, on_delete=models.CASCADE, related_name='gallery_images', verbose_name=_('Сайт'),
    )
    image = models.ImageField(upload_to='democorp/gallery/', verbose_name=_('Фото'))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис'))
    caption_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис (RU)'))
    caption_en = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис (EN)'))
    caption_cs = models.CharField(max_length=200, blank=True, verbose_name=_('Підпис (CS)'))
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.PRODUCTION, verbose_name=_('Тип'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('kind', 'order', 'id')
        verbose_name = _('Фото галереї')
        verbose_name_plural = _('Галерея / сертифікати')

    def __str__(self):
        return self.caption or f'Photo #{self.pk}'

    @property
    def localized_caption(self) -> str:
        return localized_text(self.caption, self.caption_ru, self.caption_en, self.caption_cs)


class CorpTestimonial(models.Model):
    tenant = models.ForeignKey(
        CorpSite, on_delete=models.CASCADE, related_name='testimonials', verbose_name=_('Сайт'),
    )
    author_name = models.CharField(max_length=150, verbose_name=_('Автор'))
    role = models.CharField(max_length=150, blank=True, verbose_name=_('Роль / компанія'))
    text = models.TextField(verbose_name=_('Текст'))
    text_ru = models.TextField(blank=True, verbose_name=_('Текст (RU)'))
    text_en = models.TextField(blank=True, verbose_name=_('Текст (EN)'))
    text_cs = models.TextField(blank=True, verbose_name=_('Текст (CS)'))
    rating = models.PositiveSmallIntegerField(default=5, verbose_name=_('Оцінка'))
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


class CorpPartner(models.Model):
    tenant = models.ForeignKey(
        CorpSite, on_delete=models.CASCADE, related_name='partners', verbose_name=_('Сайт'),
    )
    name = models.CharField(max_length=150, verbose_name=_('Назва'))
    logo = models.ImageField(upload_to='democorp/partners/', verbose_name=_('Лого'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Партнер')
        verbose_name_plural = _('Партнери')

    def __str__(self):
        return self.name
