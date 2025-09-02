import json
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import PaymentLink, PaymentSettings
from .monobank_service import MonobankAcquiringService


def payment_page(request: HttpRequest, unique_id):
    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)

    # Перевірка статусів
    if payment_link.status in [PaymentLink.Status.PAID, PaymentLink.Status.DEACTIVATED]:
        return render(request, 'payment/link_inactive.html', {'payment_link': payment_link})

    # Прострочення
    payment_link.mark_first_open()
    if payment_link.is_expired():
        payment_link.status = PaymentLink.Status.EXPIRED
        payment_link.save(update_fields=['status'])
        return render(request, 'payment/link_inactive.html', {'payment_link': payment_link})

    payment_settings = PaymentSettings.objects.first()
    return render(request, 'payment/payment_page.html', {
        'payment_link': payment_link,
        'payment_settings': payment_settings,
    })


def create_invoice(request: HttpRequest, unique_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)
    if payment_link.status in [PaymentLink.Status.PAID, PaymentLink.Status.DEACTIVATED] or payment_link.is_expired():
        return render(request, 'payment/link_inactive.html', {'payment_link': payment_link})

    svc = MonobankAcquiringService()
    invoice_id, page_url = svc.create_invoice(
        reference=str(payment_link.unique_id),
        amount_uah=payment_link.final_amount_uah,
        destination=payment_link.description or 'Оплата послуг',
        comment=f'Платіж від {payment_link.client_name}',
        validity_seconds=payment_link.duration_minutes * 60 if payment_link.duration_minutes else 3600,
    )

    if not invoice_id or not page_url:
        return render(request, 'payment/payment_failure.html', {'payment_link': payment_link, 'reason': 'Помилка створення інвойсу'})

    payment_link.monobank_invoice_id = invoice_id
    payment_link.monobank_invoice_url = page_url
    payment_link.save(update_fields=['monobank_invoice_id', 'monobank_invoice_url'])
    return redirect(page_url)


@csrf_exempt
def monobank_webhook(request: HttpRequest):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    # Приклад структури, перевіряйте під свій контракт
    invoice_id = payload.get('invoiceId') or payload.get('invoice', {}).get('invoiceId')
    status = payload.get('status') or payload.get('invoice', {}).get('status')
    reference = payload.get('reference') or payload.get('invoice', {}).get('reference')

    if not reference:
        return HttpResponseBadRequest('No reference')

    try:
        payment_link = PaymentLink.objects.get(unique_id=reference)
    except PaymentLink.DoesNotExist:
        return HttpResponseBadRequest('Unknown reference')

    # Оновлення статусу
    if status == 'success' or status == 'paid' or payload.get('paymentInfo', {}).get('maskedPan'):
        payment_link.mark_paid()
    elif status in ['expired', 'reversed']:
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

