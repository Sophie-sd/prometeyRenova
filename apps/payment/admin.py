from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import PaymentLink, PaymentSettings


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('title',)
    readonly_fields = ()

    def has_add_permission(self, request):
        # Дозволяємо лише один запис
        if PaymentSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'amount_usd', 'final_amount_uah', 'status', 'created_at', 'open_link_button', 'copy_link_button')
    list_filter = ('status', 'created_at')
    search_fields = ('client_name', 'client_email', 'unique_id')
    readonly_fields = ('final_amount_uah', 'first_opened_at', 'expires_at', 'monobank_invoice_id', 'monobank_invoice_url', 'payment_processed_at')
    fields = ('client_name', 'client_email', 'description', 'contract_file', 'amount_usd', 'exchange_rate_usd_to_uah', 'final_amount_uah', 'status', 'duration_minutes', 'first_opened_at', 'expires_at', 'monobank_invoice_id', 'monobank_invoice_url', 'payment_processed_at')

    def get_client_facing_link(self, obj: PaymentLink) -> str:
        base_url = getattr(settings, 'SITE_URL', '').rstrip('/') or 'https://pay.prometeylabs.com'
        return f"{base_url}/payment/pay/{obj.unique_id}/"

    def open_link_button(self, obj):
        url = self.get_client_facing_link(obj)
        return format_html('<a class="button" href="{}" target="_blank">Відкрити</a>', url)
    open_link_button.short_description = 'Клієнтське посилання'

    def copy_link_button(self, obj):
        url = self.get_client_facing_link(obj)
        return format_html('<input type="text" value="{}" readonly style="width:100%"/>', url)
    copy_link_button.short_description = 'Скопіювати'

