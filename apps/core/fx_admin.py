"""Синглтон курсу і чекбокс права в картці користувача."""
from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.forms import UserChangeForm, UserCreationForm
from unfold.widgets import UnfoldBooleanWidget

from apps.core.admin_permissions import (
    apply_fx_grant,
    can_set_exchange_rates,
    user_has_fx_grant,
)
from apps.core.fx_models import ExchangeRateSettings


def _fx_grant_field():
    return forms.BooleanField(
        required=False,
        label=_('Може встановлювати курс валют'),
        widget=UnfoldBooleanWidget(),
    )


class UserFxForm(UserChangeForm):
    can_set_fx = _fx_grant_field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['can_set_fx'].initial = user_has_fx_grant(self.instance)
        password = self.fields.get('password')
        if password is not None:
            # Unfold прибирає кнопку з віджета хешу; посилання лишається в help_text.
            password.help_text = format_html(
                '{} <a href="../password/" class="text-primary-600 dark:text-primary-500">{}</a>.',
                _(
                    'Пароль зберігається у вигляді хешу, тому побачити його не можна. '
                    'Змінити пароль можна'
                ),
                _('цією формою'),
            )


class UserFxAddForm(UserCreationForm):
    """Форма створення: Unfold UserCreationForm → AdminUserCreationForm (є usable_password)."""

    can_set_fx = _fx_grant_field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['can_set_fx'].initial = False


@admin.register(ExchangeRateSettings)
class ExchangeRateSettingsAdmin(UnfoldModelAdmin):
    fields = ('uah_per_eur', 'usd_per_eur', 'czk_per_eur')
    list_filter_sheet = False

    def has_module_permission(self, request):
        return can_set_exchange_rates(request)

    def has_view_permission(self, request, obj=None):
        return can_set_exchange_rates(request)

    def has_change_permission(self, request, obj=None):
        return can_set_exchange_rates(request)

    def has_add_permission(self, request):
        if ExchangeRateSettings.objects.exists():
            return False
        return can_set_exchange_rates(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        obj, _created = ExchangeRateSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse('admin:core_exchangeratesettings_change', args=[obj.pk])
        )


def save_user_fx_grant(request, form) -> None:
    if not request.user.is_superuser:
        return
    if 'can_set_fx' not in form.cleaned_data:
        return
    apply_fx_grant(form.instance, bool(form.cleaned_data['can_set_fx']))
