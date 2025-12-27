from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EventCategory(models.Model):
    """Категорії подій"""
    name = models.CharField(max_length=100, verbose_name=_("Назва категорії"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("URL"))
    color = models.CharField(max_length=7, default="#E65100", verbose_name=_("Колір категорії"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Іконка"))
    
    class Meta:
        verbose_name = _("Категорія подій")
        verbose_name_plural = _("Категорії подій")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Event(models.Model):
    """Модель події"""
    EVENT_TYPES = [
        ('webinar', _('Вебінар')),
        ('discount', _('Знижка')),
        ('course', _('Курс')),
        ('workshop', _('Майстер-клас')),
        ('meetup', _('Зустріч')),
        ('other', _('Інше')),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', _('Майбутня')),
        ('active', _('Активна')),
        ('completed', _('Завершена')),
        ('cancelled', _('Скасована')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_("Назва події"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("URL"))
    excerpt = models.TextField(max_length=300, verbose_name=_("Короткий опис"))
    content = models.TextField(verbose_name=_("Повний опис"))
    
    # Категорія та тип
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE, verbose_name=_("Категорія"))
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name=_("Тип події"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name=_("Статус"))
    
    # Дати та час
    start_date = models.DateTimeField(verbose_name=_("Дата та час початку"))
    end_date = models.DateTimeField(verbose_name=_("Дата та час завершення"))
    registration_deadline = models.DateTimeField(verbose_name=_("Дедлайн реєстрації"), null=True, blank=True)
    
    # Місце проведення
    location = models.CharField(max_length=200, blank=True, verbose_name=_("Місце проведення"))
    is_online = models.BooleanField(default=True, verbose_name=_("Онлайн подія"))
    meeting_link = models.URLField(blank=True, verbose_name=_("Посилання на зустріч"))
    
    # Ціна та знижки
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Ціна"))
    discount_percent = models.IntegerField(default=0, verbose_name=_("Відсоток знижки"))
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Оригінальна ціна"))
    
    # Обмеження
    max_participants = models.IntegerField(null=True, blank=True, verbose_name=_("Максимальна кількість учасників"))
    current_participants = models.IntegerField(default=0, verbose_name=_("Поточна кількість учасників"))
    
    # Зображення
    image = models.ImageField(upload_to='events/', blank=True, verbose_name=_("Зображення події"))
    
    # SEO
    seo_title = models.CharField(max_length=70, verbose_name=_("SEO заголовок"), blank=True)
    seo_description = models.CharField(max_length=160, verbose_name=_("SEO опис"), blank=True)
    keywords = models.CharField(max_length=255, verbose_name=_("Ключові слова"), blank=True)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))
    is_published = models.BooleanField(default=True, verbose_name=_("Опубліковано"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Рекомендована"))
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = _("Подія")
        verbose_name_plural = _("Події")
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Автоматичний розрахунок зниженої ціни
        if self.original_price and self.discount_percent > 0:
            self.price = self.original_price * (1 - self.discount_percent / 100)
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})
    
    @property
    def is_registration_open(self):
        """Чи відкрита реєстрація"""
        now = timezone.now()
        if self.registration_deadline:
            return now <= self.registration_deadline
        return now <= self.start_date
    
    @property
    def is_full(self):
        """Чи заповнена подія"""
        if self.max_participants:
            return self.current_participants >= self.max_participants
        return False
    
    @property
    def available_spots(self):
        """Доступні місця"""
        if self.max_participants:
            return max(0, self.max_participants - self.current_participants)
        return None
    
    @property
    def is_upcoming(self):
        """Чи майбутня подія"""
        return self.start_date > timezone.now()
    
    @property
    def is_active(self):
        """Чи активна подія"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date


class EventRegistration(models.Model):
    """Реєстрація на подію"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("Подія"))
    name = models.CharField(max_length=100, verbose_name=_("Ім'я"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, verbose_name=_("Телефон"))
    company = models.CharField(max_length=100, blank=True, verbose_name=_("Компанія"))
    message = models.TextField(blank=True, verbose_name=_("Додаткова інформація"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата реєстрації"))
    is_confirmed = models.BooleanField(default=False, verbose_name=_("Підтверджено"))
    
    class Meta:
        verbose_name = _("Реєстрація на подію")
        verbose_name_plural = _("Реєстрації на події")
        ordering = ['-created_at']
        unique_together = ['event', 'email']
    
    def __str__(self):
        return f"{self.name} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        # Збільшуємо лічильник учасників при реєстрації
        if not self.pk:  # Тільки при створенні
            self.event.current_participants += 1
            self.event.save()
        super().save(*args, **kwargs) 