import json
import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List

from django.contrib.admin.views.decorators import staff_member_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import PaymentLink, PaymentSettings, SubscriptionCharge
from .monobank_service import MonobankAcquiringService
from .subscription_service import MonobankSubscriptionService

logger = logging.getLogger('payment')

PAYMENT_SETTINGS_CACHE_KEY = 'payment_settings'
PAYMENT_SETTINGS_CACHE_TTL = 3600


def get_payment_settings():
    """Cached PaymentSettings lookup. Cache is invalidated via signal on save."""
    settings = cache.get(PAYMENT_SETTINGS_CACHE_KEY)
    if settings is None:
        settings = PaymentSettings.objects.first()
        cache.set(PAYMENT_SETTINGS_CACHE_KEY, settings, PAYMENT_SETTINGS_CACHE_TTL)
    return settings


def parse_requisites(text: str) -> list:
    """Splits company_info into structured rows {label, value, copyable}."""
    rows = []
    for line in (text or '').splitlines():
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            label, _sep, value = line.partition(':')
            rows.append({'label': label.strip(), 'value': value.strip(), 'copyable': True})
        else:
            rows.append({'label': '', 'value': line, 'copyable': True})
    return rows


def _build_requisites_payload(requisites_rows: list, payment_link: PaymentLink) -> List[str]:
    payload: List[str] = []
    for row in requisites_rows:
        if not row.get('copyable', True):
            continue
        value = row.get('value', '')
        if not value:
            continue
        label = row.get('label') or ''
        payload.append(f'{label}: {value}' if label else str(value))
    if payment_link.description:
        payload.append(f"{_('Призначення')}: {payment_link.description}")
    payload.append(f"{_('Сума')}: {payment_link.final_amount_uah} UAH")
    return payload


def _next_month_first(from_date: date) -> date:
    """Returns the 1st day of the month following from_date."""
    if from_date.month == 12:
        return from_date.replace(year=from_date.year + 1, month=1, day=1)
    return from_date.replace(month=from_date.month + 1, day=1)


def _card_token_from_wallet_cards(cards: list) -> str:
    """Picks cardToken from Monobank wallet cards list (active card preferred)."""
    if not cards:
        return ''
    active = next((c for c in cards if c.get('status') == 'active'), None)
    return (active or {}).get('cardToken', '') or ''


def _activate_subscription(payment_link: PaymentLink, payload: dict) -> None:
    """Called from webhook after first subscription payment succeeds."""
    invoice_sub = payload.get('invoice') if isinstance(payload.get('invoice'), dict) else {}
    wallet_data = payload.get('walletData') or invoice_sub.get('walletData') or {}
    card_token = wallet_data.get('cardToken', '')

    if not card_token:
        logger.warning(
            'No cardToken in webhook payload for %s. Payload: %s',
            payment_link.unique_id,
            payload,
        )
        svc = MonobankSubscriptionService()
        cards = svc.get_wallet_cards(str(payment_link.unique_id)) or []
        card_token = _card_token_from_wallet_cards(cards)

    if not card_token:
        logger.error(
            'Cannot activate subscription %s: no cardToken',
            payment_link.unique_id,
        )
        return

    today = timezone.now().date()
    payment_link.card_token = card_token
    payment_link.subscription_status = PaymentLink.SubscriptionStatus.ACTIVE
    payment_link.next_charge_date = _next_month_first(today)
    payment_link.save(update_fields=['card_token', 'subscription_status', 'next_charge_date'])
    logger.info('Subscription activated: payment %s', payment_link.unique_id)


