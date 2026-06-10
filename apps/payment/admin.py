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

from .models import PaymentLink, PaymentLinkFile, PaymentSettings, RecipientProfile, SubscriptionCharge
from .subscription_service import MonobankSubscriptionService


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


class SubscriptionChargeInline(UnfoldTabularInline):
    model = SubscriptionCharge
    extra = 0
    can_delete = False
    fields = ('created_at', 'charged_at', 'amount_uah', 'status', 'monobank_invoice_id', 'error_message')
    readonly_fields = fields
    verbose_name = _('Списання')
    verbose_name_plural = _('Історія списань по підписці')

    def has_add_permission(self, request, obj=None):
        return False


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


class SubscriptionDropdownFilter(DropdownFilter):
    title = _('Підписка')
    parameter_name = 'is_subscription'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Так')),
            ('0', _('Ні')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == '1':
            return queryset.filter(is_subscription=True)
        if value == '0':
            return queryset.filter(is_subscription=False)
        return queryset


class SubscriptionStatusDropdownFilter(DropdownFilter):
    title = _('Статус підписки')
    parameter_name = 'subscription_status'

    def lookups(self, request, model_admin):
        return PaymentLink.SubscriptionStatus.choices

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(subscription_status=value)
        return queryset




@admin.register(PaymentLink)
class PaymentLinkAdmin(UnfoldModelAdmin):
    form = PaymentLinkAdminForm
    list_filter_sheet = False
    list_display = (
        'client_name', 'recipient', 'amount', 'currency', 'amount_uah_display',
        'status', 'subscription_badge', 'acquiring_enabled', 'created_at_compact',
        'client_link_cell',
    )
    list_filter = (
        ('status', ChoicesDropdownFilter),
        AcquiringDropdownFilter,
        SubscriptionDropdownFilter,
        SubscriptionStatusDropdownFilter,
        ('recipient', RelatedDropdownFilter),
        ('created_at', RangeDateFilter),
    )
    search_fields = ('client_name', 'client_email', 'unique_id')
    readonly_fields = (
        'final_amount_uah', 'company_info',
        'first_opened_at', 'expires_at',
        'monobank_invoice_id', 'monobank_invoice_url', 'payment_processed_at',
        'subscription_status', 'card_token', 'next_charge_date', 'last_charged_at',
    )
    inlines = [PaymentLinkFileInline, SubscriptionChargeInline]
    actions = ['mark_deactivated', 'charge_subscriptions_now', 'pause_subscriptions', 'resume_subscriptions']

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
        (_('Підписка'), {
            'fields': ('is_subscription', 'subscription_status', 'next_charge_date', 'last_charged_at', 'card_token'),
            'description': _(
                'Якщо увімкнено — перший платіж збереже картку клієнта. '
                'Після активації адмін може списувати кошти вручну через дії у списку. '
                'Поля статусу, дати та токену заповнюються автоматично.'
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

    @admin.display(description=_('Підписка'))
    def subscription_badge(self, obj):
        if not obj.is_subscription:
            return '—'
        status_map = {
            PaymentLink.SubscriptionStatus.PENDING_CARD: ('⏳', '#f59e0b'),
            PaymentLink.SubscriptionStatus.ACTIVE:       ('✓', '#16a34a'),
            PaymentLink.SubscriptionStatus.PAUSED:       ('⏸', '#6b7280'),
            PaymentLink.SubscriptionStatus.CANCELLED:    ('✕', '#dc2626'),
        }
        icon, color = status_map.get(obj.subscription_status, ('?', '#6b7280'))
        label = obj.get_subscription_status_display() if obj.subscription_status else '—'
        return format_html(
            '<span style="color:{color};font-weight:600">{icon} {label}</span>',
            color=color, icon=icon, label=label,
        )

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

    @admin.display(description=_('Посилання клієнта'))
    def client_link_cell(self, obj):
        url = self.get_client_facing_link(obj)
        open_label = _('Відкрити посилання')
        copy_label = _('Скопіювати посилання клієнта')
        return format_html(
            '<div class="pl-copy-row pl-copy-row--compact pl-copy-row--icons-only">'
            '<a class="pl-icon-btn pl-icon-btn--open" href="{url}" target="_blank" '
            'rel="noopener noreferrer" aria-label="{open_aria}" title="{open_title}">↗</a>'
            '<button type="button" class="pl-icon-btn pl-copy-btn" '
            'data-copy data-copy-value="{url}" '
            'aria-label="{copy_aria}" aria-pressed="false" title="{copy_title}">'
            '<span class="pl-copy-btn-icon" data-copy-icon="default" aria-hidden="true">⧉</span>'
            '<span class="pl-copy-btn-icon" data-copy-icon="done" aria-hidden="true" hidden>✓</span>'
            '</button>'
            '</div>',
            url=url,
            open_aria=open_label,
            open_title=_('Відкрити'),
            copy_aria=copy_label,
            copy_title=_('Копіювати'),
        )

    # ── Bulk actions ─────────────────────────────────────────────────────────

    @admin.action(description=_('Деактивувати вибрані посилання'))
    def mark_deactivated(self, request, queryset):
        updated = queryset.exclude(status=PaymentLink.Status.PAID).update(
            status=PaymentLink.Status.DEACTIVATED
        )
        self.message_user(request, _('Деактивовано: %(n)s') % {'n': updated})

    @admin.action(description=_('Зарядити вибрані підписки зараз'))
    def charge_subscriptions_now(self, request, queryset):
        eligible = queryset.filter(
            is_subscription=True,
            subscription_status=PaymentLink.SubscriptionStatus.ACTIVE,
        ).exclude(card_token='')

        if not eligible.exists():
            self.message_user(
                request,
                _('Серед вибраних немає активних підписок із прив\'язаною карткою.'),
                level='warning',
            )
            return

        svc = MonobankSubscriptionService()
        success_count = failed_count = pending_count = 0

        for pl in eligible:
            charge = SubscriptionCharge.objects.create(
                source_payment=pl,
                amount_uah=pl.final_amount_uah,
            )
            invoice_id, api_status = svc.charge_wallet(
                card_token=pl.card_token,
                wallet_id=str(pl.unique_id),
                amount_uah=pl.final_amount_uah,
                reference=f'sub-charge-{charge.id}',
                destination=pl.description or 'Щомісячна підписка',
                comment=f'Підписка: {pl.client_name}',
            )

            if api_status == 'success':
                now = timezone.now()
                charge.status = SubscriptionCharge.Status.SUCCESS
                charge.monobank_invoice_id = invoice_id or ''
                charge.charged_at = now
                charge.save(update_fields=['status', 'monobank_invoice_id', 'charged_at'])
                pl.last_charged_at = now
                next_date = pl.next_charge_date or now.date()
                if next_date.month == 12:
                    next_date = next_date.replace(year=next_date.year + 1, month=1, day=1)
                else:
                    next_date = next_date.replace(month=next_date.month + 1, day=1)
                pl.next_charge_date = next_date
                pl.save(update_fields=['last_charged_at', 'next_charge_date'])
                success_count += 1
            elif api_status in ('processing', 'created'):
                charge.monobank_invoice_id = invoice_id or ''
                charge.save(update_fields=['monobank_invoice_id'])
                pending_count += 1
            else:
                err = api_status or 'unknown'
                charge.status = SubscriptionCharge.Status.FAILED
                charge.error_message = f'API status: {err}'
                charge.save(update_fields=['status', 'error_message'])
                failed_count += 1

        parts = []
        if success_count:
            parts.append(_('Успішно: %(n)s') % {'n': success_count})
        if pending_count:
            parts.append(_('В обробці: %(n)s') % {'n': pending_count})
        if failed_count:
            parts.append(_('Помилок: %(n)s') % {'n': failed_count})
        level = 'error' if failed_count and not success_count and not pending_count else 'success'
        self.message_user(request, ' | '.join(parts) or _('Немає результатів'), level=level)

    @admin.action(description=_('Призупинити підписки'))
    def pause_subscriptions(self, request, queryset):
        updated = queryset.filter(
            is_subscription=True,
            subscription_status=PaymentLink.SubscriptionStatus.ACTIVE,
        ).update(subscription_status=PaymentLink.SubscriptionStatus.PAUSED)
        self.message_user(request, _('Призупинено: %(n)s') % {'n': updated})

    @admin.action(description=_('Відновити підписки'))
    def resume_subscriptions(self, request, queryset):
        updated = queryset.filter(
            is_subscription=True,
            subscription_status=PaymentLink.SubscriptionStatus.PAUSED,
        ).update(subscription_status=PaymentLink.SubscriptionStatus.ACTIVE)
        self.message_user(request, _('Відновлено: %(n)s') % {'n': updated})
