from django.http import JsonResponse
from django.db import transaction
from .mixins import BasePageView
from .form_handlers import (
    validate_phone, validate_name, create_form_response, get_form_type_from_path,
    create_form_data, send_form_email, save_form_submission,
    send_test_result_email
)
from .keycrm_service import sync_submission_to_keycrm
import logging
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def _sync_to_keycrm(submission_id):
    """Асинхронно синхронізує заявку з KeyCRM (не блокує відповідь користувачу)."""
    try:
        from apps.core.models import FormSubmission
        submission = FormSubmission.objects.get(id=submission_id)
        sync_submission_to_keycrm(submission)
    except Exception as e:
        logger.error(f"KeyCRM sync error for submission {submission_id}: {e}")

# ===== БАЗОВІ СТОРІНКИ =====

class HomeView(BasePageView):
    template_name = 'pages/home.html'
    page_title = _('PrometeyLabs - Розробка сайтів під ключ | Telegram боти | Реклама')
    meta_description = _('PrometeyLabs - професійна розробка сайтів під ключ, створення Telegram ботів, налаштування реклами Google Ads, навчання веб-розробки. Сучасні технології, конкурентні ціни.')
    og_title = _('PrometeyLabs - Розробка сайтів під ключ')

class PortfolioView(BasePageView):
    template_name = 'pages/portfolio.html'
    page_title = _('Портфоліо | Створені нами сайти під ключ - PrometeyLabs')
    meta_description = _('Портфоліо PrometeyLabs - приклади створених сайтів під ключ, Telegram ботів, налаштованої реклами. Подивіться на наші роботи та оцініть якість.')

class CalculatorView(BasePageView):
    template_name = 'pages/calculator.html'
    page_title = _('Розрахувати вартість сайту | Калькулятор ціни - PrometeyLabs')
    meta_description = _('Розрахуйте вартість створення сайту онлайн. Сучасні технології знижують ціну розробки. Тест для точного розрахунку вартості проекту.')

class DeveloperView(BasePageView):
    template_name = 'pages/developer.html'
    page_title = _('PrometeyLabs — Навчання web-розробці та AI')
    meta_description = _('Навчання веб-розробці та AI у PrometeyLabs. Програми для новачків та розробників з досвідом. Практичне навчання, комунікація з експертами, можливість кар\'єри у нашій компанії.')

class ContactsView(BasePageView):
    template_name = 'pages/contacts.html'
    page_title = _('Контакти | PrometeyLabs - Зв\'яжіться з нами')
    meta_description = _('Зв\'яжіться з командою PrometeyLabs для розробки сайтів, Telegram ботів, реклами чи навчання. Київ, Україна.')

class OfferView(BasePageView):
    template_name = 'pages/offer.html'
    page_title = _('Публічна оферта на надання послуг | PrometeyLabs')
    meta_description = _('Публічна оферта на надання послуг від PrometeyLabs. Офіційні умови надання послуг веб-розробки, мобільних застосунків та маркетингу.')

class PrivacyView(BasePageView):
    template_name = 'pages/privacy.html'
    page_title = _('Політика конфіденційності | PrometeyLabs')
    meta_description = _('Політика конфіденційності PrometeyLabs. Дізнайтеся, як ми захищаємо ваші персональні дані відповідно до законодавства України та GDPR.')

class CookiesView(BasePageView):
    template_name = 'pages/cookies.html'
    page_title = _('Політика щодо файлів cookie | PrometeyLabs')
    meta_description = _('Політика щодо файлів cookie від PrometeyLabs. Дізнайтеся, які файли cookie ми використовуємо та як керувати налаштуваннями.')

class RefundPolicyView(BasePageView):
    template_name = 'pages/refund.html'
    page_title = _('Політика повернення коштів | PrometeyLabs')
    meta_description = _('Політика повернення коштів від PrometeyLabs. Дізнайтеся про умови і порядок повернення коштів за наші послуги.')

class IntellectualPropertyView(BasePageView):
    template_name = 'pages/intellectual-property.html'
    page_title = _('Політика щодо інтелектуальної власності | PrometeyLabs')
    meta_description = _('Політика щодо інтелектуальної власності від PrometeyLabs. Дізнайтеся про права на контент та захист авторських прав.')

class InternetShopView(BasePageView):
    template_name = 'pages/internet-shop.html'
    page_title = _('Розробка інтернет-магазинів під ключ | PrometeyLabs')
    meta_description = _('Розробка інтернет-магазинів під ключ від PrometeyLabs. Кастомний код, зручна адмінка, інтеграції з платіжними системами та Новою Поштою. Міграція з Prom, Rozetka.')
    og_title = _('Інтернет-магазини під ключ — PrometeyLabs')

