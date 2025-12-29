/**
 * BASE.JS - Базовий JavaScript для PrometeyLabs
 * Рефакторинг 2025: БЕЗ дублювань, чиста архітектура
 * 
 * Залежності: MobileCore, Utils (опціонально)
 */

class PrometeyApp {
    constructor() {
        this.config = {
            scrollThreshold: 50,
            menuTransitionDuration: 400,
            notificationDuration: 5000
        };

        this.state = {
            menuOpen: false,
            activeModal: null
        };

        this.elements = {}; // Кеш DOM елементів

        this.init();
    }

    init() {
        // Чекаємо MobileCore
        if (window.MobileCore?.isInitialized()) {
            this.initWithMobileCore();
        } else {
            document.addEventListener('mobilecore:initialized', () => {
                this.initWithMobileCore();
            });
        }
    }

    initWithMobileCore() {
        // Кешуємо часто використовувані елементи
        this.cacheElements();

        // Ініціалізація систем
        this.setupNavigation();
        this.setupMobileMenu();
        this.setupModals();
        this.setupForms();
        this.setupLanguageSwitcher();
        this.setupAccessibility();
        this.setupFooterAccordion();
        this.setupScrollStateDetection();

        // DOM ready actions
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
    }

    cacheElements() {
        this.elements = {
            nav: document.querySelector('.main-navigation'),
            burgerBtn: document.querySelector('.burger-menu'),
            mobileMenu: document.querySelector('.mobile-menu'),
            mobileMenuClose: document.querySelector('.mobile-menu-close'),
            mobileNavLinks: document.querySelectorAll('.mobile-nav-link'),
            langDropdown: document.querySelector('.lang-dropdown'),
            langDropdownBtn: document.querySelector('.lang-dropdown-btn'),
            langSwitchers: document.querySelectorAll('.lang-switcher-link')
        };
    }

    onDOMReady() {
        // PrometeyLabs готово
    }

