"""Згода на чекаут: чекбокси, IP, лист-підтвердження (§1824a NOZ)."""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from .models import PaymentLink

logger = logging.getLogger('payment')

_CHECKED = frozenset({'1', 'on', 'true', 'yes'})


def client_ip(request: HttpRequest):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip() or None
    return request.META.get('REMOTE_ADDR') or None


def has_checkout_consents(request: HttpRequest) -> bool:
    waiver = (request.POST.get('withdrawal_waiver') or '').strip().lower()
    consent = (request.POST.get('data_consent') or '').strip().lower()
    return waiver in _CHECKED and consent in _CHECKED


def require_and_record_consents(request: HttpRequest, payment_link: PaymentLink):
    """400, якщо чекбокси не відмічені; інакше фіксує час і IP."""
    if not has_checkout_consents(request):
        return HttpResponseBadRequest(
            _('Підтвердіть обидва пункти: відмову від права відступлення та згоду на обробку даних.'),
        )
    payment_link.record_checkout_consent(client_ip(request))
    return None


def send_payment_confirmation(payment_link: PaymentLink):
    """Лист клієнту з текстом про втрату права відступлення. Без ODR."""
    email = (payment_link.client_email or '').strip()
    if not email:
        return
    try:
        body = render_to_string('payment/emails/payment_confirmation.txt', {
            'payment_link': payment_link,
        })
        send_mail(
            subject=_('Підтвердження оплати — PrometeyLabs'),
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            'Payment confirmation email failed: link=%s',
            payment_link.unique_id,
        )
