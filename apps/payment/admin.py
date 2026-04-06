from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import PaymentLink, PaymentLinkFile, PaymentSettings, RecipientProfile


# ── PaymentSettings ────────────────────────────────────────────────────────

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        if PaymentSettings.objects.exists():
            return False
        return super().has_add_permission(request)


# ── RecipientProfile ───────────────────────────────────────────────────────

@admin.register(RecipientProfile)
class RecipientProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'recipient', 'iban', 'ipn', 'bank', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'recipient', 'iban')
    fieldsets = (
        (None, {
            'fields': ('name', 'is_active'),
        }),
        ('Реквізити', {
            'fields': ('recipient', 'iban', 'ipn', 'bank', 'mfo', 'bank_edrpou'),
        }),
    )


# ── PaymentLink form ───────────────────────────────────────────────────────

class PaymentLinkAdminForm(forms.ModelForm):
    description = forms.CharField(
        label='Опис замовлення',
        widget=forms.Textarea(attrs={'rows': 3, 'style': 'width:100%; resize:vertical'}),
        required=False,
        max_length=500,
        help_text='Що саме замовлено — буде показано клієнту на сторінці оплати.',
    )
    payment_instructions = forms.CharField(
        label='Інструкції для клієнта',
        widget=forms.Textarea(attrs={'rows': 4, 'style': 'width:100%; resize:vertical'}),
        required=False,
        help_text='Крок за кроком: як оплатити (через картку або переказ).',
    )

    class Meta:
        model = PaymentLink
        fields = '__all__'


# ── PaymentLink inline ─────────────────────────────────────────────────────

class PaymentLinkFileInline(admin.TabularInline):
    model = PaymentLinkFile
    extra = 1
    fields = ('file_type', 'name', 'file')
    verbose_name = 'Файл'
    verbose_name_plural = 'Файли (договори, рахунки)'


# ── PaymentLink admin ──────────────────────────────────────────────────────

@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    form = PaymentLinkAdminForm
    list_display = (
        'client_name', 'recipient', 'amount_usd', 'final_amount_uah',
        'status', 'use_acquiring', 'created_at',
        'open_link_button', 'copy_link_button',
    )
    list_filter = ('status', 'use_acquiring', 'recipient', 'created_at')
    search_fields = ('client_name', 'client_email', 'unique_id')
    readonly_fields = (
        'final_amount_uah', 'company_info',
        'first_opened_at', 'expires_at',
        'monobank_invoice_id', 'monobank_invoice_url', 'payment_processed_at',
    )
    inlines = [PaymentLinkFileInline]

    fieldsets = (
        ('Клієнт', {
            'fields': ('client_name', 'client_email'),
        }),
        ('Замовлення', {
            'fields': ('description', 'payment_instructions'),
        }),
        ('Отримувач платежу', {
            'fields': ('recipient', 'company_info'),
            'description': (
                'Оберіть профіль ФОП — реквізити на сторінці підставляться автоматично. '
                'Поле «Реквізити» нижче — тільки для перегляду.'
            ),
        }),
        ('Еквайринг', {
            'fields': ('use_acquiring',),
            'description': (
                'Якщо увімкнено — клієнт зможе оплатити карткою, Apple Pay або Google Pay '
                'через Monobank acquiring.'
            ),
        }),
        ('Сума та курс', {
            'fields': ('amount_usd', 'exchange_rate_usd_to_uah', 'final_amount_uah'),
            'description': 'Сума USD × курс = UAH. Розраховується автоматично при збереженні.',
        }),
        ('Налаштування посилання', {
            'fields': ('status', 'duration_minutes'),
        }),
        ('Системна інформація', {
            'fields': (
                'first_opened_at', 'expires_at', 'payment_processed_at',
                'monobank_invoice_id', 'monobank_invoice_url',
            ),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.recipient:
            rows = obj.recipient.as_requisites_rows()
            obj.company_info = '\n'.join(
                f"{r['label']}: {r['value']}" for r in rows
            )
        super().save_model(request, obj, form, change)

    def get_client_facing_link(self, obj):
        base = getattr(settings, 'SITE_URL', '').rstrip('/') or 'https://prometeylabs.com'
        return f"{base}/payment/pay/{obj.unique_id}/"

    def open_link_button(self, obj):
        url = self.get_client_facing_link(obj)
        return format_html('<a class="button" href="{}" target="_blank">Відкрити</a>', url)
    open_link_button.short_description = 'Відкрити'

    def copy_link_button(self, obj):
        url = self.get_client_facing_link(obj)
        btn_id = f'copy-btn-{obj.pk}'
        return format_html(
            '<div style="display:flex;gap:6px;align-items:center;min-width:260px">'
            '<input type="text" value="{url}" readonly '
            'style="flex:1;min-width:0;padding:4px 6px;border:1px solid #ccc;border-radius:3px"/>'
            '<button type="button" id="{btn_id}" '
            'onclick="(function(b,u){{navigator.clipboard.writeText(u).then(function(){{'
            'var o=b.textContent;b.textContent=\'\u2713\';'
            'setTimeout(function(){{b.textContent=o;}},1500);}})}})'
            '(document.getElementById(\'{btn_id}\'),\'{url}\')" '
            'style="white-space:nowrap;padding:4px 10px;cursor:pointer;'
            'border:1px solid #ccc;border-radius:3px;background:#f8f8f8">'
            '\U0001f4cb Копіювати'
            '</button>'
            '</div>',
            url=url, btn_id=btn_id,
        )
    copy_link_button.short_description = 'Посилання клієнта'
