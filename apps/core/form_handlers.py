"""
Допоміжні функції для обробки форм
"""
import re
import socket
from smtplib import SMTPException, SMTPAuthenticationError, SMTPConnectError
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail, get_connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Email timeout (максимум 10 секунд)
EMAIL_TIMEOUT = 10


def validate_phone(phone):
    """
    Валідація номера телефону українського формату
    Формат: +380XXXXXXXXX (12 цифр після +38, починається з 0)
    """
    if not phone:
        return False
    
    # Очищаємо від усіх символів крім цифр та +
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Перевірка формату +380XXXXXXXXX
    # Має починатися з +380 і містити ще 9 цифр (всього 13 символів)
    pattern = r'^\+380\d{9}$'
    
    if not re.match(pattern, clean_phone):
        return False
    
    return True


def validate_name(name):
    """Валідація імені - мінімум 2 символи, хоча б одна літера, не тільки цифри"""
    if not name or len(name.strip()) < 2:
        return False
    if name.isdigit():
        return False
    if not any(c.isalpha() for c in name):
        return False
    return True


def create_form_response(success=True, message="", **extra_data):
    """Створює стандартну відповідь для AJAX форм"""
    response_data = {
        'success': success,
        'message': message
    }
    response_data.update(extra_data)
    return JsonResponse(response_data)


def get_form_type_from_path(request):
    """Визначає тип форми на основі URL або інших параметрів"""
    referer = request.META.get('HTTP_REFERER', '')
    if 'calculator' in referer:
        return 'site-request'
    elif 'developer' in referer:
        return 'developer'
    return 'consultation'  # default


def create_form_data(form_type, name, phone, request, **extra_fields):
    """Створює стандартний словник даних для форми"""
    form_data = {
        'type': form_type,
        'name': name,
        'phone': phone,
        'timestamp': timezone.now().strftime('%d.%m.%Y %H:%M'),
        'ip': request.META.get('REMOTE_ADDR', ''),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'gclid': request.POST.get('gclid', '').strip(),
        'utm_source': request.POST.get('utm_source', '').strip(),
        'utm_medium': request.POST.get('utm_medium', '').strip(),
        'utm_campaign': request.POST.get('utm_campaign', '').strip(),
        'utm_term': request.POST.get('utm_term', '').strip(),
        'utm_content': request.POST.get('utm_content', '').strip(),
    }
    form_data.update(extra_fields)
    return form_data


def send_form_email(form_data):
    """Відправка email з даними форми. Повертає (success: bool, error_message: str)"""
    try:
        subject = f"[PrometeyLabs] {form_data['type']}"
        
        # Формуємо тіло email
        message_body = f"""
Нова заявка з сайту PrometeyLabs

Тип заявки: {form_data['type']}
Дата: {form_data['timestamp']}

=== КОНТАКТНІ ДАНІ ===
Ім'я: {form_data['name']}
Телефон: {form_data['phone']}
Email: {form_data.get('email', 'Не вказано')}

=== ДЕТАЛІ ЗАЯВКИ ===
"""
        
        # Додаємо специфічні поля
        for field, value in form_data.items():
            if field not in ['type', 'name', 'phone', 'email', 'timestamp', 'ip', 'user_agent'] and value:
                field_name = {
                    'details': 'Деталі заявки',
                    'message': 'Повідомлення',
                    'course_type': 'Тип курсу',
                    'experience': 'Досвід',
                    'topic': 'Тема консультації',
                    'source_page': 'Сторінка',
                }.get(field, field.replace('_', ' ').title())
                message_body += f"{field_name}: {value}\n"
        
        message_body += f"\n=== ДОДАТКОВА ІНФОРМАЦІЯ ===\nIP: {form_data.get('ip', 'Невідомо')}\nUser Agent: {form_data.get('user_agent', 'Невідомо')}"
        
        # Створюємо connection з timeout
        connection = get_connection(timeout=EMAIL_TIMEOUT)
        
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
            connection=connection
        )
        
        logger.info(f"Email sent successfully for form type: {form_data['type']}")
        return (True, None)
        
    except (SMTPAuthenticationError, SMTPConnectError) as e:
        error_msg = f"SMTP authentication error: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except socket.timeout as e:
        error_msg = f"Email timeout (>10 seconds): {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)


def save_form_submission(form_type, form_data, email_success=False):
    """Збереження даних форми в БД. Повертає (success: bool, submission_id, error_message)"""
    try:
        from apps.core.models import FormSubmission
        
        # Основні поля
        submission_data = {
            'form_type': form_type,
            'name': form_data.get('name', ''),
            'phone': form_data.get('phone', ''),
            'email': form_data.get('email', ''),
            'ip_address': form_data.get('ip'),
            'user_agent': form_data.get('user_agent'),
            'status': 'new',
            'email_sent': email_success,
            'gclid': form_data.get('gclid', ''),
            'utm_source': form_data.get('utm_source', ''),
            'utm_medium': form_data.get('utm_medium', ''),
            'utm_campaign': form_data.get('utm_campaign', ''),
            'utm_term': form_data.get('utm_term', ''),
            'utm_content': form_data.get('utm_content', ''),
        }
        
        if email_success:
            submission_data['email_sent_at'] = timezone.now()
        
        # Деталі (текстові поля)
        detail_fields = ['details', 'message', 'topic']
        for field in detail_fields:
            if form_data.get(field):
                submission_data['details'] = form_data[field]
                break
        
        # Додаткові дані в JSON
        extra_data = {}
        extra_fields = ['course_type', 'experience', 'company', 'answers', 
                       'alt_services_checked', 'event_title']
        for field in extra_fields:
            if form_data.get(field):
                extra_data[field] = form_data[field]
        
        if extra_data:
            submission_data['extra_data'] = extra_data
        
        submission = FormSubmission.objects.create(**submission_data)
        logger.info(f"Form submission saved: ID {submission.id}, email_sent={email_success}")
        return (True, submission.id, None)
        
    except Exception as e:
        error_msg = f"Failed to save form submission: {str(e)}"
        logger.error(error_msg)
        return (False, None, error_msg)


