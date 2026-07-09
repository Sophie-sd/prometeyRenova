from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


class FormSubmission(models.Model):
    """Модель для збереження всіх заявок з сайту"""
    
    # Вибір типів форм
    FORM_TYPE_CHOICES = [
        ('manual', _('Ручна заявка')),
        ('site-request', _('Заявка на розробку сайту')),
        ('developer', _('Заявка на курси')),
        ('consultation', _('Заявка на консультацію')),
        ('contact', _('Заявка зі сторінки контактів')),
        ('call-request', _('Замовлення дзвінка')),
        ('footer-consultation', _('Заявка з футера')),
        ('test_result', _('Результат тесту калькулятора')),
    ]
    
    # Вибір статусів
    STATUS_CHOICES = [
        ('new', _('Новий')),
        ('in_progress', _('В роботі')),
        ('thinking', _('Думає / Очікує')),
        ('no_contact', _('Не на зв\'язку')),
        ('back_to_applications', _('Назад в заявки')),
        ('completed', _('Завершено')),
        ('pause', _('Пауза')),
        ('rejected', _('Архів заявок')),
    ]
    
    # Вибір пріоритету
    PRIORITY_CHOICES = [
        ('low', _('Низький')),
        ('normal', _('Нормальний')),
        ('high', _('Високий')),
    ]
    
    # ===== КОНТАКТНІ ДАНІ =====
    name = models.CharField(max_length=200, verbose_name=_('Ім\'я'))
    phone = models.CharField(max_length=20, verbose_name=_('Телефон'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    messenger_link = models.URLField(blank=True, verbose_name=_('Посилання на месенджер'))
    project = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name=_('Проект'),
        help_text=_('Короткий опис проекту для швидкого огляду в списку')
    )
    
    # ===== ДЖЕРЕЛО ТА КЛАСИФІКАЦІЯ =====
    form_type = models.CharField(
        max_length=30, 
        choices=FORM_TYPE_CHOICES, 
        default='manual',
        verbose_name=_('Тип форми'),
        db_index=True
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name=_('Статус'),
        db_index=True
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='normal',
        verbose_name=_('Пріоритет')
    )
    
    # ===== ДЕТАЛІ ЗАПИТУ =====
    details = models.TextField(blank=True, verbose_name=_('Деталі / Повідомлення'))
    extra_data = models.JSONField(blank=True, null=True, verbose_name=_('Додаткові дані'))
    
    # ===== EMAIL ВІДПРАВКА =====
    email_sent = models.BooleanField(
        default=False, 
        db_index=True,
        verbose_name=_('Email відправлено')
    )
    email_sent_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_('Час відправки email')
    )
    
    # ===== СИСТЕМНІ ПОЛЯ =====
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Створено'),
        db_index=True
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))
    ip_address = models.GenericIPAddressField(
        blank=True, 
        null=True, 
        verbose_name=_('IP адреса')
    )
    user_agent = models.TextField(blank=True, verbose_name=_('User Agent'))
    
    # ===== GOOGLE ADS TRACKING =====
    gclid = models.CharField(
        max_length=255, blank=True,
        verbose_name=_('Google Click ID')
    )
    utm_source = models.CharField(max_length=255, blank=True, verbose_name=_('UTM Source'))
    utm_medium = models.CharField(max_length=255, blank=True, verbose_name=_('UTM Medium'))
    utm_campaign = models.CharField(max_length=255, blank=True, verbose_name=_('UTM Campaign'))
    utm_term = models.CharField(max_length=255, blank=True, verbose_name=_('UTM Term'))
    utm_content = models.CharField(max_length=255, blank=True, verbose_name=_('UTM Content'))
    
    # ===== KEYCRM ІНТЕГРАЦІЯ =====
    keycrm_card_id = models.IntegerField(
        null=True, blank=True, db_index=True,
        verbose_name=_('KeyCRM Card ID')
    )
    keycrm_synced = models.BooleanField(
        default=False,
        verbose_name=_('Синхронізовано з KeyCRM')
    )
    
    # ===== МЕНЕДЖМЕНТ =====
    manager_comment = models.TextField(
        blank=True, 
        verbose_name=_('Коментар менеджера')
    )
    assigned_to = models.ForeignKey(
        User, 
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL,
        verbose_name=_('Призначено')
    )
    
    class Meta:
        verbose_name = _('Заявка')
        verbose_name_plural = _('Заявки')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['form_type']),
            models.Index(fields=['created_at', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_form_type_display()} ({self.get_status_display()})"
    
    def get_status_color(self):
        """Повертає колір для статусу"""
        colors = {
            'new': '#FFD700',           # Яскраво-жовтий
            'in_progress': '#1E90FF',   # Блакитний
            'thinking': '#9370DB',      # Фіолетовий
            'no_contact': '#FF8C00',    # Оранжевий
            'back_to_applications': '#FF8C00',  # Оранжевий (як no_contact)
            'completed': '#228B22',     # Forest green (темно-зелений)
            'pause': '#9370DB',         # Фіолетовий (як thinking)
            'rejected': '#696969'       # Темно-сірий
        }
        return colors.get(self.status, '#999999')
    
    def time_since_created(self):
        """Повертає час з моменту створення у форматованому вигляді"""
        delta = timezone.now() - self.created_at
        
        if delta.days > 0:
            return _('%(days)d днів') % {'days': delta.days}
        
        hours = delta.seconds // 3600
        if hours > 0:
            return _('%(hours)d годин') % {'hours': hours}
        
        minutes = (delta.seconds % 3600) // 60
        if minutes > 0:
            return _('%(minutes)d хвилин') % {'minutes': minutes}
        
        return _('щойно')
    
    def is_urgent(self):
        """Чи критична заявка (>24 години в статусі 'new')"""
        if self.status != 'new':
            return False
        
        time_passed = timezone.now() - self.created_at
        return time_passed > timedelta(hours=24)
    
    def get_form_type_display_uk(self):
        """Більш короткий вивід типу форми для таблиці"""
        display_map = {
            'manual': 'Ручна',
            'site-request': 'Сайт',
            'developer': 'Курси',
            'consultation': 'Консультація',
            'contact': 'Контакт',
            'call-request': 'Дзвінок',
            'footer-consultation': 'Футер',
            'test_result': 'Тест',
        }
        return display_map.get(self.form_type, self.get_form_type_display())


class ArchivedFormSubmission(FormSubmission):
    """Proxy-модель для відображення архівованих заявок (status=rejected)"""
    class Meta:
        proxy = True
        verbose_name = _('Архівна заявка')
        verbose_name_plural = _('Архів заявок')


class InProgressFormSubmission(FormSubmission):
    """Proxy-модель для заявок у статусі «В роботі»"""
    class Meta:
        proxy = True
        verbose_name = _('Заявка в роботі')
        verbose_name_plural = _('В роботі')


class CompletedFormSubmission(FormSubmission):
    """Proxy-модель для завершених заявок"""
    class Meta:
        proxy = True
        verbose_name = _('Завершена заявка')
        verbose_name_plural = _('Завершено')


class Employee(models.Model):
    """Модель співробітника для відображення в блоці 'Аутентифікація та авторизація'"""
    
    # ===== ОСОБИСТІ ДАНІ =====
    last_name = models.CharField(
        max_length=100,
        verbose_name=_('Прізвище')
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name=_('Ім\'я')
    )
    patronymic = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('По батькові')
    )
    
    # ===== ПОСАДОВІ ДАНІ =====
    position = models.CharField(
        max_length=200,
        verbose_name=_('Посада')
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Дата прийому на роботу')
    )
    
    # ===== КОНТАКТНА ІНФОРМАЦІЯ =====
    email = models.EmailField(
        blank=True,
        verbose_name=_('Email')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Телефон')
    )
    
    # ===== ОПИСОВА ІНФОРМАЦІЯ =====
    bio = models.TextField(
        blank=True,
        verbose_name=_('Короткий опис / Біо')
    )
    
    # ===== СТАТУС ТА ПОРЯДОК =====
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активний'),
        db_index=True
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок відображення'),
        db_index=True
    )
    
    # ===== СИСТЕМНІ ПОЛЯ =====
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Створено')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Оновлено')
    )
    
    class Meta:
        # app_label = 'auth' — щоб модель з'являлася в блоці "Аутентифікація та авторизація"
        app_label = 'auth'
        db_table = 'auth_employee'
        verbose_name = _('Співробітник')
        verbose_name_plural = _('Співробітники')
        ordering = ['order', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['order', 'is_active']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        """Представлення як Прізвище Ім'я По батькові"""
        full_name = f"{self.last_name} {self.first_name}"
        if self.patronymic:
            full_name += f" {self.patronymic}"
        return full_name
    
    def get_full_name(self):
        """Повертає повне ім'я"""
        return str(self)


class SiteContactSettings(models.Model):
    """Singleton: контакти сайту та точка на Google Maps."""

    phone_display = models.CharField(
        max_length=32,
        default='+38 (063) 952-05-65',
        verbose_name=_('Телефон (відображення)'),
    )
    phone_e164 = models.CharField(
        max_length=20,
        default='380639520565',
        verbose_name=_('Телефон (цифри для посилань)'),
        help_text=_('Без +, наприклад 380639520565'),
    )
    email = models.EmailField(
        default='prometeylabs@gmail.com',
        verbose_name=_('Email'),
    )
    instagram_url = models.URLField(
        default='https://instagram.com/prometeylabs',
        verbose_name=_('Instagram'),
    )
    facebook_url = models.URLField(
        default='https://www.facebook.com/profile.php?id=61577585882254',
        verbose_name=_('Facebook'),
    )
    linkedin_url = models.URLField(
        default='https://www.linkedin.com/in/sofia-dmitrenko',
        verbose_name=_('LinkedIn'),
    )
    telegram_url = models.URLField(
        default='https://t.me/prometeylabs',
        verbose_name=_('Telegram'),
    )
    whatsapp_url = models.URLField(
        blank=True,
        verbose_name=_('WhatsApp (опційно)'),
        help_text=_('Якщо порожньо — генерується з телефону'),
    )
    viber_url = models.URLField(
        blank=True,
        verbose_name=_('Viber (опційно)'),
        help_text=_('Якщо порожньо — генерується з телефону'),
    )
    tiktok_url = models.URLField(
        blank=True,
        default='https://tiktok.com/@prometeylabs',
        verbose_name=_('TikTok'),
    )
    address = models.CharField(
        max_length=255,
        default='Київ, бульвар Тараса Шевченка 46а',
        verbose_name=_('Адреса'),
    )
    maps_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Широта (Google Maps)'),
    )
    maps_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Довгота (Google Maps)'),
    )
    maps_zoom = models.PositiveSmallIntegerField(
        default=15,
        verbose_name=_('Масштаб карти'),
    )
    google_maps_embed_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('URL вбудованої карти (iframe src)'),
        help_text=_(
            'Повний src з Google Maps «Поділитися → Вбудувати». '
            'Має пріоритет над координатами.'
        ),
    )

    class Meta:
        verbose_name = _('Контакти та карта')
        verbose_name_plural = _('Контакти та карта')

    def __str__(self):
        return str(_('Контакти сайту'))

    def save(self, *args, **kwargs):
        if not self.pk and SiteContactSettings.objects.exists():
            raise ValidationError(_('Дозволено лише один запис налаштувань контактів'))
        super().save(*args, **kwargs)
        cache.delete('site_contact_settings')

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete('site_contact_settings')
        return result

    def get_localized_address(self):
        if not self.address:
            return ''
        return gettext(self.address)

    def get_tel_href(self):
        digits = (self.phone_e164 or '').strip()
        return f'tel:+{digits}' if digits else ''

    def get_whatsapp_href(self):
        if self.whatsapp_url:
            return self.whatsapp_url
        digits = (self.phone_e164 or '').strip()
        return f'https://wa.me/{digits}' if digits else ''

    def get_viber_href(self):
        if self.viber_url:
            return self.viber_url
        digits = (self.phone_e164 or '').strip()
        return f'viber://add?number={digits}' if digits else ''

    def get_maps_embed_src(self):
        embed = (self.google_maps_embed_url or '').strip()
        if embed:
            return embed
        if self.maps_latitude is not None and self.maps_longitude is not None:
            lat = self.maps_latitude
            lng = self.maps_longitude
            zoom = self.maps_zoom or 15
            return (
                f'https://www.google.com/maps?q={lat},{lng}&hl=uk&z={zoom}&output=embed'
            )
        return ''


