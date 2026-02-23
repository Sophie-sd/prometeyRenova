import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PaymentSettings(models.Model):
    title = models.CharField(max_length=255, default='Оплата послуг')
    description = models.TextField(blank=True, default='')
    default_contract_file = models.FileField(upload_to='contracts/', blank=True, null=True)

    class Meta:
        verbose_name = _('Налаштування платіжної системи')
        verbose_name_plural = _('Налаштування платіжної системи')

    def save(self, *args, **kwargs):
        # Забороняємо створення другого запису
        if not self.pk and PaymentSettings.objects.exists():
            raise ValidationError('Дозволено лише один запис PaymentSettings')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or f'Payment Settings #{self.pk}'


class PaymentLink(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        EXPIRED = 'expired', 'Expired'
        DEACTIVATED = 'deactivated', 'Deactivated'

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField(blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, default='')
    contract_file = models.FileField(upload_to='contracts/', blank=True, null=True, help_text='Персональний договір для цього посилання')
    company_info = models.TextField(blank=True, default='')
    payment_instructions = models.TextField(blank=True, default='')

    amount_usd = models.DecimalField(max_digits=12, decimal_places=2)
    exchange_rate_usd_to_uah = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('40.0000'))
    final_amount_uah = models.DecimalField(max_digits=14, decimal_places=2, editable=False)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    duration_minutes = models.PositiveIntegerField(default=0, help_text='0 — безстроково')
    first_opened_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    monobank_invoice_id = models.CharField(max_length=128, blank=True, default='')
    monobank_invoice_url = models.URLField(blank=True, default='')
    payment_processed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Платіжне посилання')
        verbose_name_plural = _('Платіжні посилання')

    def __str__(self):
        return f'{self.client_name} — {self.amount_usd} USD'

    def save(self, *args, **kwargs):
        # Обчислюємо суму в UAH
        if self.amount_usd is not None and self.exchange_rate_usd_to_uah:
            self.final_amount_uah = (self.amount_usd * self.exchange_rate_usd_to_uah).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def mark_first_open(self):
        if not self.first_opened_at:
            self.first_opened_at = timezone.now()
            if self.duration_minutes and self.duration_minutes > 0:
                self.expires_at = self.first_opened_at + timezone.timedelta(minutes=self.duration_minutes)
            if self.status == self.Status.NEW:
                self.status = self.Status.PENDING
            self.save(update_fields=['first_opened_at', 'expires_at', 'status'])

    def is_expired(self) -> bool:
        if self.duration_minutes and self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def deactivate(self):
        self.status = self.Status.DEACTIVATED
        self.save(update_fields=['status'])

    def mark_paid(self):
        self.status = self.Status.PAID
        self.payment_processed_at = timezone.now()
        self.save(update_fields=['status', 'payment_processed_at'])

