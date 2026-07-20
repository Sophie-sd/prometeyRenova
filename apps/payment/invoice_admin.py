"""Admin для модуля «Рахунки»."""
from datetime import date

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline as UnfoldTabularInline

from .invoice_models import Invoice, InvoiceItem
from .invoice_pdf import get_or_create_invoice_pdf
from .models import RecipientProfile


CLIENT_HINTS_HTML = mark_safe(
    '<div class="invoice-client-hints">'
    '<p class="invoice-client-hints__title">Що вказувати:</p>'
    '<ul class="invoice-client-hints__list">'
    '<li><strong>ФОП</strong> — ФОП Прізвище Імʼя По батькові, РНОКПП (10 цифр), '
    'адреса за бажанням</li>'
    '<li><strong>ТОВ / юрособа</strong> — повна назва (ТОВ «…»), ЄДРПОУ (8 цифр), '
    'юридична адреса бажано</li>'
    '<li><strong>Фізособа</strong> — ПІБ повністю, РНОКПП (якщо є), адреса за бажанням</li>'
    '</ul>'
    '</div>'
)


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ('title', 'unit', 'quantity', 'price', 'position')
        widgets = {
            'title': forms.Textarea(attrs={
                'rows': 2,
                'cols': 40,
                'class': 'vLargeTextField invoice-item-title',
            }),
        }

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty <= 0:
            raise forms.ValidationError(_('Кількість має бути більшою за 0.'))
        return qty

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None or price < 0:
            raise forms.ValidationError(_('Ціна не може бути від\'ємною.'))
        return price


class InvoiceItemInline(UnfoldTabularInline):
    model = InvoiceItem
    form = InvoiceItemForm
    extra = 1
    min_num = 1
    fields = ('position', 'title', 'unit', 'quantity', 'price')
    ordering = ('position', 'id')
    verbose_name = _('Послуга')
    verbose_name_plural = _('Послуги')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1

    def has_add_permission(self, request, obj=None):
        if obj:
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj:
            return False
        return super().has_delete_permission(request, obj)


class InvoiceAdminForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            'recipient', 'client_name', 'client_tax_id', 'client_address',
            'invoice_date', 'contract_number', 'contract_date',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'recipient' in self.fields:
            self.fields['recipient'].queryset = RecipientProfile.objects.filter(
                is_active=True
            ).order_by('name')
            self.fields['recipient'].label = _('Отримувач / Виконавець')
            self.fields['recipient'].empty_label = _('— оберіть отримувача —')
        if 'client_name' in self.fields:
            self.fields['client_name'].label = _('Замовник (назва / ПІБ)')
            self.fields['client_name'].help_text = _(
                'ФОП: ФОП Прізвище Імʼя По батькові · '
                'ТОВ: повна назва (ТОВ «…») · '
                'Фізособа: ПІБ повністю'
            )
        if 'client_tax_id' in self.fields:
            self.fields['client_tax_id'].label = _('РНОКПП / ЄДРПОУ')
            self.fields['client_tax_id'].help_text = _(
                'ФОП / фізособа — РНОКПП (10 цифр); ТОВ / юрособа — ЄДРПОУ (8 цифр)'
            )
        if 'client_address' in self.fields:
            self.fields['client_address'].label = _('Адреса (опційно)')
            self.fields['client_address'].help_text = _(
                'Для ТОВ бажано юридичну адресу; для ФОП / фізособи — за бажанням'
            )
        if 'invoice_date' in self.fields and not self.instance.pk:
            self.fields['invoice_date'].initial = date.today()


