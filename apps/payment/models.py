import uuid
import os
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


class RecipientProfile(models.Model):
    """ФОП / юрособа — профіль отримувача платежу."""
    name = models.CharField(max_length=255, verbose_name=_('Назва профілю'))
    recipient = models.CharField(max_length=255, verbose_name=_('Отримувач'))
    iban = models.CharField(max_length=100, verbose_name=_('IBAN'))
    ipn = models.CharField(max_length=50, verbose_name=_('ІПН/ЄДРПОУ'))
    bank = models.CharField(max_length=255, blank=True, default='', verbose_name=_('Банк'))
    mfo = models.CharField(max_length=20, blank=True, default='', verbose_name=_('МФО'))
    bank_edrpou = models.CharField(max_length=20, blank=True, default='', verbose_name=_('ЄДРПОУ Банку'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))

    class Meta:
        ordering = ['name']
        verbose_name = _('Профіль отримувача (ФОП)')
        verbose_name_plural = _('Профілі отримувачів (ФОП)')

    def __str__(self):
        return self.name

    def as_requisites_rows(self) -> list:
        fields = [
            ('Отримувач',    self.recipient,   True),
            ('IBAN',         self.iban,         True),
            ('ІПН/ЄДРПОУ',  self.ipn,          True),
            ('Банк',         self.bank,         False),
            ('МФО',          self.mfo,          False),
            ('ЄДРПОУ Банку', self.bank_edrpou,  False),
        ]
        return [{'label': lbl, 'value': val, 'copyable': cp} for lbl, val, cp in fields if val]


class PaymentLink(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        EXPIRED = 'expired', 'Expired'
        DEACTIVATED = 'deactivated', 'Deactivated'

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    client_name = models.CharField(max_length=255, verbose_name=_('Ім\'я клієнта'))
    client_email = models.EmailField(blank=True, null=True, verbose_name=_('Email клієнта'))
    description = models.TextField(blank=True, default='', verbose_name=_('Опис замовлення'))
    recipient = models.ForeignKey(
        RecipientProfile,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Отримувач (ФОП)'),
        related_name='payment_links',
    )
    company_info = models.TextField(blank=True, default='', verbose_name=_('Реквізити (авто з профілю)'))
    payment_instructions = models.TextField(blank=True, default='', verbose_name=_('Інструкції'))
    contract_file = models.FileField(upload_to='contracts/', blank=True, null=True)
    use_acquiring = models.BooleanField(
        default=True,
        verbose_name=_('Увімкнути еквайринг (картка / Apple Pay / Google Pay)'),
    )

    amount_usd = models.DecimalField(max_digits=12, decimal_places=2)
    exchange_rate_usd_to_uah = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('40.00'))
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


class PaymentLinkFile(models.Model):
    class FileType(models.TextChoices):
        CONTRACT = 'contract', _('Договір')
        INVOICE = 'invoice', _('Рахунок')
        OTHER = 'other', _('Інший документ')

    payment_link = models.ForeignKey(
        PaymentLink,
        on_delete=models.CASCADE,
        related_name='attached_files',
        verbose_name=_('Платіжне посилання'),
    )
    file = models.FileField(upload_to='payment_files/', verbose_name=_('Файл'))
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.CONTRACT,
        verbose_name=_('Тип'),
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_('Назва (необов\'язково)'),
        help_text=_('Якщо не заповнено — показується тип файлу'),
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['file_type', 'uploaded_at']
        verbose_name = _('Файл посилання')
        verbose_name_plural = _('Файли посилання')

    def display_name(self) -> str:
        return self.name or self.get_file_type_display()

    def filename(self) -> str:
        return os.path.basename(self.file.name)

    def __str__(self):
        return f'{self.display_name()} — {self.filename()}'