ANSWER_TEXT_MAP = {
    'question_1': {
        'A': 'Лендінг (одна сторінка)',
        'B': 'Розширений лендінг / промо-сайт (багатосторінковий)',
        'C': 'Корпоративний сайт або сайт послуг',
        'D': 'Інтернет-магазин',
        'E': 'Веб-додаток / PWA'
    },
    'question_2': {
        'A': 'На email',
        'B': 'У месенджер (Telegram / WhatsApp / Viber)',
        'C': 'В адмін-панель сайту (простий кабінет / CRM)',
        'D': 'В існуючу CRM',
        'E': 'Відправка заявок не потрібна'
    },
    'question_3': {
        'A': 'Терміново (3–14 днів)',
        'B': 'Стандартно (7–21 день)',
        'C': 'Не поспішаю (14–28 днів)',
        'D': 'Гнучкий графік, можна підлаштуватися'
    },
    'question_4': {
        'A': 'Ні, оплата на сайті не потрібна',
        'B': 'Так, оплата карткою онлайн',
        'C': 'Так, оплата за рахунком / інвойсом',
        'D': 'Так, кілька способів оплати (картка + рахунок тощо)'
    },
    'question_5': {
        'A': 'Є тільки ідея, потрібна консультація',
        'B': 'Є повне, чітко сформульоване технічне завдання',
        'C': 'Є макети/дизайн',
        'D': 'Є логотип та брендинг',
        'E': 'Є соціальні мережі та контент'
    }
}


def get_answer_text(question, answer):
    """Повертає текст відповіді на основі коду. Підтримує як окремі значення, так і масиви"""
    question_map = ANSWER_TEXT_MAP.get(question, {})
    
    if isinstance(answer, list):
        texts = []
        for ans in answer:
            text = question_map.get(ans, f'Невідома відповідь ({ans})')
            texts.append(text)
        return ', '.join(texts)
    else:
        return question_map.get(answer, f'Невідома відповідь ({answer})')


def send_test_result_email(test_data):
    """Відправка email з результатом тесту - з повними текстами відповідей. Повертає (success: bool, error_message: str)"""
    try:
        name = test_data['name']
        phone = test_data['phone']
        answers = test_data.get('answers', {})
        alt_services_checked = test_data.get('alt_services_checked', False)
        
        # Перевіряємо, що є для відправки
        has_answers = bool(answers)
        
        # Формуємо рядок з відповідями для email
        answers_text_lines = []
        if has_answers:
            for i in range(1, 6):
                question_key = f'question_{i}'
                if question_key in answers:
                    answer = answers[question_key]
                    answer_text = get_answer_text(question_key, answer)
                    answers_text_lines.append(f"{i}. {answer_text}")
        
        answers_section = '\n'.join(answers_text_lines) if answers_text_lines else ""
        
        # Email для команди
        admin_subject = "[PrometeyLabs] Новий розрахунок проекту"
        admin_message = f"""
Новий розрахунок проекту

=== КОНТАКТ ===
Ім'я: {name}
Телефон: {phone}

=== ТИП ЗАПИТУ ===
"""
        
        # Додаємо інформацію про тип запиту
        if alt_services_checked and has_answers:
            admin_message += "Галочка: Так (потребує додаткових послуг)\nТест: Пройдений\n"
        elif alt_services_checked:
            admin_message += "Галочка: Так (потребує додаткових послуг)\nТест: Не пройдений\n"
        elif has_answers:
            admin_message += "Галочка: Ні\nТест: Пройдений\n"
        
        # Додаємо відповіді, якщо вони є
        if has_answers:
            admin_message += f"""
=== ВІДПОВІДІ НА ТЕСТ ===
{answers_section}
"""
        
        admin_message += f"""
=== ДОДАТКОВА ІНФОРМАЦІЯ ===
Дата: {timezone.now().strftime('%d.%m.%Y %H:%M')}
IP: {test_data.get('ip', 'Невідомо')}
"""
        
        # Створюємо connection з timeout
        connection = get_connection(timeout=EMAIL_TIMEOUT)
        
        send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
            connection=connection
        )
        
        logger.info(f"Test result emails sent for {name}")
        return (True, None)
        
    except (SMTPAuthenticationError, SMTPConnectError) as e:
        error_msg = f"SMTP authentication error: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except socket.timeout as e:
        error_msg = f"Email timeout (>10 seconds): {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
    except Exception as e:
        error_msg = f"Failed to send test result email: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)
