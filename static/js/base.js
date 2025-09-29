/* BASE.JS - Базовий JavaScript для PrometeyLabs */

// Performance monitoring (безпечне логування)
window.PrometeyPerformance = {
    start: Date.now(),
    marks: {},

    mark(name) {
        this.marks[name] = Date.now() - this.start;
    },

    log() {
        if (typeof console !== 'undefined' && console.log) {
            console.log('PrometeyLabs Performance:', this.marks);
        }
    }
};

class PrometeyApp {
    constructor() {
        window.PrometeyPerformance.mark('app-constructor');
        this.init();
    }

    init() {
        // Чекаємо ініціалізації MobileCore
        if (window.MobileCore && !window.MobileCore.isInitialized()) {
            document.addEventListener('mobilecore:initialized', () => {
                this.initWithMobileCore();
            });
        } else {
            this.initWithMobileCore();
        }
    }

    initWithMobileCore() {
        window.PrometeyPerformance.mark('init-start');

        this.device = window.MobileCore?.getDevice() || {};
        this.capabilities = window.MobileCore?.getCapabilities() || {};

        // КРИТИЧНО: Встановлюємо viewport змінні для iOS
        this.setupViewportVars();

        this.setupEventListeners();
        this.setupScrollNavigation();
        this.setupMobileMenu();
        this.setupModals();
        this.setupAnimations();

        window.PrometeyPerformance.mark('init-complete');

        // Застарілі iOS фікси замінено на MobileCore
        if (!window.MobileCore) {
            console.warn('MobileCore not found, using legacy iOS support');
            this.setupIOSSafariSupport();
        }
    }

    // Встановлення правильних viewport змінних для iOS Safari
    setupViewportVars() {
        const setViewportVars = () => {
            const vh = window.innerHeight * 0.01;
            const vw = window.innerWidth * 0.01;

            document.documentElement.style.setProperty('--vh', `${vh}px`);
            document.documentElement.style.setProperty('--vw', `${vw}px`);

            // Для iOS Safari - враховуємо URL bar
            if (this.device.iOS) {
                const availableHeight = window.innerHeight;
                document.documentElement.style.setProperty('--mobile-vh', `${availableHeight}px`);
                document.body.classList.add('ios-device');

                // URL bar detection
                if (availableHeight !== screen.height) {
                    document.body.classList.add('ios-url-bar-visible');
                } else {
                    document.body.classList.remove('ios-url-bar-visible');
                }
            }
        };

        // Встановити при завантаженні
        setViewportVars();

        // Оновлювати при зміні орієнтації та resize
        window.addEventListener('resize', setViewportVars);
        window.addEventListener('orientationchange', () => {
            // Затримка для iOS Safari
            setTimeout(setViewportVars, 100);
        });

        // Для iOS - оновлювати при скролі (URL bar hide/show)
        if (this.device.iOS) {
            let resizeTimer;
            window.addEventListener('scroll', () => {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(setViewportVars, 50);
            });
        }
    }

