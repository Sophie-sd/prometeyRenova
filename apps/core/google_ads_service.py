"""
Google Ads API інтеграція для завантаження офлайн-конверсій.
Використовує GCLID для передачі даних про конверсії назад в Google Ads.
"""
import logging
from datetime import datetime, timezone
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_google_ads_client():
    """Створює та повертає клієнт Google Ads API."""
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError:
        logger.error("google-ads package not installed. Run: pip install google-ads")
        return None

    developer_token = getattr(settings, 'GOOGLE_ADS_DEVELOPER_TOKEN', '')
    client_id = getattr(settings, 'GOOGLE_ADS_CLIENT_ID', '')
    client_secret = getattr(settings, 'GOOGLE_ADS_CLIENT_SECRET', '')
    refresh_token = getattr(settings, 'GOOGLE_ADS_REFRESH_TOKEN', '')

    if not all([developer_token, client_id, client_secret, refresh_token]):
        logger.warning("Google Ads API credentials not fully configured")
        return None

    credentials = {
        'developer_token': developer_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'use_proto_plus': True,
    }

    login_customer_id = getattr(settings, 'GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')
    if login_customer_id:
        credentials['login_customer_id'] = login_customer_id

    return GoogleAdsClient.load_from_dict(credentials)


def upload_conversion(gclid, conversion_datetime_str=None, conversion_value=None):
    """
    Завантажує офлайн-конверсію в Google Ads через GCLID.
    
    Args:
        gclid: Google Click ID
        conversion_datetime_str: ISO datetime рядок (UTC). Якщо None - використовується поточний час.
        conversion_value: Значення конверсії (опціонально)
    """
    client = _get_google_ads_client()
    if not client:
        logger.warning("Google Ads client not available, skipping conversion upload")
        return

    customer_id = getattr(settings, 'GOOGLE_ADS_CUSTOMER_ID', '')
    conversion_action_id = getattr(settings, 'GOOGLE_ADS_CONVERSION_ACTION_ID', '')

    if not customer_id or not conversion_action_id:
        logger.warning("GOOGLE_ADS_CUSTOMER_ID or GOOGLE_ADS_CONVERSION_ACTION_ID not configured")
        return

    customer_id = customer_id.replace('-', '')

    if conversion_datetime_str:
        try:
            if conversion_datetime_str.endswith('Z'):
                conversion_datetime_str = conversion_datetime_str[:-1] + '+00:00'
            dt = datetime.fromisoformat(conversion_datetime_str)
        except (ValueError, TypeError):
            dt = datetime.now(timezone.utc)
    else:
        dt = datetime.now(timezone.utc)

    conversion_date_time = dt.strftime('%Y-%m-%d %H:%M:%S%z')
    if len(conversion_date_time) > 19 and conversion_date_time[-5] != '+' and conversion_date_time[-5] != '-':
        tz_offset = dt.strftime('%z')
        conversion_date_time = dt.strftime('%Y-%m-%d %H:%M:%S') + tz_offset[:3] + ':' + tz_offset[3:]

    conversion_action_resource = (
        f'customers/{customer_id}/conversionActions/{conversion_action_id}'
    )

    try:
        conversion_upload_service = client.get_service('ConversionUploadService')
        click_conversion = client.get_type('ClickConversion')

        click_conversion.gclid = gclid
        click_conversion.conversion_action = conversion_action_resource
        click_conversion.conversion_date_time = conversion_date_time

        if conversion_value is not None:
            click_conversion.conversion_value = float(conversion_value)
            click_conversion.currency_code = 'UAH'

        request = client.get_type('UploadClickConversionsRequest')
        request.customer_id = customer_id
        request.conversions.append(click_conversion)
        request.partial_failure = True

        response = conversion_upload_service.upload_click_conversions(request=request)

        if response.partial_failure_error:
            logger.error(
                f"Google Ads partial failure: {response.partial_failure_error.message}"
            )
        else:
            for result in response.results:
                logger.info(
                    f"Google Ads conversion uploaded: gclid={result.gclid}, "
                    f"action={result.conversion_action}, "
                    f"datetime={result.conversion_date_time}"
                )

    except Exception as e:
        logger.error(f"Google Ads conversion upload error: {e}")
        raise
