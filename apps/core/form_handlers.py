"""
Допоміжні функції для обробки форм
"""
import re
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


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
        'user_agent': request.META.get('HTTP_USER_AGENT', '')
    }
    form_data.update(extra_fields)
    return form_data


def send_form_email(form_data):
    """Відправка email з даними форми"""
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
                    'details': 'Опис проекту',
                    'message': 'Повідомлення', 
                    'course_type': 'Тип курсу',
                    'experience': 'Досвід',
                    'topic': 'Тема консультації'
                }.get(field, field.title())
                message_body += f"{field_name}: {value}\n"
        
        message_body += f"\n=== ДОДАТКОВА ІНФОРМАЦІЯ ===\nIP: {form_data.get('ip', 'Невідомо')}\nUser Agent: {form_data.get('user_agent', 'Невідомо')}"
        
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        
        logger.info(f"Email sent successfully for form type: {form_data['type']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def save_form_submission(form_type, form_data):
    """Збереження даних форми в БД (placeholder)"""
    try:
        # TODO: Реалізувати збереження в БД коли будуть створені моделі
        logger.info(f"Form data saved: {form_type} - {form_data['name']}")
        return True
    except Exception as e:
        logger.error(f"Failed to save form data: {e}")
        return False


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
    """Відправка email з результатом тесту - з повними текстами відповідей"""
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
        
        send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        
        logger.info(f"Test result emails sent for {name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send test result email: {e}")
        return False
