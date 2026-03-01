"""
KeyCRM API інтеграція.
Створення карток воронки та отримання даних через OpenAPI.
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

KEYCRM_BASE_URL = 'https://openapi.keycrm.app/v1'
REQUEST_TIMEOUT = 15


class KeyCRMService:
    def __init__(self):
        self.api_key = getattr(settings, 'KEYCRM_API_KEY', '')
        self.pipeline_id = getattr(settings, 'KEYCRM_PIPELINE_ID', 1)
        self.source_id = getattr(settings, 'KEYCRM_SOURCE_ID', None)
        self.gclid_field_uuid = getattr(settings, 'KEYCRM_GCLID_FIELD_UUID', '')

    @property
    def _headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    @property
    def is_configured(self):
        return bool(self.api_key)

    def create_pipeline_card(self, submission):
        """
        Створює картку у воронці KeyCRM з даних FormSubmission.
        Повертає (success: bool, card_id: int|None, error: str|None)
        """
        if not self.is_configured:
            logger.warning("KeyCRM API key not configured, skipping")
            return (False, None, "API key not configured")

        payload = {
            'pipeline_id': self.pipeline_id,
            'title': f'{submission.get_form_type_display()} - {submission.name}',
            'contact': {
                'full_name': submission.name,
                'phone': submission.phone,
            },
        }

        if submission.email:
            payload['contact']['email'] = submission.email

        if self.source_id:
            payload['source_id'] = int(self.source_id)

        if submission.utm_source:
            payload['utm_source'] = submission.utm_source
        if submission.utm_medium:
            payload['utm_medium'] = submission.utm_medium
        if submission.utm_campaign:
            payload['utm_campaign'] = submission.utm_campaign
        if submission.utm_term:
            payload['utm_term'] = submission.utm_term
        if submission.utm_content:
            payload['utm_content'] = submission.utm_content

        if submission.gclid and self.gclid_field_uuid:
            payload['custom_fields'] = [{
                'uuid': self.gclid_field_uuid,
                'value': submission.gclid,
            }]

        comment_parts = []
        if submission.details:
            comment_parts.append(submission.details)
        comment_parts.append(f'Form: {submission.form_type}')
        comment_parts.append(f'Site ID: {submission.id}')
        if submission.gclid:
            comment_parts.append(f'GCLID: {submission.gclid}')
        payload['manager_comment'] = '\n'.join(comment_parts)

        try:
            response = requests.post(
                f'{KEYCRM_BASE_URL}/pipelines/cards',
                json=payload,
                headers=self._headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code in (200, 201):
                data = response.json()
                card_id = data.get('id')
                logger.info(f"KeyCRM card created: {card_id} for submission {submission.id}")
                return (True, card_id, None)
            else:
                error = f"KeyCRM API error {response.status_code}: {response.text[:300]}"
                logger.error(error)
                return (False, None, error)

        except requests.Timeout:
            error = "KeyCRM API timeout"
            logger.error(error)
            return (False, None, error)
        except requests.RequestException as e:
            error = f"KeyCRM API request failed: {str(e)}"
            logger.error(error)
            return (False, None, error)

    def get_card_with_custom_fields(self, card_id):
        """
        Отримує картку воронки з кастомними полями.
        Повертає (success, data_dict|None, error)
        """
        if not self.is_configured:
            return (False, None, "API key not configured")

        try:
            response = requests.get(
                f'{KEYCRM_BASE_URL}/pipelines/cards/{card_id}',
                params={'include': 'custom_fields'},
                headers=self._headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                return (True, response.json(), None)
            else:
                error = f"KeyCRM GET card error {response.status_code}: {response.text[:300]}"
                logger.error(error)
                return (False, None, error)

        except requests.RequestException as e:
            error = f"KeyCRM GET card failed: {str(e)}"
            logger.error(error)
            return (False, None, error)

    def extract_gclid_from_card(self, card_data):
        """Витягує GCLID з кастомних полів картки."""
        custom_fields = card_data.get('custom_fields', [])
        if not custom_fields:
            return None

        for field in custom_fields:
            if field.get('uuid') == self.gclid_field_uuid:
                return field.get('value')

        for field in custom_fields:
            name = (field.get('name') or '').lower()
            if 'gclid' in name:
                return field.get('value')

        return None


def sync_submission_to_keycrm(submission):
    """
    Хелпер: синхронізує FormSubmission з KeyCRM.
    Оновлює keycrm_card_id та keycrm_synced на submission.
    """
    service = KeyCRMService()
    if not service.is_configured:
        return

    success, card_id, error = service.create_pipeline_card(submission)

    if success and card_id:
        submission.keycrm_card_id = card_id
        submission.keycrm_synced = True
        submission.save(update_fields=['keycrm_card_id', 'keycrm_synced'])
        logger.info(f"Submission {submission.id} synced to KeyCRM card {card_id}")
    elif error:
        logger.error(f"Failed to sync submission {submission.id} to KeyCRM: {error}")