    // ===== NAVIGATION SYSTEM =====
    setupNavigation() {
        if (!this.elements.nav) return;

        let ticking = false;
        let lastScrollTop = 0;
        let isScrolled = false;

        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    const shouldBeScrolled = scrollTop > this.config.scrollThreshold;

                    if (shouldBeScrolled !== isScrolled) {
                        this.elements.nav.classList.toggle('scrolled', shouldBeScrolled);
                        isScrolled = shouldBeScrolled;
                    }

                    lastScrollTop = scrollTop;
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });

        this.setupSmoothScroll();
    }

    setupSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');

        links.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href === '#') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const offsetTop = target.offsetTop - 80;
                    window.scrollTo({ top: offsetTop, behavior: 'smooth' });
                }
            }, { passive: false }); // НЕ passive через preventDefault
        });
    }

    setupScrollStateDetection() {
        let scrollTimeout;
        let isScrolling = false;
        
        const handleScroll = () => {
            if (!isScrolling) {
                document.body.classList.add('is-scrolling');
                isScrolling = true;
            }
            
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                document.body.classList.remove('is-scrolling');
                isScrolling = false;
            }, 100);
        };
        
        window.addEventListener('scroll', handleScroll, { passive: true, capture: true });
    }

    // ===== MOBILE MENU SYSTEM =====
    setupMobileMenu() {
        const { burgerBtn, mobileMenu, mobileMenuClose, mobileNavLinks } = this.elements;

        if (!burgerBtn || !mobileMenu) return;

        // Відкриття/закриття
        burgerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMobileMenu();
        });

        // Закриття через кнопку
        mobileMenuClose?.addEventListener('click', (e) => {
            e.preventDefault();
            this.closeMobileMenu();
        });

        // Закриття при кліку на посилання
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => this.closeMobileMenu());
        });

        // Закриття при кліку на backdrop
        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) this.closeMobileMenu();
        });

        // Закриття при ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.menuOpen) {
                this.closeMobileMenu();
            }
        });

        // Touch оптимізації для iOS
        if ('ontouchstart' in window) {
            this.setupMenuTouchOptimizations();
        }
    }

    setupMenuTouchOptimizations() {
        const { mobileMenu, mobileNavLinks } = this.elements;

        mobileMenu?.addEventListener('touchstart', (e) => {
            e.stopPropagation();
        }, { passive: true });

        mobileNavLinks.forEach(link => {
            link.addEventListener('touchstart', (e) => {
                e.stopPropagation();
            }, { passive: true });
        });
    }

    toggleMobileMenu() {
        if (this.state.menuOpen) {
            this.closeMobileMenu();
        } else {
            this.openMobileMenu();
        }
    }

    openMobileMenu() {
        const { burgerBtn, mobileMenu } = this.elements;

        this.saveScrollPosition();
        burgerBtn.classList.add('active');
        mobileMenu.classList.add('active');
        document.body.style.top = `-${this.scrollPosition}px`;
        document.body.style.overflow = 'hidden';
        document.body.classList.add('menu-open');

        this.state.menuOpen = true;

        this.emit('menu:opened');
    }

    closeMobileMenu() {
        const { burgerBtn, mobileMenu } = this.elements;

        burgerBtn.classList.remove('active');
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
        document.body.style.top = '';
        document.body.classList.remove('menu-open');

        this.state.menuOpen = false;
        this.restoreScrollPosition();

        this.emit('menu:closed');
    }

    // ===== MODAL SYSTEM =====
    setupModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        const closeButtons = document.querySelectorAll('.modal-close, .modal-close-specific');

        // Відкриття модалок
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId);
            });
        });

        // Закриття модалок
        closeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = button.getAttribute('data-modal-id');
                this.closeModal(modalId);
            });
        });

        // Закриття при кліку на backdrop
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal || e.target.classList.contains('modal-backdrop')) {
                    this.closeModal(modal.id);
                }
            });
        });

        // Закриття при ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.activeModal) {
                this.closeModal();
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        this.saveScrollPosition();
        this.prefillModalForm(modal);

        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.top = `-${this.scrollPosition}px`;
        document.body.style.overflow = 'hidden';

        this.state.activeModal = modalId;

        const firstInput = modal.querySelector('input:not([type="hidden"]), textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }

        this.emit('modal:opened', { modalId });
    }

    closeModal(modalId = null) {
        const modal = modalId
            ? document.getElementById(modalId)
            : document.querySelector('.modal.active');

        if (!modal) return;

        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        document.body.style.top = '';

        this.state.activeModal = null;
        this.restoreScrollPosition();

        this.emit('modal:closed', { modalId: modal.id });
    }

    prefillModalForm(modal) {
        const userData = this.getStoredUserData();
        if (!userData) return;

        const nameField = modal.querySelector('input[name="name"]');
        const phoneField = modal.querySelector('input[name="phone"]');

        if (nameField && userData.name) nameField.value = userData.name;
        if (phoneField && userData.phone) phoneField.value = userData.phone;
    }

    // ===== FORM SYSTEM =====
    setupForms() {
        const forms = document.querySelectorAll('form[data-form-type]');

        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit(form);
            });

            // Додаємо обробники для очищення помилок при редагуванні
            const inputs = form.querySelectorAll('[required], [name="name"], [name="phone"]');
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    if (input.classList.contains('error')) {
                        input.classList.remove('error');
                        this.clearFieldError(input);
                    }
                });
            });
        });
    }

    async handleFormSubmit(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn?.textContent;

        // При помилці валідації на клієнті - форма НЕ очищається, відповіді залишаються
        if (!this.validateForm(form)) return;

        // Показуємо loading
        if (submitBtn) {
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
        }

        try {
            const formData = new FormData(form);
            const formType = form.getAttribute('data-form-type');

            // Зберігаємо дані користувача
            this.saveUserData(formData);

            // AJAX відправка
            const response = await this.submitForm(formData, formType);
            const data = await response.json();

            if (response.ok && data.success) {
                // ТІЛЬКИ при успішній відправці - очищаємо форму
                // Для тесту - виклик спеціального очищення
                if (formType === 'test' && window.calculatorInstance) {
                    window.calculatorInstance.clearForm();
                } else {
                    form.reset();
                }

                this.handleFormSuccess(data, formType);
                this.closeModal();
            } else {
                // При помилці від сервера - форма НЕ очищається, відповіді залишаються
                // Обробляємо помилку від сервера
                const errorMessage = data.message || (window.I18N?.errorSending || 'Помилка при відправці. Спробуйте ще раз.');
                
                // Перевіримо чи це помилка валідації конкретного поля
                if (errorMessage.includes('ім\'я') || errorMessage.includes('name') || errorMessage.includes('коректне ім')) {
                    const nameField = form.querySelector('[name="name"]');
                    if (nameField) {
                        nameField.classList.add('error');
                        this.showFieldError(nameField, errorMessage);
                    }
                } else if (errorMessage.includes('телефон') || errorMessage.includes('phone') || errorMessage.includes('номер')) {
                    const phoneField = form.querySelector('[name="phone"]');
                    if (phoneField) {
                        phoneField.classList.add('error');
                        this.showFieldError(phoneField, errorMessage);
                    }
                } else {
                    this.showNotification(errorMessage, 'error');
                }
            }

        } catch (error) {
            // При помилці мережі/винятку - форма НЕ очищається, відповіді залишаються
            console.error('Form error:', error);
            this.showNotification(window.I18N?.errorSubmittingForm || 'Помилка при відправці форми. Спробуйте ще раз.', 'error');
        } finally {
            if (submitBtn) {
                submitBtn.classList.remove('btn-loading');
                submitBtn.disabled = false;
                if (originalText) submitBtn.textContent = originalText;
            }
        }
    }

    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                this.showFieldError(field, 'Це поле обов\'язкове');
                isValid = false;
            } else {
                field.classList.remove('error');
                this.clearFieldError(field);
            }
        });

        // Додаткова валідація для імені та телефону (як на сервері)
        const nameField = form.querySelector('[name="name"]');
        const phoneField = form.querySelector('[name="phone"]');

        if (nameField && nameField.value) {
            const name = nameField.value.trim();
            let nameError = null;

            if (name.length < 2) {
                nameError = 'Введіть коректне ім\'я (мінімум 2 символи)';
            } else if (/^\d+$/.test(name)) {
                nameError = 'Ім\'я не може складатися тільки з цифр';
            } else if (!/\p{L}/u.test(name)) {
                nameError = 'Введіть коректне ім\'я (хоча б одна літера)';
            }

            if (nameError) {
                nameField.classList.add('error');
                this.showFieldError(nameField, nameError);
                isValid = false;
            } else {
                nameField.classList.remove('error');
                this.clearFieldError(nameField);
            }
        }

        if (phoneField && phoneField.value) {
            const phone = phoneField.value;
            const clean = phone.replace(/[^\d+]/g, '');
            const digitCount = clean.replace(/\D/g, '').length;
            let phoneError = null;

            if (digitCount < 10) {
                phoneError = 'Введіть коректний номер (мінімум 10 цифр)';
            } else if (clean.length > 20) {
                phoneError = 'Введіть коректний номер телефону';
            }

            if (phoneError) {
                phoneField.classList.add('error');
                this.showFieldError(phoneField, phoneError);
                isValid = false;
            } else {
                phoneField.classList.remove('error');
                this.clearFieldError(phoneField);
            }
        }

        return isValid;
    }

    showFieldError(field, message) {
        const errorEl = field.parentElement?.querySelector('.calc-field__error');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.add('show');
        }
    }

    clearFieldError(field) {
        const errorEl = field.parentElement?.querySelector('.calc-field__error');
        if (errorEl) {
            errorEl.textContent = '';
            errorEl.classList.remove('show');
        }
    }

    async submitForm(formData, formType) {
        const url = formType === 'test' ? '/forms/test/' : '/forms/submit/';

        if (formType !== 'test') {
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

    handleFormSuccess(data, formType) {
        if (formType === 'test' && data.result) {
            this.showTestResult(data.result);
        } else {
            this.showNotification(window.I18N?.thankYouSent || 'Дякуємо! Ваша заявка відправлена.', 'success');
            this.openModal('thank-you-modal');
        }
    }

    showTestResult(result) {
        const modal = document.getElementById('test-result-modal');
        if (!modal) return;

        // Заповнюємо результати
        const projectTypeEl = modal.querySelector('#result-project-type');
        const priceEl = modal.querySelector('#result-price');
        const timelineEl = modal.querySelector('#result-timeline');

        if (projectTypeEl) projectTypeEl.textContent = result.project_type || '';
        if (priceEl) priceEl.textContent = result.price || '';
        if (timelineEl) timelineEl.textContent = result.timeline || '';

        this.openModal('test-result-modal');
    }

    // ===== LANGUAGE SWITCHER =====
    setupLanguageSwitcher() {
        const { langDropdown, langDropdownBtn, langSwitchers } = this.elements;

        // Dropdown toggle
        langDropdownBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            langDropdown?.classList.toggle('active');
        });

        // Close dropdown при кліку поза
        document.addEventListener('click', (e) => {
            if (langDropdown && !langDropdown.contains(e.target)) {
                langDropdown.classList.remove('active');
            }
        });

        // Language switcher links
        langSwitchers.forEach(switcher => {
            switcher.addEventListener('click', (e) => {
                e.preventDefault();
                const langCode = switcher.getAttribute('data-language-code');
                if (langCode) this.setLanguage(langCode);
            });
        });
    }

    setLanguage(langCode) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/i18n/set_language/';

        // CSRF token
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = this.getCSRFToken();
        form.appendChild(csrfInput);

        // Language
        const langInput = document.createElement('input');
        langInput.type = 'hidden';
        langInput.name = 'language';
        langInput.value = langCode;
        form.appendChild(langInput);

        // Next URL - видаляємо префікс мови якщо є
        let nextUrl = window.location.pathname + window.location.search;
        const originalUrl = nextUrl;
        // Видаляємо /en/ з початку URL (uk не має префікса)
        nextUrl = nextUrl.replace(/^\/en\//, '/');

        const nextInput = document.createElement('input');
        nextInput.type = 'hidden';
        nextInput.name = 'next';
        nextInput.value = nextUrl;
        form.appendChild(nextInput);

        document.body.appendChild(form);
        form.submit();
    }

    // ===== ACCESSIBILITY =====
    setupAccessibility() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll');

        if (animatedElements.length === 0) return;
        if (!('IntersectionObserver' in window)) {
            animatedElements.forEach(el => el.classList.add('visible'));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    
                    setTimeout(() => {
                        entry.target.classList.add('animated');
                    }, 600);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.05,
            rootMargin: '0px 0px -20px 0px'
        });

        animatedElements.forEach(el => observer.observe(el));
    }

    // ===== FOOTER ACCORDION (Mobile) =====
    setupFooterAccordion() {
        const footerSections = document.querySelectorAll('.footer-section:not(.footer-form-section)');
        
        if (footerSections.length === 0) return;

        footerSections.forEach(section => {
            const heading = section.querySelector('h3');
            if (!heading) return;

            heading.addEventListener('click', () => {
                // Тільки на мобільних пристроях (< 768px)
                if (window.innerWidth >= 768) return;

                // Toggle активного стану
                section.classList.toggle('footer-accordion-active');

                // Emit подію для аналітики
                this.emit('footer:accordion-toggle', {
                    section: heading.textContent,
                    isOpen: section.classList.contains('footer-accordion-active')
                });
            });
        });

        // Закриваємо всі акордеони при зміні розміру на desktop
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 768) {
                footerSections.forEach(section => {
                    section.classList.remove('footer-accordion-active');
                });
            }
        });
    }

    // ===== NOTIFICATIONS =====
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `prometey-notification prometey-notification--${type}`;

        const messageSpan = document.createElement('span');
        messageSpan.textContent = message;

        const closeBtn = document.createElement('button');
        closeBtn.className = 'prometey-notification__close';
        closeBtn.textContent = '×';
        closeBtn.setAttribute('aria-label', window.I18N?.close || 'Закрити');
        closeBtn.addEventListener('click', () => this.removeNotification(notification));

        notification.appendChild(messageSpan);
        notification.appendChild(closeBtn);
        document.body.appendChild(notification);

        // Показуємо з анімацією
        setTimeout(() => notification.classList.add('prometey-notification--show'), 50);

        // Автозакриття
        setTimeout(() => this.removeNotification(notification), this.config.notificationDuration);
    }

    removeNotification(notification) {
        notification.classList.remove('prometey-notification--show');
        setTimeout(() => notification.remove(), 300);
    }

    // ===== SCROLL POSITION MANAGEMENT =====
    saveScrollPosition() {
        this.scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    }

    restoreScrollPosition() {
        if (this.scrollPosition !== undefined) {
            window.scrollTo({
                top: this.scrollPosition,
                behavior: 'auto'
            });
        }
    }

    // ===== UTILITY METHODS =====
    getCSRFToken() {
        // Використовуємо Utils якщо доступний
        if (window.PrometeyUtils?.getCSRFToken) {
            return window.PrometeyUtils.getCSRFToken();
        }

        // 1. Спробуємо з meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            const token = metaTag.getAttribute('content');
            if (token) return token;
        }

        // 2. Fallback на input
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input) return input.value;

        // 3. Fallback на cookie
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    saveUserData(formData) {
        const userData = {
            name: formData.get('name'),
            phone: formData.get('phone'),
            timestamp: Date.now()
        };

        try {
            sessionStorage.setItem('prometey_user_data', JSON.stringify(userData));
        } catch (error) {
            console.error('Failed to save user data:', error);
        }
    }

    getStoredUserData() {
        try {
            const data = sessionStorage.getItem('prometey_user_data');
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to get user data:', error);
            return null;
        }
    }

    // ===== EVENT BUS =====
    emit(eventName, data = null) {
        const event = new CustomEvent(eventName, { detail: data });
        document.dispatchEvent(event);
        window.dispatchEvent(event);
    }

    on(eventName, callback) {
        document.addEventListener(eventName, callback);
    }

    off(eventName, callback) {
        document.removeEventListener(eventName, callback);
    }

    // ===== STATIC METHOD =====
    static getInstance() {
        if (!window.prometeyApp) {
            window.prometeyApp = new PrometeyApp();
        }
        return window.prometeyApp;
    }
}