    // ===== НАЛАШТУВАННЯ EVENT LISTENERS =====
    setupEventListeners() {
        // Готовність DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.onDOMReady();
            });
        } else {
            this.onDOMReady();
        }

        // Обробка розміру вікна (iOS Safari)
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 100));

        // Обробка орієнтації (мобільні)
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleResize();
            }, 500);
        });
    }

    onDOMReady() {
        window.PrometeyPerformance.mark('dom-ready');
        console.log('PrometeyLabs готово до роботи');

        this.setupForms();
        this.setupSmoothScroll();

        // Логування performance через 2 секунди (після завантаження)
        setTimeout(() => {
            window.PrometeyPerformance.mark('page-loaded');
            window.PrometeyPerformance.log();
        }, 2000);
    }

    // ===== НАВІГАЦІЯ З ПРОЗОРІСТЮ =====
    setupScrollNavigation() {
        const nav = document.querySelector('.main-navigation');
        if (!nav) return;

        let isScrolling = false;

        const handleScroll = () => {
            if (!isScrolling) {
                requestAnimationFrame(() => {
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

                    if (scrollTop > 50) {
                        nav.classList.add('scrolled');
                    } else {
                        nav.classList.remove('scrolled');
                    }

                    isScrolling = false;
                });
                isScrolling = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
    }

    // ===== МОБІЛЬНЕ БУРГЕР МЕНЮ =====
    setupMobileMenu() {
        const burgerBtn = document.querySelector('.burger-menu');
        const mobileMenu = document.querySelector('.mobile-menu');
        const mobileLinks = document.querySelectorAll('.mobile-nav-link');

        if (!burgerBtn || !mobileMenu) return;

        // Відкриття/закриття меню
        burgerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMobileMenu();
        });

        // Закриття при кліку на посилання
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.closeMobileMenu();
            });
        });

        // Закриття при кліку поза меню
        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) {
                this.closeMobileMenu();
            }
        });

        // Закриття при ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
                this.closeMobileMenu();
            }
        });

        // Покращення для iOS Safari
        if ('ontouchstart' in window) {
            // Запобігання двойному тапу для зум
            let lastTouchEnd = 0;
            document.addEventListener('touchend', (e) => {
                const now = (new Date()).getTime();
                if (now - lastTouchEnd <= 300) {
                    e.preventDefault();
                }
                lastTouchEnd = now;
            }, false);

            // Покращення для мобільного меню
            mobileMenu.addEventListener('touchstart', (e) => {
                e.stopPropagation();
            }, { passive: true });

            mobileLinks.forEach(link => {
                link.addEventListener('touchstart', (e) => {
                    e.stopPropagation();
                }, { passive: true });
            });
        }
    }

    toggleMobileMenu() {
        const burgerBtn = document.querySelector('.burger-menu');
        const mobileMenu = document.querySelector('.mobile-menu');
        const body = document.body;

        if (mobileMenu.classList.contains('active')) {
            this.closeMobileMenu();
        } else {
            burgerBtn.classList.add('active');
            mobileMenu.classList.add('active');
            body.style.overflow = 'hidden';
        }
    }

    closeMobileMenu() {
        const burgerBtn = document.querySelector('.burger-menu');
        const mobileMenu = document.querySelector('.mobile-menu');
        const body = document.body;

        burgerBtn.classList.remove('active');
        mobileMenu.classList.remove('active');
        body.style.overflow = '';

        // Скидання анімацій для iOS Safari
        const mobileLinks = document.querySelectorAll('.mobile-nav-link');
        mobileLinks.forEach(link => {
            link.style.animation = 'none';
            link.offsetHeight; // trigger reflow
            link.style.animation = null;
        });
    }

    // ===== МОДАЛЬНІ ВІКНА =====
    setupModals() {
        // Кнопки відкриття модалок
        const modalTriggers = document.querySelectorAll('[data-modal]');
        const modals = document.querySelectorAll('.modal');
        const closeButtons = document.querySelectorAll('.modal-close');

        // Відкриття модалок
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId, trigger);
            });
        });

        // Закриття модалок
        closeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeModal();
            });
        });

        // Закриття при кліку на backdrop
        modals.forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        });

        // Закриття при ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    openModal(modalId, trigger = null) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        // Зберігаємо дані з тригера для pre-fill форм
        if (trigger) {
            const userData = this.getUserDataFromTrigger(trigger);
            this.prefillModalForm(modal, userData);
        }

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Фокус на першому полі форми
        const firstInput = modal.querySelector('input, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }
    }

    closeModal() {
        const activeModal = document.querySelector('.modal.active');
        if (!activeModal) return;

        activeModal.classList.remove('active');
        document.body.style.overflow = '';
    }

    getUserDataFromTrigger(trigger) {
        // Отримуємо збережені дані користувача якщо є
        const savedData = sessionStorage.getItem('prometey_user_data');
        if (savedData) {
            return JSON.parse(savedData);
        }
        return {};
    }

    prefillModalForm(modal, userData) {
        if (!userData.name && !userData.phone) return;

        const nameField = modal.querySelector('input[name="name"]');
        const phoneField = modal.querySelector('input[name="phone"]');

        if (nameField && userData.name) {
            nameField.value = userData.name;
        }
        if (phoneField && userData.phone) {
            phoneField.value = userData.phone;
        }
    }

    // ===== ФОРМИ =====
    setupForms() {
        const forms = document.querySelectorAll('form[data-form-type]');

        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit(form);
            });
        });
    }

    async handleFormSubmit(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        // Показуємо завантаження
        submitBtn.textContent = 'Відправляємо...';
        submitBtn.disabled = true;

        try {
            const formData = new FormData(form);
            const formType = form.getAttribute('data-form-type');

            // Зберігаємо дані користувача
            if (formType === 'contact' || formType === 'developer') {
                this.saveUserData(formData);
            }

            // AJAX відправка (буде реалізовано з Django views)
            const response = await this.submitForm(formData, formType);

            if (response.ok) {
                this.showSuccess('Дякуємо! Ваша заявка відправлена.');
                form.reset();
                this.closeModal();

                // Перенаправлення якщо потрібно
                if (formType === 'developer') {
                    setTimeout(() => {
                        window.location.href = '/developer/';
                    }, 1500);
                }
            } else {
                throw new Error('Помилка відправки');
            }

        } catch (error) {
            console.error('Помилка:', error);
            this.showError('Сталася помилка. Спробуйте ще раз.');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    saveUserData(formData) {
        const userData = {
            name: formData.get('name'),
            phone: formData.get('phone'),
            timestamp: Date.now()
        };
        sessionStorage.setItem('prometey_user_data', JSON.stringify(userData));
    }

    async submitForm(formData, formType) {
        // Визначаємо URL на основі типу форми
        let url;
        if (formType === 'test') {
            url = '/forms/test/';
        } else {
            url = '/forms/submit/';
            // Додаємо тип форми до formData
            formData.append('form_type', formType);
        }

        return fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        });
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // ===== ПОВІДОМЛЕННЯ =====
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Створюємо повідомлення
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;

        // Додаємо стилі якщо їх немає
        if (!document.querySelector('.notification-styles')) {
            const style = document.createElement('style');
            style.className = 'notification-styles';
            style.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 3000;
                    padding: 15px 20px;
                    background: white;
                    border: 2px solid;
                    font-weight: 600;
                    transform: translateX(400px);
                    transition: transform 0.3s ease-out;
                }
                .notification-success { border-color: #e14811; color: #e14811; }
                .notification-error { border-color: #e14811; color: #e14811; background: #ffebee; }
                .notification.show { transform: translateX(0); }
                .notification-close {
                    background: none;
                    border: none;
                    font-size: 18px;
                    margin-left: 10px;
                    cursor: pointer;
                }
            `;
            document.head.appendChild(style);
        }

        // Додаємо на сторінку
        document.body.appendChild(notification);

        // Показуємо
        setTimeout(() => notification.classList.add('show'), 100);

        // Закриття
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.removeNotification(notification);
        });

        // Автозакриття
        setTimeout(() => {
            this.removeNotification(notification);
        }, 5000);
    }

    removeNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    // ===== АНІМАЦІЇ ПРИ СКРОЛІ =====
    setupAnimations() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll');

        if (animatedElements.length === 0) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        animatedElements.forEach(el => observer.observe(el));
    }

    // ===== ПЛАВНИЙ СКРОЛ =====
    setupSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');

        links.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                const target = document.querySelector(href);

                if (target) {
                    e.preventDefault();
                    const offsetTop = target.offsetTop - 80; // Врахування header

                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // ===== iOS SAFARI ПІДТРИМКА =====
    setupIOSSafariSupport() {
        // Визначаємо iOS Safari
        const isIOSSafari = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

        if (isIOSSafari) {
            document.body.classList.add('ios-safari');
            this.fixIOSViewport();
            this.preventIOSZoom();
        }
    }

    fixIOSViewport() {
        // Фікс для viewport height на iOS Safari
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);

            // Додатковий фікс для iOS Safari
            const realVh = window.innerHeight;
            document.documentElement.style.setProperty('--real-vh', `${realVh}px`);

            // Фікс для full height секцій
            const fullHeightElements = document.querySelectorAll('.hero-section, .developer-hero, .dark-split-section');
            fullHeightElements.forEach(el => {
                el.style.height = `${realVh}px`;
            });
        };

        setVH();

        // Більш точне відслідковування змін
        window.addEventListener('resize', () => {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(setVH, 150);
        });

        window.addEventListener('orientationchange', () => {
            setTimeout(setVH, 500);
        });

        // Додатковий фікс при загрузці сторінки
        window.addEventListener('load', () => {
            setTimeout(setVH, 200);
        });

        // Фікс при scroll (iOS Safari змінює розмір)
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(setVH, 100);
        }, { passive: true });
    }

    preventIOSZoom() {
        // ЗАСТАРІЛИЙ МЕТОД - замінено на MobileCore
        // Використовуйте MobileCore.setupTouchOptimizations() замість цього
        console.warn('preventIOSZoom is deprecated, use MobileCore instead');

        // Базовий fallback тільки якщо MobileCore недоступний
        if (!window.MobileCore) {
            const inputs = document.querySelectorAll('input[type="text"], input[type="tel"], input[type="email"], textarea');
            inputs.forEach(input => {
                // Встановлюємо font-size 16px для запобігання zoom
                if (!input.style.fontSize) {
                    input.style.fontSize = '16px';
                }
            });
        }
    }

    // ===== УТИЛІТАРНІ ФУНКЦІЇ =====
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    handleResize() {
        // Обробка зміни розміру екрану
        this.fixIOSViewport();
    }

    // ===== ПУБЛІЧНІ МЕТОДИ =====
    // Для використання в інших JS файлах
    static getInstance() {
        if (!window.prometeyApp) {
            window.prometeyApp = new PrometeyApp();
        }
        return window.prometeyApp;
    }
}

// Функція зміни мови
function setLanguage(langCode) {
    // Створюємо форму для відправки POST запиту
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/i18n/set_language/';

    // CSRF токен
    let csrfToken = window.csrfToken;
    if (!csrfToken) {
        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        csrfToken = csrfTokenElement ? csrfTokenElement.value : '';
    }

    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
    }

    // Мова
    const langInput = document.createElement('input');
    langInput.type = 'hidden';
    langInput.name = 'language';
    langInput.value = langCode;
    form.appendChild(langInput);

    // Поточна сторінка
    const nextInput = document.createElement('input');
    nextInput.type = 'hidden';
    nextInput.name = 'next';
    nextInput.value = window.location.pathname;
    form.appendChild(nextInput);

    document.body.appendChild(form);
    form.submit();
}

// Ініціалізація dropdown для мобільного меню
document.addEventListener('DOMContentLoaded', function () {
    const dropdown = document.querySelector('.lang-dropdown');
    const dropdownBtn = document.querySelector('.lang-dropdown-btn');

    if (dropdownBtn) {
        dropdownBtn.addEventListener('click', function (e) {
            e.preventDefault();
            dropdown.classList.toggle('active');
        });

        // Закривати при кліку поза межами
        document.addEventListener('click', function (e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
    }
});

// Ініціалізація
const app = PrometeyApp.getInstance();

// Експорт для інших модулів
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PrometeyApp;
} 