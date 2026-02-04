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
        ('footer-consultation', _('Заявка з footer')),
        ('event_registration', _('Реєстрація на подію')),
        ('test_result', _('Результат тесту калькулятора')),
    ]
    
    # Вибір статусів
    STATUS_CHOICES = [
        ('new', _('Новий')),
        ('in_progress', _('В роботі')),
        ('thinking', _('Думає / Очікує')),
        ('no_contact', _('Не на зв\'язку')),
        ('ordered', _('Замовив сайт')),
        ('completed', _('Завершено')),
        ('rejected', _('Відмова / Архів')),
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
            'ordered': '#32CD32',       # Зелений
            'completed': '#228B22',     # Forest green (темно-зелений)
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
            'footer-consultation': 'Footer',
            'event_registration': 'Подія',
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
