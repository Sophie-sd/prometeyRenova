"""
Webhook endpoints для зовнішніх інтеграцій.
Обробляє події від KeyCRM при зміні статусу картки воронки.
"""
import json
import logging
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def keycrm_webhook(request):
    """
    Приймає webhook від KeyCRM при зміні статусу картки воронки.
    Подія: lead.change_lead_status
    
    При статусі "Успешно" → завантажує конверсію в Google Ads.
    KeyCRM відправляє 3 спроби, очікує HTTP 200.
    """
    token = request.GET.get('token', '')
    expected_token = getattr(settings, 'KEYCRM_WEBHOOK_SECRET', '')

    if not expected_token or token != expected_token:
        logger.warning(f"KeyCRM webhook: invalid token from {request.META.get('REMOTE_ADDR')}")
        return HttpResponseForbidden('Invalid token')

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        logger.error("KeyCRM webhook: invalid JSON body")
        return HttpResponseBadRequest('Invalid JSON')

    event = body.get('event', '')
    context = body.get('context', {})

    logger.info(f"KeyCRM webhook received: event={event}, card_id={context.get('id')}")

    if event != 'lead.change_lead_status':
        return JsonResponse({'status': 'ok', 'message': 'event ignored'})

    success_status_id = getattr(settings, 'KEYCRM_SUCCESS_STATUS_ID', None)
    if not success_status_id:
        logger.warning("KEYCRM_SUCCESS_STATUS_ID not configured")
        return JsonResponse({'status': 'ok', 'message': 'success status not configured'})

    current_status_id = context.get('status_id')
    if str(current_status_id) != str(success_status_id):
        return JsonResponse({'status': 'ok', 'message': 'status not target'})

    card_id = context.get('id')
    if not card_id:
        return JsonResponse({'status': 'ok', 'message': 'no card_id'})

    logger.info(f"KeyCRM webhook: card {card_id} reached success status, processing conversion")

    _process_conversion(card_id, context)

    return JsonResponse({'status': 'ok', 'message': 'conversion processed'})


def _process_conversion(card_id, context):
    """
    Обробляє конверсію: дістає GCLID з KeyCRM та відправляє в Google Ads.
    """
    from .keycrm_service import KeyCRMService
    from .google_ads_service import upload_conversion

    service = KeyCRMService()

    success, card_data, error = service.get_card_with_custom_fields(card_id)
    if not success:
        logger.error(f"Failed to get card {card_id} from KeyCRM: {error}")
        return

    gclid = service.extract_gclid_from_card(card_data)

    if not gclid:
        logger.info(f"No GCLID found for card {card_id}, skipping Google Ads conversion")
        return

    conversion_time = context.get('status_changed_at') or context.get('updated_at')

    try:
        upload_conversion(gclid, conversion_time)
        logger.info(f"Google Ads conversion uploaded for card {card_id}, gclid={gclid[:20]}...")
    except Exception as e:
        logger.error(f"Google Ads conversion upload failed for card {card_id}: {e}")
