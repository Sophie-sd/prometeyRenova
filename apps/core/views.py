from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from .mixins import BasePageView, homepage_clients, portfolio_page_projects
from .form_handlers import (
    validate_phone, validate_name, create_form_response, get_form_type_from_path,
    create_form_data, send_form_email, save_form_submission,
    send_test_result_email
)
from .keycrm_service import sync_submission_to_keycrm
import logging
import threading
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def _dispatch_async(submission_id, form_data, email_sender=None):
    """
    У фоновому потоці: надсилає email і синхронізує заявку з KeyCRM.

    Робиться після того, як заявку вже збережено в БД. Це звільняє HTTP-відповідь
    від блокувань на SMTP (до 10 с) та KeyCRM API (до 15 с) — користувач бачить
    «Дякуємо» одразу, незалежно від продуктивності зовнішніх сервісів.
    """
    sender = email_sender or send_form_email

    def run():
        from django.db import close_old_connections

        close_old_connections()
        try:
            from apps.core.models import FormSubmission

            email_success, email_error = sender(form_data)
            if not email_success:
                logger.warning(
                    f"Email not sent for submission {submission_id}: {email_error}"
                )

            try:
                submission = FormSubmission.objects.get(id=submission_id)
            except FormSubmission.DoesNotExist:
                logger.error(f"Submission {submission_id} not found in async dispatch")
                return

            if email_success and not submission.email_sent:
                submission.email_sent = True
                submission.email_sent_at = timezone.now()
                submission.save(update_fields=['email_sent', 'email_sent_at'])

            sync_submission_to_keycrm(submission)
        except Exception as e:
            logger.error(f"Async dispatch error for submission {submission_id}: {e}")
        finally:
            close_old_connections()

    threading.Thread(target=run, daemon=True, name=f"submission-{submission_id}").start()


# ===== БАЗОВІ СТОРІНКИ =====

class HomeView(BasePageView):
    template_name = 'pages/home.html'
    page_title = _('PrometeyLabs - Розробка сайтів під ключ | Telegram боти | Реклама')
    meta_description = _('PrometeyLabs - професійна розробка сайтів під ключ, створення Telegram ботів, налаштування реклами Google Ads, навчання веб-розробки. Сучасні технології, конкурентні ціни.')
    og_title = _('PrometeyLabs - Розробка сайтів під ключ')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_clients'] = homepage_clients()
        return context


class PortfolioView(BasePageView):
    template_name = 'pages/portfolio.html'
    page_title = _('Портфоліо | Створені нами сайти під ключ - PrometeyLabs')
    meta_description = _('Портфоліо PrometeyLabs - приклади створених сайтів під ключ, Telegram ботів, налаштованої реклами. Подивіться на наші роботи та оцініть якість.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio_projects'] = portfolio_page_projects()
        return context


class CalculatorView(BasePageView):
    template_name = 'pages/calculator.html'
    page_title = _('Розрахувати вартість сайту | Калькулятор ціни - PrometeyLabs')
    meta_description = _('Розрахуйте вартість створення сайту онлайн. Сучасні технології знижують ціну розробки. Тест для точного розрахунку вартості проекту.')

class DeveloperView(BasePageView):
    """Landing курсів тимчасово прихований — заявки через developer-modal на інших сторінках."""

    def dispatch(self, request, *args, **kwargs):
        return redirect('home')

class ContactsView(BasePageView):
    template_name = 'pages/contacts.html'
    page_title = _('Контакти | PrometeyLabs - Зв\'яжіться з нами')
    meta_description = _('Зв\'яжіться з командою PrometeyLabs для розробки сайтів, Telegram ботів, реклами чи навчання. Київ, Україна.')

class OfferView(BasePageView):
    page_title = _('Публічна оферта на надання послуг | PrometeyLabs')
    meta_description = _('Публічна оферта на надання послуг від PrometeyLabs. Офіційні умови надання послуг веб-розробки, мобільних застосунків та маркетингу.')

    def get_template_names(self):
        from django.utils import translation
        if translation.get_language() == 'ru':
            return ['pages/offer-ru.html']
        return ['pages/offer.html']

class PrivacyView(BasePageView):
    page_title = _('Політика конфіденційності | PrometeyLabs')
    meta_description = _('Політика конфіденційності PrometeyLabs. Дізнайтеся, як ми захищаємо ваші персональні дані відповідно до законодавства України та GDPR.')

    def get_template_names(self):
        from django.utils import translation
        if translation.get_language() == 'ru':
            return ['pages/privacy-ru.html']
        return ['pages/privacy.html']

class CookiesView(BasePageView):
    page_title = _('Політика щодо файлів cookie | PrometeyLabs')
    meta_description = _('Політика щодо файлів cookie від PrometeyLabs. Дізнайтеся, які файли cookie ми використовуємо та як керувати налаштуваннями.')

    def get_template_names(self):
        from django.utils import translation
        if translation.get_language() == 'ru':
            return ['pages/cookies-ru.html']
        return ['pages/cookies.html']

class RefundPolicyView(BasePageView):
    page_title = _('Політика повернення коштів | PrometeyLabs')
    meta_description = _('Політика повернення коштів від PrometeyLabs. Дізнайтеся про умови і порядок повернення коштів за наші послуги.')

    def get_template_names(self):
        from django.utils import translation
        if translation.get_language() == 'ru':
            return ['pages/refund-ru.html']
        return ['pages/refund.html']