def _handle_subscription_charge_webhook(
    reference: str, invoice_id: str, status: str, payload: dict
) -> HttpResponse:
    """Handles webhook callbacks for recurring SubscriptionCharge payments."""
    try:
        charge_id = int(reference.split('sub-charge-', 1)[1])
        charge = SubscriptionCharge.objects.select_related('source_payment').get(id=charge_id)
    except (IndexError, ValueError, SubscriptionCharge.DoesNotExist):
        return HttpResponseBadRequest('Unknown subscription charge reference')

    if status in ('success', 'paid'):
        now = timezone.now()
        charge.status = SubscriptionCharge.Status.SUCCESS
        charge.monobank_invoice_id = invoice_id or ''
        charge.charged_at = now
        charge.save(update_fields=['status', 'monobank_invoice_id', 'charged_at'])
        pl = charge.source_payment
        pl.last_charged_at = now
        pl.next_charge_date = _next_month_first(pl.next_charge_date or now.date())
        pl.save(update_fields=['last_charged_at', 'next_charge_date'])
        logger.info('Subscription charge %s succeeded', charge_id)
    elif status in ('failure', 'expired', 'reversed'):
        err = payload.get('errText', '') or status
        charge.status = SubscriptionCharge.Status.FAILED
        charge.error_message = err
        charge.save(update_fields=['status', 'error_message'])
        logger.warning('Subscription charge %s failed: %s', charge_id, err)

    return JsonResponse({'ok': True})


def payment_page(request: HttpRequest, unique_id):
    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)

    inactive_statuses = (
        PaymentLink.Status.PAID,
        PaymentLink.Status.DEACTIVATED,
        PaymentLink.Status.EXPIRED,
    )
    if payment_link.status in inactive_statuses:
        return render(request, 'payment/link_inactive.html', {'payment_link': payment_link})

    payment_link.mark_first_open()
    if payment_link.is_expired():
        if payment_link.status != PaymentLink.Status.EXPIRED:
            payment_link.status = PaymentLink.Status.EXPIRED
            payment_link.save(update_fields=['status'])
        return render(request, 'payment/link_inactive.html', {'payment_link': payment_link})

    payment_settings = get_payment_settings()

    expires_at_iso = payment_link.expires_at.isoformat() if payment_link.expires_at else None

    if payment_link.recipient:
        requisites_rows = payment_link.recipient.as_requisites_rows()
    else:
        requisites_rows = parse_requisites(payment_link.company_info)

    has_bank_rows = any(not row.get('copyable', True) for row in requisites_rows)
    requisites_payload = _build_requisites_payload(requisites_rows, payment_link)

    return render(request, 'payment/payment_page.html', {
        'payment_link': payment_link,
        'payment_settings': payment_settings,
        'expires_at_iso': expires_at_iso,
        'requisites_rows': requisites_rows,
        'requisites_payload': requisites_payload,
        'has_bank_rows': has_bank_rows,
    })


def create_invoice(request: HttpRequest, unique_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)
    inactive_statuses = (
        PaymentLink.Status.PAID,
        PaymentLink.Status.DEACTIVATED,
        PaymentLink.Status.EXPIRED,
    )
    if payment_link.status in inactive_statuses or payment_link.is_expired():
        return render(request, 'payment/link_inactive.html', {'payment_link': payment_link})

    if not payment_link.use_acquiring:
        return HttpResponseBadRequest('Acquiring disabled for this payment link')

    validity = payment_link.duration_minutes * 60 if payment_link.duration_minutes else 3600

    if payment_link.is_subscription:
        svc = MonobankSubscriptionService()
        invoice_id, page_url = svc.create_invoice_with_save_card(
            reference=str(payment_link.unique_id),
            wallet_id=str(payment_link.unique_id),
            amount_uah=payment_link.final_amount_uah,
            destination=payment_link.description or 'Щомісячна підписка',
            comment=f'Підписка: {payment_link.client_name}',
            validity_seconds=validity,
        )
    else:
        svc = MonobankAcquiringService()
        invoice_id, page_url = svc.create_invoice(
            reference=str(payment_link.unique_id),
            amount_uah=payment_link.final_amount_uah,
            destination=payment_link.description or 'Оплата послуг',
            comment=f'Платіж від {payment_link.client_name}',
            validity_seconds=validity,
        )

    if not invoice_id or not page_url:
        return render(request, 'payment/payment_failure.html', {
            'payment_link': payment_link,
            'reason': 'Помилка створення інвойсу',
        })

    payment_link.monobank_invoice_id = invoice_id
    payment_link.monobank_invoice_url = page_url
    payment_link.save(update_fields=['monobank_invoice_id', 'monobank_invoice_url'])
    return redirect(page_url)


