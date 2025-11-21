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
        console.log('PrometeyLabs готово');
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
        });
    }

    async handleFormSubmit(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn?.textContent;

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

            if (response.ok) {
                const data = await response.json();

                this.handleFormSuccess(data, formType);
                form.reset();
                this.closeModal();
            } else {
                throw new Error('Server error');
            }

        } catch (error) {
            console.error('Form error:', error);
            this.showNotification('Помилка відправки. Спробуйте ще раз.', 'error');
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
                isValid = false;
            } else {
                field.classList.remove('error');
            }
        });

        return isValid;
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
            this.showNotification('Дякуємо! Ваша заявка відправлена.', 'success');
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
        console.log('Switching language to:', langCode);

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
        // Видаляємо /uk/ або /en/ з початку URL
        nextUrl = nextUrl.replace(/^\/(uk|en)\//, '/');

        console.log('Original URL:', originalUrl);
        console.log('Next URL (cleaned):', nextUrl);
        console.log('CSRF Token:', this.getCSRFToken());

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

    // ===== NOTIFICATIONS =====
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `prometey-notification prometey-notification--${type}`;

        const messageSpan = document.createElement('span');
        messageSpan.textContent = message;

        const closeBtn = document.createElement('button');
        closeBtn.className = 'prometey-notification__close';
        closeBtn.textContent = '×';
        closeBtn.setAttribute('aria-label', 'Закрити');
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
        top: auto;
        bottom: calc(var(--mobile-safe-area-bottom, 0px) + 80px);
        right: var(--space-xs);
        left: var(--space-xs);
        width: calc(100% - var(--space-xs) * 2);
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