@admin.register(Invoice)
class InvoiceAdmin(UnfoldModelAdmin):
    form = InvoiceAdminForm
    inlines = [InvoiceItemInline]
    list_filter_sheet = False
    list_display = (
        'number', 'invoice_date', 'recipient_col', 'client_name',
        'total_col', 'contract_col', 'created_at_col', 'pdf_col',
    )
    list_display_links = ('number',)
    search_fields = ('number', 'client_name', 'contract_number', 'client_tax_id')
    ordering = ('-number',)
    list_per_page = 50
    change_form_template = 'admin/payment/invoice/change_form.html'

    class Media:
        css = {'all': ('payment/css/invoice_admin.css',)}
        js = ('payment/js/invoice_admin.js',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                'number', 'invoice_date', 'valid_until', 'recipient',
                'client_name', 'client_tax_id', 'client_address',
                'contract_number', 'contract_date', 'total_amount',
                'created_at', 'created_by',
            )
        return ('number', 'valid_until', 'total_amount')

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (_('Рахунок'), {
                    'fields': ('number', 'invoice_date', 'valid_until', 'total_amount'),
                }),
                (_('Виконавець'), {
                    'fields': ('recipient',),
                }),
                (_('Замовник'), {
                    'fields': ('client_name', 'client_tax_id', 'client_address'),
                }),
                (_('Договір'), {
                    'fields': ('contract_number', 'contract_date'),
                }),
                (_('Службове'), {
                    'fields': ('created_at', 'created_by'),
                    'classes': ('collapse',),
                }),
            )
        return (
            (_('Виконавець'), {
                'fields': ('recipient',),
                'description': _(
                    'Оберіть активний профіль отримувача — реквізити підставляться в PDF.'
                ),
            }),
            (_('Замовник'), {
                    'fields': ('client_name', 'client_tax_id', 'client_address'),
                    'description': CLIENT_HINTS_HTML,
                }),
                (_('Рахунок'), {
                    'fields': ('invoice_date', 'valid_until'),
                    'description': _(
                        'Номер рахунку призначається автоматично при збереженні. '
                        '«Доступний до» = дата рахунку + 3 дні.'
                    ),
                }),
            (_('Договір'), {
                'fields': ('contract_number', 'contract_date'),
            }),
        )

    def has_change_permission(self, request, obj=None):
        # Дозволяємо відкриття change для перегляду / PDF, але поля readonly.
        return request.user.has_perm('payment.view_invoice') or super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        invoice = form.instance
        # Нормалізуємо position 1..N
        for idx, item in enumerate(invoice.items.all().order_by('position', 'id'), start=1):
            if item.position != idx:
                item.position = idx
                item.save(update_fields=['position'])
            else:
                # Перерахувати amount на випадок
                item.save()
        invoice.recalculate_total()

    def response_add(self, request, obj, post_url_continue=None):
        if '_save_and_pdf' in request.POST:
            return HttpResponseRedirect(
                reverse('admin:payment_invoice_download_pdf', args=[obj.pk])
            )
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if '_save_and_pdf' in request.POST:
            return HttpResponseRedirect(
                reverse('admin:payment_invoice_download_pdf', args=[obj.pk])
            )
        return super().response_change(request, obj)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<path:object_id>/pdf/',
                self.admin_site.admin_view(self.download_pdf_view),
                name='payment_invoice_download_pdf',
            ),
        ]
        return custom + urls

    def download_pdf_view(self, request, object_id):
        invoice = Invoice.objects.filter(pk=object_id).first()
        if not invoice:
            messages.error(request, _('Рахунок не знайдено.'))
            return HttpResponseRedirect(reverse('admin:payment_invoice_changelist'))
        try:
            data, filename = get_or_create_invoice_pdf(invoice, force=True)
        except Exception as exc:
            messages.error(request, _('Помилка генерації PDF: %s') % exc)
            return HttpResponseRedirect(
                reverse('admin:payment_invoice_change', args=[object_id])
            )
        from urllib.parse import quote
        response = HttpResponse(data, content_type='application/pdf')
        ascii_name = f'Invoice_{invoice.number}.pdf'
        response['Content-Disposition'] = (
            f"attachment; filename=\"{ascii_name}\"; "
            f"filename*=UTF-8''{quote(filename)}"
        )
        return response

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            extra_context['show_save'] = False
            extra_context['show_save_and_continue'] = False
            extra_context['show_save_and_add_another'] = False
            extra_context['invoice_pdf_url'] = reverse(
                'admin:payment_invoice_download_pdf', args=[object_id]
            )
            extra_context['invoice_is_readonly'] = True
        else:
            extra_context['invoice_is_readonly'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)

    @admin.display(description=_('Виконавець'))
    def recipient_col(self, obj):
        return obj.recipient_name_snapshot or (obj.recipient.name if obj.recipient else '—')

    @admin.display(description=_('Сума'), ordering='total_amount')
    def total_col(self, obj):
        from .amount_ua import format_money_ua
        return f'{format_money_ua(obj.total_amount)} грн'

    @admin.display(description=_('Договір'))
    def contract_col(self, obj):
        d = obj.contract_date.strftime('%d.%m.%Y') if obj.contract_date else ''
        return f'№ {obj.contract_number} від {d}'

    @admin.display(description=_('Створено'), ordering='created_at')
    def created_at_col(self, obj):
        if not obj.created_at:
            return '—'
        from django.utils import timezone
        return timezone.localtime(obj.created_at).strftime('%d.%m.%Y %H:%M')

    @admin.display(description=_('PDF'))
    def pdf_col(self, obj):
        pdf_url = reverse('admin:payment_invoice_download_pdf', args=[obj.pk])
        return format_html(
            '<a class="invoice-pdf-dl" href="{}" title="{}" aria-label="{}">'
            '<span class="material-symbols-outlined" aria-hidden="true">download</span>'
            '</a>',
            pdf_url,
            _('Завантажити PDF'),
            _('Завантажити PDF'),
        )

    def delete_model(self, request, obj):
        obj.delete()  # soft-delete

    def delete_queryset(self, request, queryset):
        queryset.delete()  # soft-delete через SoftDeleteQuerySet
