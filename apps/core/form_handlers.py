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
    """Базова валідація номера телефону"""
    # Прибираємо всі символи крім цифр та +
    clean_phone = re.sub(r'[^\d+]', '', phone)
    # Перевіряємо що номер має правильну довжину
    return len(clean_phone) >= 10 and len(clean_phone) <= 15


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


# Константи для калькулятора
PRICE_MAP = {
    'A': 15000,  # Веб-сайт
    'B': 8000,   # Telegram бот
    'C': 5000,   # Реклама
    'D': 25000,  # Інтернет-магазин
    'E': 35000   # Мобільний додаток
}

ANSWER_TEXT_MAP = {
    'question_1': {
        'A': 'Веб-сайт (лендінг, корпоративний сайт)',
        'B': 'Telegram бот',
        'C': 'Реклама (Google Ads, Facebook Ads)',
        'D': 'Інтернет-магазин',
        'E': 'Мобільний додаток'
    },
    'question_2': {
        'A': 'Форма на сайті',
        'B': 'Telegram бот',
        'C': 'WhatsApp/Вайбер',
        'D': 'Email',
        'E': 'Телефон'
    },
    'question_3': {
        'A': 'Терміново (3-7 днів)',
        'B': 'Стандартно (10-14 днів)',
        'C': 'Не поспішаємо (2-4 тижні)',
        'D': 'Гнучкий графік'
    },
    'question_4': {
        'A': 'Ні, тільки форма заявки',
        'B': 'Так, онлайн оплата картою',
        'C': 'Так, через термінал/касу',
        'D': 'Так, через криптовалюту',
        'E': 'Так, через розрахунковий рахунок'
    },
    'question_5': {
        'A': 'Тільки думки, потрібна консультація',
        'B': 'Є макети/дизайн',
        'C': 'Є технічне завдання',
        'D': 'Є логотип та брендинг',
        'E': 'Є соціальні мережі та контент'
    }
}


def calculate_project_price(answers):
    """Розрахунок орієнтовної ціни проекту"""
    # Базова ціна на основі першого питання
    project_type = answers.get('question_1', 'A')
    base_price = PRICE_MAP.get(project_type, 15000)
    
    # Коригування на основі інших відповідей
    urgency = answers.get('question_3', 'B')
    if urgency == 'A':  # Терміново
        base_price *= 1.5
    elif urgency == 'C':  # Не поспішаємо
        base_price *= 0.9
    
    payment = answers.get('question_4', 'A')
    if payment in ['B', 'C', 'D', 'E']:  # Потрібна оплата
        base_price += 5000
    
    return int(base_price)


def get_answer_text(question, answer):
    """Повертає текст відповіді на основі коду"""
    return ANSWER_TEXT_MAP.get(question, {}).get(answer, f'Невідома відповідь ({answer})')


def send_test_result_email(test_data, estimated_price):
    """Відправка email з результатом тесту"""
    try:
        name = test_data['name']
        phone = test_data['phone']
        answers = test_data['answers']
        
        # Email для клієнта
        if 'email' in test_data and test_data['email']:
            client_subject = "Результат розрахунку вартості проекту - PrometeyLabs"
            client_message = f"""
Дякуємо за проходження тесту!

Вітаємо, {name}!

На основі ваших відповідей, орієнтовна вартість проекту становить: {estimated_price} грн

=== ВАШІ ВІДПОВІДІ ===
{chr(10).join([f"{i+1}. {get_answer_text(f'question_{i+1}', answers.get(f'question_{i+1}', ''))}" for i in range(5)])}

=== НАСТУПНІ КРОКИ ===
1. Ми зв'яжемося з вами протягом 2 годин для уточнення деталей
2. Проведемо детальну консультацію
3. Підготуємо точне технічне завдання та фінальну ціну
4. Почнемо роботу над вашим проектом

З повагою,
Команда PrometeyLabs
Телефон: +380 XX XXX XX XX
Email: info@prometeylabs.com
"""
            
            send_mail(
                subject=client_subject,
                message=client_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_data['email']],
                fail_silently=True,
            )
        
        # Email для команди
        admin_subject = f"[PrometeyLabs] Новий розрахунок проекту - {estimated_price} грн"
        admin_message = f"""
Новий розрахунок проекту

=== КОНТАКТ ===
Ім'я: {name}
Телефон: {phone}
Email: {test_data.get('email', 'Не вказано')}

=== РЕЗУЛЬТАТ ===
Розрахована вартість: {estimated_price} грн

=== ВІДПОВІДІ ===
{chr(10).join([f"{i+1}. {get_answer_text(f'question_{i+1}', answers.get(f'question_{i+1}', ''))}" for i in range(5)])}

Дата: {timezone.now().strftime('%d.%m.%Y %H:%M')}
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