def portfolio_upload_to(instance, filename: str) -> str:
    """Шлях завантаження зображень портфоліо."""
    return f'portfolio/{instance.slug}/{filename}'


class PortfolioProject(models.Model):
    """Проєкт портфоліо для сторінки /portfolio/ та блоку на головній."""

    slug = models.SlugField(max_length=120, unique=True, verbose_name=_('Slug'))
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    subtitle = models.CharField(max_length=200, blank=True, verbose_name=_('Підзаголовок'))
    card_description = models.TextField(verbose_name=_('Короткий опис (картка)'))
    integrations = models.TextField(
        blank=True,
        verbose_name=_('Теги інтеграцій'),
        help_text=_('Один тег на рядок (без #)'),
    )
    card_image = models.ImageField(
        upload_to=portfolio_upload_to,
        verbose_name=_('Зображення картки (desktop)'),
    )
    card_image_mobile = models.ImageField(
        upload_to=portfolio_upload_to,
        blank=True,
        verbose_name=_('Зображення картки (mobile)'),
    )
    card_image_alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Alt текст картки'),
    )
    home_story_image = models.ImageField(
        upload_to=portfolio_upload_to,
        blank=True,
        verbose_name=_('Зображення для головної (stories)'),
    )
    home_story_label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Назва на головній'),
        help_text=_('Якщо порожньо — використовується заголовок'),
    )
    modal_content = models.TextField(
        blank=True,
        verbose_name=_('Контент модального вікна (HTML)'),
    )
    title_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Заголовок (RU)'))
    subtitle_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Підзаголовок (RU)'))
    card_description_ru = models.TextField(blank=True, verbose_name=_('Короткий опис (картка) (RU)'))
    modal_content_ru = models.TextField(blank=True, verbose_name=_('Контент модального вікна (HTML) (RU)'))
    home_story_label_ru = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Назва на головній (RU)'),
    )
    card_image_alt_ru = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Alt текст картки (RU)'),
    )
    modal_hero = models.ImageField(
        upload_to=portfolio_upload_to,
        blank=True,
        verbose_name=_('Модалка: головне зображення'),
    )
    modal_mobile = models.ImageField(
        upload_to=portfolio_upload_to,
        blank=True,
        verbose_name=_('Модалка: мобільна версія'),
    )
    modal_tablet = models.ImageField(
        upload_to=portfolio_upload_to,
        blank=True,
        verbose_name=_('Модалка: планшетна версія'),
    )
    modal_laptop = models.ImageField(
        upload_to=portfolio_upload_to,
        blank=True,
        verbose_name=_('Модалка: десктопна версія'),
    )
    is_published = models.BooleanField(default=True, verbose_name=_('Опубліковано'))
    show_on_portfolio = models.BooleanField(
        default=False,
        verbose_name=_('Показувати на /portfolio/'),
    )
    show_on_homepage = models.BooleanField(
        default=False,
        verbose_name=_('Показувати на головній'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок на /portfolio/'),
    )
    home_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок на головній'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))

    class Meta:
        db_table = 'core_portfolio_project'
        ordering = ['order', 'title']
        verbose_name = _('Проєкт портфоліо')
        verbose_name_plural = _('Проєкти портфоліо')
        indexes = [
            models.Index(fields=['is_published', 'order']),
            models.Index(fields=['show_on_portfolio', 'is_published']),
            models.Index(fields=['show_on_homepage', 'is_published']),
        ]

    def __str__(self) -> str:
        return self.title

    def get_modal_id(self) -> str:
        return f'project-{self.slug}-modal'

    def get_layout_modifier(self) -> str:
        if self.order % 2 == 0:
            return 'project-card--image-left'
        return 'project-card--image-right'

    def get_integration_tags(self) -> list[str]:
        if not self.integrations:
            return []
        return [line.strip() for line in self.integrations.splitlines() if line.strip()]

    def get_safe_modal_content(self) -> str:
        from .portfolio_sanitize import linkify_portfolio_html

        return linkify_portfolio_html(self.get_localized_modal_content())

    def get_localized_title(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.title, self.title_ru)

    def get_localized_subtitle(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.subtitle, self.subtitle_ru)

    def get_localized_card_description(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.card_description, self.card_description_ru)

    def get_localized_modal_content(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.modal_content, self.modal_content_ru)

    def get_home_image(self):
        if self.home_story_image:
            return self.home_story_image
        return self.card_image

    def get_home_image_src(self) -> str:
        """Головна: спочатку static (завжди на collectstatic), потім media."""
        from .portfolio_images import (
            resolve_portfolio_image_url,
            resolve_static_portfolio_url,
        )

        for field_name in ('home_story_image', 'card_image'):
            src = resolve_static_portfolio_url(self, field_name)
            if src:
                return src
        return (
            resolve_portfolio_image_url(self, 'home_story_image')
            or resolve_portfolio_image_url(self, 'card_image')
        )

    def get_card_image_src(self) -> str:
        from .portfolio_images import resolve_portfolio_image_url

        return resolve_portfolio_image_url(self, 'card_image')

    def get_card_image_mobile_src(self) -> str:
        from .portfolio_images import resolve_portfolio_image_url

        return resolve_portfolio_image_url(self, 'card_image_mobile')

    def get_modal_hero_src(self) -> str:
        from .portfolio_images import resolve_portfolio_image_url

        return resolve_portfolio_image_url(self, 'modal_hero')

    def get_modal_mobile_src(self) -> str:
        from .portfolio_images import resolve_portfolio_image_url

        return resolve_portfolio_image_url(self, 'modal_mobile')

    def get_modal_tablet_src(self) -> str:
        from .portfolio_images import resolve_portfolio_image_url

        return resolve_portfolio_image_url(self, 'modal_tablet')

    def get_modal_laptop_src(self) -> str:
        from .portfolio_images import resolve_portfolio_image_url

        return resolve_portfolio_image_url(self, 'modal_laptop')

    def has_card_image_mobile(self) -> bool:
        from .portfolio_images import portfolio_image_available

        return portfolio_image_available(self, 'card_image_mobile')

    def has_modal_hero(self) -> bool:
        from .portfolio_images import portfolio_image_available

        return portfolio_image_available(self, 'modal_hero')

    def has_modal_mobile(self) -> bool:
        from .portfolio_images import portfolio_image_available

        return portfolio_image_available(self, 'modal_mobile')

    def has_modal_tablet(self) -> bool:
        from .portfolio_images import portfolio_image_available

        return portfolio_image_available(self, 'modal_tablet')

    def has_modal_laptop(self) -> bool:
        from .portfolio_images import portfolio_image_available

        return portfolio_image_available(self, 'modal_laptop')

    def get_home_label(self) -> str:
        from .i18n_content import localized_text

        ua = (self.home_story_label or self.title).strip()
        ru = (self.home_story_label_ru or self.title_ru).strip()
        return localized_text(ua, ru)

    def get_card_alt(self) -> str:
        from .i18n_content import localized_text

        ua = (self.card_image_alt or self.title).strip()
        ru = (self.card_image_alt_ru or self.title_ru).strip()
        return localized_text(ua, ru)

    def get_modal_title(self) -> str:
        title = self.get_localized_title()
        subtitle = self.get_localized_subtitle()
        if subtitle:
            return f'{title} — {subtitle}'
        return title


class Client(models.Model):
    """Клієнт для секції «Наші клієнти» на головній сторінці."""

    name = models.CharField(max_length=100, verbose_name=_('Назва'))
    logo = models.ImageField(upload_to='clients/', verbose_name=_('Логотип'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))
    is_active = models.BooleanField(default=True, verbose_name=_('Показувати на головній'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))

    class Meta:
        db_table = 'core_client'
        ordering = ['order', 'name']
        verbose_name = _('Клієнт')
        verbose_name_plural = _('Клієнти')
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self) -> str:
        return self.name

    def get_logo_url(self) -> str:
        from .portfolio_images import resolve_client_logo_url

        return resolve_client_logo_url(self)
