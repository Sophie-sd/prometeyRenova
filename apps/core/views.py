from django.http import JsonResponse
from .mixins import BasePageView
from .form_handlers import (
    validate_phone, create_form_response, get_form_type_from_path,
    create_form_data, send_form_email, save_form_submission,
    calculate_project_price, send_test_result_email
)
import logging

# Налаштування логування
logger = logging.getLogger(__name__)

# ===== БАЗОВІ СТОРІНКИ =====

class HomeView(BasePageView):
    template_name = 'pages/home.html'
    page_title = 'PrometeyLabs - Розробка сайтів під ключ | Telegram боти | Реклама'
    meta_description = 'PrometeyLabs - професійна розробка сайтів під ключ, створення Telegram ботів, налаштування реклами Google Ads, навчання веб-розробки. Сучасні технології, конкурентні ціни.'
    og_title = 'PrometeyLabs - Розробка сайтів під ключ'

class PortfolioView(BasePageView):
    template_name = 'pages/portfolio.html'
    page_title = 'Портфоліо | Створені нами сайти під ключ - PrometeyLabs'
    meta_description = 'Портфоліо PrometeyLabs - приклади створених сайтів під ключ, Telegram ботів, налаштованої реклами. Подивіться на наші роботи та оцініть якість.'

class CalculatorView(BasePageView):
    template_name = 'pages/calculator.html'
    page_title = 'Розрахувати вартість сайту | Калькулятор ціни - PrometeyLabs'
    meta_description = 'Розрахуйте вартість створення сайту онлайн. Сучасні технології знижують ціну розробки. Тест для точного розрахунку вартості проекту.'

class DeveloperView(BasePageView):
    template_name = 'pages/developer.html'
    page_title = 'Курси програмування | Стати веб-розробником - PrometeyLabs'
    meta_description = 'Курси програмування у PrometeyLabs. Навчання веб-розробки з нуля. Індивідуальні та групові заняття. Практичний досвід, сучасні технології.'

class ContactsView(BasePageView):
    template_name = 'pages/contacts.html'
    page_title = 'Контакти | PrometeyLabs - Зв\'яжіться з нами'
    meta_description = 'Зв\'яжіться з командою PrometeyLabs для розробки сайтів, Telegram ботів, реклами чи навчання. Київ, Україна.'


# ===== AJAX ОБРОБКА ФОРМ =====

def handle_form_submission(request):
    """Обробка AJAX форм"""
    if request.method != 'POST':
        return create_form_response(False, 'Метод не дозволений')
    
    try:
        # Отримуємо тип форми з data-form-type або окремого поля
        form_type = request.POST.get('form_type') or get_form_type_from_path(request)
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Валідація базових полів
        if not name or not phone:
            return create_form_response(False, 'Заповніть обов\'язкові поля: ім\'я та телефон')
        
        # Валідація телефону
        if not validate_phone(phone):
            return create_form_response(False, 'Введіть коректний номер телефону')
        
        # Обробка різних типів форм
        handlers = {
            'site-request': handle_site_request,
            'developer': handle_developer_request,
            'consultation': handle_consultation_request,
            'contact': handle_contact_request,
            'call_request': handle_call_request
        }
        
        handler = handlers.get(form_type)
        if handler:
            return handler(request, name, phone)
        else:
            return create_form_response(False, f'Невідомий тип форми: {form_type}')
            
    except Exception as e:
        logger.error(f"Form submission error: {e}")
        return create_form_response(False, 'Сталася помилка при обробці заявки. Спробуйте ще раз.')

# Функції get_form_type_from_path та validate_phone перенесені в form_handlers.py

def handle_site_request(request, name, phone):
    """Обробка заявки на сайт"""
    form_data = create_form_data(
        'Заявка на розробку сайту', name, phone, request,
        details=request.POST.get('details', ''),
        email=request.POST.get('email', '')
    )
    
    send_form_email(form_data)
    save_form_submission('site-request', form_data)
    
    return create_form_response(
        True, 
        'Дякуємо! Ваша заявка отримана. Ми зв\'яжемося з вами найближчим часом.',
        redirect=None
    )

def handle_developer_request(request, name, phone):
    """Обробка заявки на курси"""
    form_data = create_form_data(
        'Заявка на курси програмування', name, phone, request,
        course_type=request.POST.get('course_type', ''),
        experience=request.POST.get('experience', ''),
        email=request.POST.get('email', '')
    )
    
    send_form_email(form_data)
    save_form_submission('developer', form_data)
    
    return create_form_response(
        True,
        'Дякуємо! Ваша заявка на курси отримана. Ми надішлемо детальну інформацію.',
        redirect=None
    )

def handle_consultation_request(request, name, phone):
    """Обробка заявки на консультацію"""
    form_data = create_form_data(
        'Заявка на консультацію', name, phone, request,
        topic=request.POST.get('topic', ''),
        email=request.POST.get('email', '')
    )
    
    send_form_email(form_data)
    save_form_submission('consultation', form_data)
    
    return create_form_response(
        True,
        'Дякуємо! Наш спеціаліст зв\'яжеться з вами протягом 15 хвилин.',
        redirect=None
    )

def handle_contact_request(request, name, phone):
    """Обробка заявки зі сторінки контактів"""
    form_data = create_form_data(
        'Заявка зі сторінки контактів', name, phone, request,
        message=request.POST.get('message', ''),
        email=request.POST.get('email', '')
    )
    
    send_form_email(form_data)
    save_form_submission('contact', form_data)
    
    return create_form_response(
        True,
        'Дякуємо за ваше повідомлення! Ми зв\'яжемося з вами найближчим часом.',
        redirect=None
    )



def handle_test_submission(request):
    """Обробка тесту для калькулятора"""
    if request.method != 'POST':
        return create_form_response(False, 'Метод не дозволений')
    
    try:
        # Отримуємо відповіді на тест
        answers = {}
        for i in range(1, 6):  # 5 питань
            answer = request.POST.get(f'question_{i}')
            if answer:
                answers[f'question_{i}'] = answer
        
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        
        if not name or not phone:
            return create_form_response(False, 'Заповніть ім\'я та телефон')
        
        # Розрахунок базової ціни на основі відповідей
        base_price = calculate_project_price(answers)
        
        # Підготовка даних для email
        test_data = {
            'name': name,
            'phone': phone,
            'email': request.POST.get('email', ''),
            'answers': answers,
            'ip': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
        
        # Відправка email з результатом
        send_test_result_email(test_data, base_price)
        
        # Збереження результату в БД
        form_data = create_form_data(
            'Результат тесту калькулятора', name, phone, request,
            estimated_price=base_price,
            answers=answers
        )
        save_form_submission('test_result', form_data)
        
        return create_form_response(
            True,
            f'Дякуємо! Орієнтовна вартість проекту: {base_price} грн. Детальний розрахунок надіслано на email.',
            estimated_price=base_price,
            answers=answers
        )
        
    except Exception as e:
        logger.error(f"Test submission error: {e}")
        return create_form_response(False, 'Помилка при обробці тесту')

def handle_call_request(request, name, phone):
    """Обробка заявки на дзвінок"""
    form_data = create_form_data(
        'Замовлення дзвінка', name, phone, request
    )
    
    send_form_email(form_data)
    save_form_submission('call-request', form_data)
    
    return create_form_response(
        True, 
        'Дякуємо! Наш менеджер зателефонує вам протягом 15 хвилин.',
        redirect=None
    )

# Всі допоміжні функції перенесені в form_handlers.py для кращої організації коду
