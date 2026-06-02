from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
        default='https://facebook.com/prometeylabs',
        verbose_name=_('Facebook'),
    )
    linkedin_url = models.URLField(
        default='https://linkedin.com/company/prometeylabs',
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
        return _('Контакти сайту')

    def save(self, *args, **kwargs):
        if not self.pk and SiteContactSettings.objects.exists():
            raise ValidationError(_('Дозволено лише один запис налаштувань контактів'))
        super().save(*args, **kwargs)
        cache.delete('site_contact_settings')

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete('site_contact_settings')
        return result

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