class IntellectualPropertyView(BasePageView):
    page_title = _('Політика щодо інтелектуальної власності | PrometeyLabs')
    meta_description = _('Політика щодо інтелектуальної власності від PrometeyLabs. Дізнайтеся про права на контент та захист авторських прав.')

    def get_template_names(self):
        from django.utils import translation
        if translation.get_language() == 'ru':
            return ['pages/intellectual-property-ru.html']
        return ['pages/intellectual-property.html']

class InternetShopView(BasePageView):
    """
    Serves the internet-shop landing page.
    URL `/internet-shop/` → Ukrainian template, UA UI.
    URL `/ru/internet-shop/` → Russian template, RU UI (i18n_patterns activates `ru`,
    so all `{% trans %}` in shared components like header/footer render in Russian).
    No redirect — the URL the user visits stays canonical.
    """
    page_title = _('Розробка інтернет-магазинів під ключ | PrometeyLabs')
    meta_description = _('Розробка інтернет-магазинів під ключ від PrometeyLabs. Кастомний код, зручна адмінка, інтеграції з платіжними системами та Новою Поштою. Міграція з Prom, Rozetka.')
    og_title = _('Інтернет-магазини під ключ — PrometeyLabs')

    def get_template_names(self):
        from django.utils import translation
        if translation.get_language() == 'ru':
            return ['pages/internet-shop-ru.html']
        return ['pages/internet-shop.html']

    def get_context_data(self, **kwargs):
        from django.utils import translation
        context = super().get_context_data(**kwargs)
        if translation.get_language() == 'ru':
            # Russian-specific overrides for SEO meta + lang-suggest popup
            context['page_title'] = 'Разработка интернет-магазинов под ключ | PrometeyLabs'
            context['meta_description'] = 'Разработка интернет-магазина под ключ от PrometeyLabs. Создание интернет-магазина с нуля, заказать интернет-магазин. Кастомный код, интеграции с платёжными системами, дропшиппинг-платформы.'
            context['og_title'] = 'Интернет-магазин под ключ — PrometeyLabs'
            context['lang_suggest_always'] = True
            context['lang_suggest_uk_url'] = '/internet-shop/'
        return context


class InternetShopRuView(BasePageView):
    """
    Legacy URL `/internet-shop-ru/` — kept for backward compatibility but 301-redirects
    to the canonical `/ru/internet-shop/` so RU language stays active site-wide.
    """
    template_name = 'pages/internet-shop-ru.html'

    def dispatch(self, request, *args, **kwargs):
        from django.shortcuts import redirect
        return redirect('/ru/internet-shop/', permanent=True)

class CorporateWebsiteView(BasePageView):
    """
    Serves the corporate-website landing page.
    URL `/corporate-website/` → Ukrainian template, UA UI.
    URL `/ru/corporate-website/` → Russian template, RU UI (i18n_patterns activates `ru`,
    so all `{% trans %}` in shared components like header/footer render in Russian).
    """
    page_title = _('Корпоративний сайт під ключ за 7 днів | Розробка сайту компанії — PrometeyLabs')
    meta_description = _('Створення корпоративного сайту під ключ. Унікальний дизайн, інтеграція з CRM, SEO + реклама Google/Facebook/TikTok у пакеті. Запуск за 7 днів. Команда досвідчених розробників. Розрахуємо вартість у брифі.')
    og_title = _('Корпоративний сайт під ключ — створимо за 7 днів | PrometeyLabs')

    def get_template_names(self):
        from django.utils import translation
        if translation.get_language() == 'ru':
            return ['pages/corporate-website-ru.html']
        return ['pages/corporate-website.html']

    def get_context_data(self, **kwargs):
        from django.utils import translation
        context = super().get_context_data(**kwargs)
        if translation.get_language() == 'ru':
            context['page_title'] = 'Корпоративный сайт под ключ за 7 дней | Разработка сайта компании — PrometeyLabs'
            context['meta_description'] = 'Создание корпоративного сайта под ключ. Уникальный дизайн, интеграция с CRM, SEO + реклама Google/Facebook/TikTok в пакете. Запуск за 7 дней. Команда опытных разработчиков. Рассчитаем стоимость в брифе.'
            context['og_title'] = 'Корпоративный сайт под ключ — создадим за 7 дней | PrometeyLabs'
            context['lang_suggest_always'] = True
            context['lang_suggest_uk_url'] = '/corporate-website/'
        return context


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

    submission_saved, submission_id, save_error = save_form_submission(
        'site-request', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save site-request submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

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

    submission_saved, submission_id, save_error = save_form_submission(
        'developer', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save developer submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

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

    submission_saved, submission_id, save_error = save_form_submission(
        'consultation', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save consultation submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

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

    submission_saved, submission_id, save_error = save_form_submission(
        'contact', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save contact submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

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
        
        submission_saved, submission_id, save_error = save_form_submission(
            'test_result', form_data, email_success=False
        )

        if not submission_saved:
            logger.error(f"Failed to save test_result submission: {save_error}")
            return create_form_response(False, _('Помилка при обробці тесту'))

        _dispatch_async(
            submission_id,
            form_data,
            email_sender=lambda _fd, _captured=test_data: send_test_result_email(_captured),
        )

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

    submission_saved, submission_id, save_error = save_form_submission(
        'call-request', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save call-request submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

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

    submission_saved, submission_id, save_error = save_form_submission(
        'footer-consultation', form_data, email_success=False
    )

    if not submission_saved:
        logger.error(f"Failed to save footer-consultation submission: {save_error}")
        return create_form_response(False, _('Помилка при збереженні заявки. Спробуйте ще раз.'))

    _dispatch_async(submission_id, form_data)

    return create_form_response(
        True,
        _('Дякуємо! Ми зв\'яжемося з вами найближчим часом.'),
        redirect='/thank-you/'
    )