@csrf_exempt
def monobank_webhook(request: HttpRequest):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    raw_body = request.body
    x_sign = request.headers.get('X-Sign') or request.META.get('HTTP_X_SIGN')

    svc = MonobankAcquiringService()
    if not svc.verify_signature(raw_body, x_sign):
        logger.warning('Monobank webhook signature verification failed')
        return HttpResponseForbidden('Invalid signature')

    try:
        payload = json.loads(raw_body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return HttpResponseBadRequest('Invalid JSON')

    invoice = payload.get('invoice') if isinstance(payload.get('invoice'), dict) else {}
    invoice_id = payload.get('invoiceId') or invoice.get('invoiceId')
    status = payload.get('status') or invoice.get('status')
    reference = payload.get('reference') or invoice.get('reference')
    amount_kop = payload.get('amount') or invoice.get('amount')

    if not reference:
        return HttpResponseBadRequest('No reference')

    # ── Subscription charge webhook ───────────────────────────────────────────
    if reference.startswith('sub-charge-'):
        return _handle_subscription_charge_webhook(reference, invoice_id or '', status or '', payload)

    # ── Regular payment link webhook ─────────────────────────────────────────
    try:
        payment_link = PaymentLink.objects.get(unique_id=reference)
    except (PaymentLink.DoesNotExist, ValueError):
        return HttpResponseBadRequest('Unknown reference')

    if invoice_id and payment_link.monobank_invoice_id and \
            payment_link.monobank_invoice_id != invoice_id:
        logger.warning(
            'Monobank webhook invoiceId mismatch: link=%s expected=%s got=%s',
            payment_link.unique_id, payment_link.monobank_invoice_id, invoice_id,
        )
        return HttpResponseBadRequest('invoiceId mismatch')

    if amount_kop is not None:
        try:
            expected_kop = int((payment_link.final_amount_uah * 100).to_integral_value())
            if int(amount_kop) != expected_kop:
                logger.warning(
                    'Monobank webhook amount mismatch: link=%s expected=%s got=%s',
                    payment_link.unique_id, expected_kop, amount_kop,
                )
        except (TypeError, ValueError, InvalidOperation):
            pass

    if status in ('success', 'paid'):
        payment_link.mark_paid()
        if payment_link.is_subscription:
            _activate_subscription(payment_link, payload)
    elif status in ('expired', 'reversed', 'failure'):
        if payment_link.status not in (PaymentLink.Status.PAID, PaymentLink.Status.DEACTIVATED):
            payment_link.status = PaymentLink.Status.EXPIRED
            payment_link.save(update_fields=['status'])

    return JsonResponse({'ok': True})


def payment_success(request: HttpRequest, unique_id):
    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)
    return render(request, 'payment/payment_success.html', {'payment_link': payment_link})


def payment_failure(request: HttpRequest, unique_id):
    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)
    return render(request, 'payment/payment_failure.html', {'payment_link': payment_link})


@staff_member_required
def test_monobank_api(request: HttpRequest):
    if request.method == 'POST':
        svc = MonobankAcquiringService()
        invoice_id, page_url = svc.create_invoice(
            reference='test-reference',
            amount_uah=Decimal('10.00'),
            destination='Тестовий платіж',
            comment='Тест API',
            validity_seconds=600,
        )
        return render(request, 'payment/payment_success.html', {
            'payment_link': None,
            'invoice_id': invoice_id,
            'page_url': page_url,
            'test_mode': True,
        })

    return render(request, 'payment/payment_page.html', {'test_mode': True})