class ThankYouView(BasePageView):
    template_name = 'pages/thank_you.html'
    page_title = _('Дякуємо за вашу заявку | PrometeyLabs')
    meta_description = _('Ваша заявка успішно отримана. Ми з вами скоро зв\'яжемось.')


# ===== AJAX ОБРОБКА ФОРМ =====

def handle_form_submission(request):
    """Обробка AJAX форм"""
    if request.method != 'POST':
        return create_form_response(False, _('Метод не дозволений'))
    
    try:
        # Отримуємо тип форми з data-form-type або окремого поля
        form_type = request.POST.get('form_type') or get_form_type_from_path(request)
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Валідація базових полів
        if not name or not phone:
            return create_form_response(False, _('Заповніть обов\'язкові поля: ім\'я та телефон'))
        
        # Валідація імені
        if not validate_name(name):
            return create_form_response(False, _('Введіть коректне ім\'я (мінімум 2 символи, хоча б одна літера)'))
        
        # Валідація телефону
        if not validate_phone(phone):
            return create_form_response(False, _('Введіть коректний номер телефону'))
        
        # Обробка різних типів форм
        handlers = {
            'site-request': handle_site_request,
            'site_request': handle_site_request,  # Альтернативна назва з підкреслюванням
            'developer': handle_developer_request,
            'consultation': handle_consultation_request,
            'contact': handle_contact_request,
            'call_request': handle_call_request,
            'footer-consultation': handle_footer_consultation,
            'event_registration': handle_event_registration
        }
        
        handler = handlers.get(form_type)
        if handler:
            return handler(request, name, phone)
        else:
            return create_form_response(False, _('Невідомий тип форми: {form_type}').format(form_type=form_type))
            
    except Exception as e:
        logger.error(f"Form submission error: {e}")
        return create_form_response(False, _('Сталася помилка при обробці заявки. Спробуйте ще раз.'))

# Функції get_form_type_from_path та validate_phone перенесені в form_handlers.py

