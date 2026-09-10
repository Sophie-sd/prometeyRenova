"""Абстрактні бази для demo-тенантів (shop/corp/landing).

Мультитенантність — на рівні даних, як `apps.demoshop.models.DemoShop`:
одна статика/код, ізоляція через FK на тенанта. Конкретний клас додає
`proposal`/`owner_user` (OneToOneField з власним `related_name` —
`demo_shop`/`demo_corp`/`demo_landing`, щоб не конфліктувати між типами)
і власний `TOKEN_MAP`/`CACHE_PREFIX` (різні CSS-префікси `--ds-`/`--dc-`/`--dl-`).
"""
from __future__ import annotations

import secrets

from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r'^#[0-9A-Fa-f]{6}$',
    message=_('Формат кольору: #RRGGBB'),
)


class AbstractDemoTenant(models.Model):
    """Один тенант (магазин/сайт/лендінг), згенерований з `Proposal`."""

    #: Перевизначити в конкретній моделі: {field_name: css_custom_property}.
    TOKEN_MAP: dict[str, str] = {}
    #: Префікс cache-ключа theme.css — унікальний на кожен тип тенанта.
    CACHE_PREFIX: str = 'demotenant_theme_css_v1'

    slug = models.SlugField(
        max_length=160,
        unique=True,
        allow_unicode=True,
        verbose_name=_('Slug'),
    )
    name = models.CharField(max_length=200, verbose_name=_('Назва'))
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Активний'),
        help_text=_('Вимкнено — вітрина й адмінка клієнта повертають 404'),
    )
    demo_login = models.CharField(max_length=150, blank=True, verbose_name=_('Логін (демо)'))
    demo_password = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('Пароль (демо)'),
        help_text=_('Показується лише в цій адмінці — для передачі клієнту'),
    )
    color_primary = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Основний колір'), help_text=_('Hex, напр. #D6CEC7. Порожньо = дефолт'),
    )
    color_primary_hover = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Основний колір (hover)'),
    )
    color_accent = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Акцентний колір'),
    )
    color_surface = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Фон секцій'),
    )
    color_text = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Колір тексту'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Клієнт міняє колір/налаштування → theme.css має віддати нове значення
        # відразу, тому кеш інвалідується на кожен save(), а не за TTL.
        cache.delete(self.theme_cache_key())

    def theme_cache_key(self) -> str:
        return f'{self.CACHE_PREFIX}:{self.pk}'

    @classmethod
    def generate_slug(cls, base: str) -> str:
        stem = slugify(base, allow_unicode=True)[:120] or 'site'
        return f'{stem}-{secrets.token_hex(3)}'

    @staticmethod
    def generate_password() -> str:
        return secrets.token_urlsafe(9)


class AbstractTenantBlock(models.Model):
    """CMS-блок (текст/фото) секції тенанта. Реєстр ключів — `registry.py`.

    НЕ має окремого CRUD ModelAdmin (admin_cms_blocks_skill §14) — редагування
    лише через `TenantContentAdminBase`-проксі конкретного тенанта.
    """

    class BlockType(models.TextChoices):
        TEXT = 'text', _('Текст')
        IMAGE = 'image', _('Зображення')
        BOOL = 'bool', _('Перемикач (видимість секції)')

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
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        abstract = True
        ordering = ('page', 'order', 'id')

    def __str__(self):
        return f'{self.page}:{self.key}'

    @property
    def localized_value(self) -> str:
        from apps.core.i18n_content import localized_text

        return localized_text(self.value_text, self.value_text_ru, self.value_text_en, self.value_text_cs)