// ===== NOTIFICATION STYLES (одноразове додавання) =====
const notificationStyles = document.createElement('style');
notificationStyles.id = 'prometey-notification-styles';
notificationStyles.textContent = `
.prometey-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    padding: 15px 20px;
    background: var(--color-white);
    border: 2px solid var(--color-brand-orange);
    font-weight: 600;
    font-size: var(--font-base);
    transform: translateX(400px);
    transition: transform var(--transition-normal) var(--easing-default);
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: var(--shadow-lg);
}

.prometey-notification--show {
    transform: translateX(0);
}

.prometey-notification--success {
    border-color: var(--color-brand-orange);
    color: var(--color-brand-orange);
}

.prometey-notification--error {
    border-color: var(--color-brand-orange);
    color: var(--color-brand-orange);
    background: #ffebee;
}

.prometey-notification__close {
    background: none;
    border: none;
    font-size: 20px;
    line-height: 1;
    cursor: pointer;
    color: inherit;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform var(--transition-fast) var(--easing-default);
}

.prometey-notification__close:hover {
    transform: rotate(90deg);
}

@media (max-width: 767px) {
    .prometey-notification {
        top: 20px;
        right: var(--space-xs);
        left: var(--space-xs);
        width: calc(100% - var(--space-xs) * 2);
        max-width: none;
        font-size: var(--font-small);
        padding: 12px 16px;
    }
}
`;

if (!document.getElementById('prometey-notification-styles')) {
    document.head.appendChild(notificationStyles);
}

// ===== ІНІЦІАЛІЗАЦІЯ =====
const app = PrometeyApp.getInstance();

// Експорт
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PrometeyApp;
}