def handle_site_request(request, name, phone):
    """Обробка заявки на сайт"""
    email = request.POST.get('email', '').strip()
    details = request.POST.get('details', '').strip()
    source_page = request.POST.get('source_page', '').strip()

    form_data = create_form_data(
        _('Заявка на розробку сайту'), name, phone, request,
        email=email,
        details=details,
        **(({'source_page': source_page}) if source_page else {}),
    )
    
    # Відправляємо email СПОЧАТКУ щоб дізнатися успіх
    email_success, email_error = send_form_email(form_data)
    
    if not email_success:
        logger.warning(f"Email not sent for site-request: {email_error}")
    
    # КРИТИЧНО: Спочатку зберігаємо у БД з інформацією про email успіх
    submission_saved, submission_id, save_error = save_form_submission('site-request', form_data, email_success=email_success)
    
    if not submission_saved:
        logger.error(f"Failed to save site-request submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))
    
    _sync_to_keycrm(submission_id)
    
    return create_form_response(
        True, 
        _('Дякуємо! Ваша заявка отримана. Ми зв\'яжемося з вами найближчим часом.'),
        redirect='/thank-you/'
    )

def handle_developer_request(request, name, phone):
    """Обробка заявки на курси"""
    email = request.POST.get('email', '').strip()
    course_type = request.POST.get('course_type', '').strip()
    experience = request.POST.get('experience', '').strip()
    
    form_data = create_form_data(
        _('Заявка на курси програмування'), name, phone, request,
        email=email,
        course_type=course_type,
        experience=experience
    )
    
    # Відправляємо email СПОЧАТКУ
    email_success, email_error = send_form_email(form_data)
    
    if not email_success:
        logger.warning(f"Email not sent for developer: {email_error}")
    
    # КРИТИЧНО: Зберігаємо у БД з інформацією про email успіх
    submission_saved, submission_id, save_error = save_form_submission('developer', form_data, email_success=email_success)
    
    if not submission_saved:
        logger.error(f"Failed to save developer submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))
    
    _sync_to_keycrm(submission_id)
    
    return create_form_response(
        True,
        _('Дякуємо! Ваша заявка на курси отримана. Ми надішлемо детальну інформацію.'),
        redirect='/thank-you/'
    )

def handle_consultation_request(request, name, phone):
    """Обробка заявки на консультацію"""
    email = request.POST.get('email', '').strip()
    topic = request.POST.get('topic', '').strip()
    
    form_data = create_form_data(
        _('Заявка на консультацію'), name, phone, request,
        email=email,
        topic=topic
    )
    
    # Відправляємо email СПОЧАТКУ
    email_success, email_error = send_form_email(form_data)
    
    if not email_success:
        logger.warning(f"Email not sent for consultation: {email_error}")
    
    # КРИТИЧНО: Зберігаємо у БД з інформацією про email успіх
    submission_saved, submission_id, save_error = save_form_submission('consultation', form_data, email_success=email_success)
    
    if not submission_saved:
        logger.error(f"Failed to save consultation submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))
    
    _sync_to_keycrm(submission_id)
    
    return create_form_response(
        True,
        _('Дякуємо! Наш спеціаліст зв\'яжеться з вами протягом 15 хвилин.'),
        redirect='/thank-you/'
    )

def handle_contact_request(request, name, phone):
    """Обробка заявки зі сторінки контактів"""
    email = request.POST.get('email', '').strip()
    message = request.POST.get('message', '').strip()
    
    form_data = create_form_data(
        _('Заявка зі сторінки контактів'), name, phone, request,
        email=email,
        message=message
    )
    
    # Відправляємо email СПОЧАТКУ
    email_success, email_error = send_form_email(form_data)
    
    if not email_success:
        logger.warning(f"Email not sent for contact: {email_error}")
    
    # КРИТИЧНО: Зберігаємо у БД з інформацією про email успіх
    submission_saved, submission_id, save_error = save_form_submission('contact', form_data, email_success=email_success)
    
    if not submission_saved:
        logger.error(f"Failed to save contact submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))
    
    _sync_to_keycrm(submission_id)
    
    return create_form_response(
        True,
        _('Дякуємо за ваше повідомлення! Ми зв\'яжемося з вами найближчим часом.'),
        redirect='/thank-you/'
    )



def handle_test_submission(request):
    """Обробка тесту для калькулятора"""
    if request.method != 'POST':
        return create_form_response(False, _('Метод не дозволений'))
    
    try:
        from apps.core.form_handlers import validate_name, validate_phone
        
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Валідація імені та телефону
        if not validate_name(name):
            return create_form_response(False, _('Введіть коректне ім\'я (мінімум 2 символи, хоча б одна літера)'))
        
        if not validate_phone(phone):
            return create_form_response(False, _('Введіть коректний номер телефону (мінімум 10 цифр)'))
        
        # Отримуємо відповіді на тест
        answers = {}
        # Питання 1, 3, 4 - radio (одне значення)
        for i in [1, 3, 4]:
            answer = request.POST.get(f'question_{i}')
            if answer:
                answers[f'question_{i}'] = answer
        
        # Питання 2, 5 - checkbox (масив значень)
        for i in [2, 5]:
            answers_list = request.POST.getlist(f'question_{i}')
            if answers_list:
                answers[f'question_{i}'] = answers_list
        
        # Перевіряємо, чи користувач поставив галочку "alt-services"
        alt_services_checked = request.POST.get('alt-services') == 'on'
        
        # Підготовка даних для email
        test_data = {
            'name': name,
            'phone': phone,
            'answers': answers,
            'alt_services_checked': alt_services_checked,
            'ip': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
        
        # Підготовка даних для БД
        form_data = create_form_data(
            _('Результат тесту калькулятора'), name, phone, request,
            answers=answers,
            alt_services_checked=alt_services_checked
        )
        
        # Відправка email СПОЧАТКУ
        email_success, email_error = send_test_result_email(test_data)
        
        if not email_success:
            logger.warning(f"Email not sent for test_result: {email_error}")
        
        # КРИТИЧНО: Спочатку збережемо у БД з інформацією про email успіх
        submission_saved, submission_id, save_error = save_form_submission('test_result', form_data, email_success=email_success)
        
        if not submission_saved:
            logger.error(f"Failed to save test_result submission: {save_error}")
            return create_form_response(False, _('Помилка при обробці тесту'))
        
        _sync_to_keycrm(submission_id)
        
        success_message = _('Дякуємо! Ми зв\'яжемося з вами найближчим часом.')
        
        return create_form_response(
            True,
            success_message,
            redirect='/thank-you/',
            answers=answers,
            alt_services_checked=alt_services_checked
        )
        
    except Exception as e:
        logger.error(f"Test submission error: {e}")
        return create_form_response(False, _('Помилка при обробці тесту'))

def handle_call_request(request, name, phone):
    """Обробка заявки на дзвінок"""
    form_data = create_form_data(
        _('Замовлення дзвінка'), name, phone, request
    )
    
    # Відправляємо email СПОЧАТКУ
    email_success, email_error = send_form_email(form_data)
    
    if not email_success:
        logger.warning(f"Email not sent for call-request: {email_error}")
    
    # КРИТИЧНО: Зберігаємо у БД з інформацією про email успіх
    submission_saved, submission_id, save_error = save_form_submission('call-request', form_data, email_success=email_success)
    
    if not submission_saved:
        logger.error(f"Failed to save call-request submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))
    
    _sync_to_keycrm(submission_id)
    
    return create_form_response(
        True, 
        _('Дякуємо! Наш менеджер зателефонує вам протягом 15 хвилин.'),
        redirect='/thank-you/'
    )

def handle_footer_consultation(request, name, phone):
    """Обробка заявки з footer форми консультації"""
    form_data = create_form_data(
        _('Заявка з footer - Консультація'), name, phone, request
    )
    
    # Відправляємо email СПОЧАТКУ
    email_success, email_error = send_form_email(form_data)
    
    if not email_success:
        logger.warning(f"Email not sent for footer-consultation: {email_error}")
    
    # КРИТИЧНО: Зберігаємо у БД з інформацією про email успіх
    submission_saved, submission_id, save_error = save_form_submission('footer-consultation', form_data, email_success=email_success)
    
    if not submission_saved:
        logger.error(f"Failed to save footer-consultation submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))
    
    _sync_to_keycrm(submission_id)
    
    return create_form_response(
        True,
        _('Дякуємо! Ми зв\'яжемося з вами найближчим часом.'),
        redirect='/thank-you/'
    )

@transaction.atomic
def handle_event_registration(request, name, phone):
    """Обробка реєстрації на подію через AJAX"""
    event_id = request.POST.get('event_id')
    if not event_id:
        return create_form_response(False, _('Не вказано подію для реєстрації'))
    
    try:
        event_id = int(event_id)
    except (ValueError, TypeError):
        return create_form_response(False, _('Невірний ID події'))
    
    email = request.POST.get('email', '').strip()
    company = request.POST.get('company', '').strip()
    message = request.POST.get('message', '').strip()
    
    # Валідація email
    if not email:
        return create_form_response(False, _('Введіть email'))
    
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
    except ValidationError:
        return create_form_response(False, _('Введіть коректний email'))
    
    # Імпортуємо необхідні моделі
    try:
        from apps.events.models import Event, EventRegistration
        
        event = Event.objects.select_related('category').get(id=event_id, is_published=True)
        
        # Перевірки події
        if not event.is_registration_open:
            return create_form_response(False, _('Реєстрація на цю подію закрита.'))
        
        if event.is_full:
            return create_form_response(False, _('На жаль, всі місця на цю подію вже зайняті.'))
        
        # Перевірка чи вже реєструвався
        if EventRegistration.objects.filter(event=event, email=email).exists():
            return create_form_response(False, _('Ви вже зареєстровані на цю подію.'))
        
        # КРИТИЧНО: Спочатку зберігаємо у FormSubmission
        form_data = create_form_data(
            _('Реєстрація на подію'), name, phone, request,
            email=email,
            company=company,
            message=message,
            event_title=event.title
        )
        submission_saved, submission_id, save_error = save_form_submission('event_registration', form_data, email_success=email_success)
        
        if not submission_saved:
            logger.error(f"Failed to save event_registration submission: {save_error}")
            return create_form_response(False, _('Помилка при реєстрації. Спробуйте ще раз.'))
        
        # Потім створюємо EventRegistration (яка автоматично збільшує лічильник)
        # Це все всередині @transaction.atomic, тому якщо щось пійде не так - все відкатується
        registration = EventRegistration.objects.create(
            event=event,
            name=name,
            email=email,
            phone=phone,
            company=company,
            message=message
        )
        
        # Відправка email СПОЧАТКУ
        email_success, email_error = send_form_email(form_data)
        
        if not email_success:
            logger.warning(f"Email not sent for event_registration: {email_error}")
        
        # Зберігаємо у БД з інформацією про email успіх
        submission_saved, submission_id, save_error = save_form_submission('event_registration', form_data, email_success=email_success)
        
        return create_form_response(
            True,
            _('Ви успішно зареєструвалися на подію "{event_title}"!').format(event_title=event.title),
            redirect='/thank-you/'
        )
        
    except Event.DoesNotExist:
        return create_form_response(False, _('Подію не знайдено.'))
    except Exception as e:
        logger.error(f"Event registration error: {e}")
        return create_form_response(False, _('Помилка при реєстрації. Спробуйте ще раз.'))

# Всі допоміжні функції перенесені в form_handlers.py для кращої організації коду
