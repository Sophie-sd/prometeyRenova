from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline as UnfoldTabularInline
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    DropdownFilter,
    RangeDateFilter,
    RelatedDropdownFilter,
)

from .models import PaymentLink, PaymentLinkFile, PaymentSettings, RecipientProfile


# ── PaymentSettings ────────────────────────────────────────────────────────

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(UnfoldModelAdmin):
    list_display = ('title',)
    list_filter_sheet = False

    def has_add_permission(self, request):
        if PaymentSettings.objects.exists():
            return False
        return super().has_add_permission(request)


# ── RecipientProfile ───────────────────────────────────────────────────────

@admin.register(RecipientProfile)
class RecipientProfileAdmin(UnfoldModelAdmin):
    list_display = ('name', 'recipient', 'iban', 'ipn', 'bank', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'recipient', 'iban')
    list_filter_sheet = False
    fieldsets = (
        (None, {
            'fields': ('name', 'is_active'),
        }),
        (_('Реквізити'), {
            'fields': ('recipient', 'iban', 'ipn', 'bank', 'mfo', 'bank_edrpou'),
        }),
    )


# ── PaymentLink form ───────────────────────────────────────────────────────

class PaymentLinkAdminForm(forms.ModelForm):
    description = forms.CharField(
        label=_('Опис / Призначення платежу'),
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'pl-textarea-wide'}),
        required=False,
        max_length=500,
        help_text=_(
            'Що саме замовлено. Це поле використовується як призначення платежу — '
            'клієнт зможе його скопіювати.'
        ),
    )

    class Meta:
        model = PaymentLink
        fields = '__all__'


# ── PaymentLink inline ─────────────────────────────────────────────────────

class PaymentLinkFileInline(UnfoldTabularInline):
    model = PaymentLinkFile
    extra = 1
    fields = ('file_type', 'name', 'file')
    verbose_name = _('Файл')
    verbose_name_plural = _('Файли (договори, рахунки)')


# ── List filters ───────────────────────────────────────────────────────────

class AcquiringDropdownFilter(DropdownFilter):
    title = _('Еквайринг')
    parameter_name = 'use_acquiring'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Так')),
            ('0', _('Ні')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == '1':
            return queryset.filter(use_acquiring=True)
        if value == '0':
            return queryset.filter(use_acquiring=False)
        return queryset


# ── PaymentLink admin ──────────────────────────────────────────────────────

@admin.register(PaymentLink)
class PaymentLinkAdmin(UnfoldModelAdmin):
    form = PaymentLinkAdminForm
    list_filter_sheet = False
    list_display = (
        'client_name', 'recipient', 'amount', 'currency', 'amount_uah_display',
        'status', 'acquiring_enabled', 'created_at_compact',
        'open_link_button', 'copy_link_button',
    )
    list_filter = (
        ('status', ChoicesDropdownFilter),
        AcquiringDropdownFilter,
        ('recipient', RelatedDropdownFilter),
        ('created_at', RangeDateFilter),
    )
    search_fields = ('client_name', 'client_email', 'unique_id')
    readonly_fields = (
        'final_amount_uah', 'company_info',
        'first_opened_at', 'expires_at',
        'monobank_invoice_id', 'monobank_invoice_url', 'payment_processed_at',
    )
    inlines = [PaymentLinkFileInline]
    actions = ['mark_deactivated']

    fieldsets = (
        (_('Клієнт'), {
            'fields': ('client_name', 'client_email'),
        }),
        (_('Замовлення / Призначення платежу'), {
            'fields': ('description',),
        }),
        (_('Отримувач платежу'), {
            'fields': ('recipient', 'company_info'),
            'description': _(
                'Оберіть профіль ФОП — реквізити на сторінці підставляться автоматично. '
                'Поле «Реквізити» нижче — тільки для перегляду.'
            ),
        }),
        (_('Еквайринг'), {
            'fields': ('use_acquiring',),
            'description': _(
                'Якщо увімкнено — клієнт зможе оплатити карткою, Apple Pay або Google Pay '
                'через Monobank acquiring.'
            ),
        }),
        (_('Сума та курс'), {
            'fields': ('currency', 'amount', 'exchange_rate', 'final_amount_uah'),
            'description': _(
                'Для USD/EUR вкажіть суму та курс до UAH. '
                'Для UAH — лише сума, курс ігнорується. '
                'Підсумкова сума UAH розраховується автоматично при збереженні.'
            ),
        }),
        (_('Налаштування посилання'), {
            'fields': ('status', 'duration_minutes'),
        }),
        (_('Системна інформація'), {
            'fields': (
                'first_opened_at', 'expires_at', 'payment_processed_at',
                'monobank_invoice_id', 'monobank_invoice_url',
            ),
            'classes': ('collapse',),
        }),
    )

    class Media:
        css = {'all': ('payment/css/admin.css',)}
        js = ('payment/js/copy.js', 'payment/js/admin.js')

    @admin.display(description=_('Сума UAH'), ordering='final_amount_uah')
    def amount_uah_display(self, obj):
        return obj.final_amount_uah

    @admin.display(description=_('Еквайринг'), boolean=True)
    def acquiring_enabled(self, obj):
        return obj.use_acquiring

    @admin.display(description=_('Створено'), ordering='created_at')
    def created_at_compact(self, obj):
        if not obj.created_at:
            return '—'
        local_dt = timezone.localtime(obj.created_at)
        return local_dt.strftime('%d.%m.%Y %H:%M')

    def save_model(self, request, obj, form, change):
        if obj.recipient:
            rows = obj.recipient.as_requisites_rows()
            obj.company_info = '\n'.join(
                f"{r['label']}: {r['value']}" for r in rows
            )
        super().save_model(request, obj, form, change)

    def get_client_facing_link(self, obj) -> str:
        base = getattr(settings, 'SITE_URL', '').rstrip('/') or 'https://prometeylabs.com'
        return f"{base}/payment/pay/{obj.unique_id}/"

    @admin.display(description=_('Відкрити'))
    def open_link_button(self, obj):
        url = self.get_client_facing_link(obj)
        return format_html(
            '<a class="button" href="{}" target="_blank" rel="noopener">{}</a>',
            url, _('Відкрити'),
        )

    @admin.display(description=_('Посилання клієнта'))
    def copy_link_button(self, obj):
        url = self.get_client_facing_link(obj)
        return format_html(
            '<div class="pl-copy-row pl-copy-row--compact">'
            '<input type="text" class="pl-copy-input" value="{url}" readonly '
            'aria-label="{aria}" title="{url}">'
            '<button type="button" class="pl-copy-btn" '
            'data-copy data-copy-value="{url}" '
            'aria-label="{aria}" aria-pressed="false" title="{label}">'
            '<span class="pl-copy-btn-icon" data-copy-icon="default" aria-hidden="true">⧉</span>'
            '<span class="pl-copy-btn-icon" data-copy-icon="done" aria-hidden="true" hidden>✓</span>'
            '<span class="pl-copy-btn-text" data-copy-label>{label}</span>'
            '</button>'
            '</div>',
            url=url, label=_('Копіювати'), aria=_('Скопіювати посилання клієнта'),
        )

    @admin.action(description=_('Деактивувати вибрані посилання'))
    def mark_deactivated(self, request, queryset):
        updated = queryset.exclude(status=PaymentLink.Status.PAID).update(
            status=PaymentLink.Status.DEACTIVATED
        )
        self.message_user(request, _('Деактивовано: %(n)s') % {'n': updated})
