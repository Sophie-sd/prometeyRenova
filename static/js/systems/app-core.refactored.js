/**
 * APP-CORE.JS - Refactored v2.0 (було base.js)
 * БЕЗ дублювань, використовує централізовані системи
 * Залежності: MobileCore, Config, Storage, Analytics
 */

import CONFIG from '../core/config.js';
import { userData } from '../core/storage.js';
import analytics from '../core/analytics.js';

class PrometeyApp {
    constructor() {
        this.config = CONFIG.timing;
        this.state = {
            menuOpen: false,
            activeModal: null,
        };
        this.elements = {};

        this.init();
    }

    init() {
        if (window.MobileCore?.isInitialized()) {
            this.initWithMobileCore();
        } else {
            document.addEventListener(CONFIG.events.mobileCoreInit, () => {
                this.initWithMobileCore();
            });
        }
    }

    initWithMobileCore() {
        this.cacheElements();
        this.setupNavigation();
        this.setupMobileMenu();
        this.setupModals();
        this.setupForms();
        this.setupLanguageSwitcher();
        this.setupAccessibility();

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
    }

    cacheElements() {
        this.elements = {
            nav: document.querySelector(CONFIG.selectors.nav),
            burgerBtn: document.querySelector(CONFIG.selectors.burgerBtn),
            mobileMenu: document.querySelector(CONFIG.selectors.mobileMenu),
            mobileMenuClose: document.querySelector('.mobile-menu-close'),
            mobileNavLinks: document.querySelectorAll('.mobile-nav-link'),
            langSwitchers: document.querySelectorAll('.lang-switcher-link'),
        };
    }

    onDOMReady() {
        console.log('[PrometeyApp] Ready');
        this.emit(CONFIG.events.ready);
    }

    // ===== NAVIGATION =====
    setupNavigation() {
        if (!this.elements.nav) return;

        let ticking = false;

        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    this.elements.nav.classList.toggle('scrolled', scrollTop > this.config.scrollThreshold);
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        this.setupSmoothScroll();
    }

    setupSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href === '#') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const offsetTop = target.offsetTop - CONFIG.animation.scrollOffset;
                    window.scrollTo({ 
                        top: offsetTop, 
                        behavior: CONFIG.animation.scrollBehavior 
                    });
                }
            });
        });
    }

    // ===== MOBILE MENU =====
    setupMobileMenu() {
        const { burgerBtn, mobileMenu, mobileMenuClose, mobileNavLinks } = this.elements;

        if (!burgerBtn || !mobileMenu) return;

        burgerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMobileMenu();
        });

        mobileMenuClose?.addEventListener('click', (e) => {
            e.preventDefault();
            this.closeMobileMenu();
        });

        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => this.closeMobileMenu());
        });

        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) this.closeMobileMenu();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.menuOpen) {
                this.closeMobileMenu();
            }
        });

        // Touch optimizations через MobileCore
    }

    toggleMobileMenu() {
        this.state.menuOpen ? this.closeMobileMenu() : this.openMobileMenu();
    }

    openMobileMenu() {
        const { burgerBtn, mobileMenu } = this.elements;

        burgerBtn.classList.add('active');
        mobileMenu.classList.add('active');
        document.body.style.overflow = 'hidden';
        document.body.classList.add('menu-open');

        this.state.menuOpen = true;
        this.emit(CONFIG.events.menuOpen);
    }

    closeMobileMenu() {
        const { burgerBtn, mobileMenu } = this.elements;

        burgerBtn.classList.remove('active');
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
        document.body.classList.remove('menu-open');

        this.state.menuOpen = false;
        this.emit(CONFIG.events.menuClose);
    }

    // ===== MODALS =====
    setupModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        const closeButtons = document.querySelectorAll('.modal-close, .modal-close-specific');

        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId);
            });
        });

        closeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = button.getAttribute('data-modal-id');
                this.closeModal(modalId);
            });
        });

        document.querySelectorAll(CONFIG.selectors.modal).forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal || e.target.classList.contains('modal-backdrop')) {
                    this.closeModal(modal.id);
                }
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.activeModal) {
                this.closeModal();
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        // Prefill через централізований storage
        this.prefillModalForm(modal);

        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

        this.state.activeModal = modalId;

        // Focus
        const firstInput = modal.querySelector('input:not([type="hidden"]), textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }

        this.emit(CONFIG.events.modalOpen, { modalId });
        analytics.trackCustom('modal_open', { modal_id: modalId });
    }

    closeModal(modalId = null) {
        const modal = modalId
            ? document.getElementById(modalId)
            : document.querySelector('.modal.active');

        if (!modal) return;

        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';

        this.state.activeModal = null;
        this.emit(CONFIG.events.modalClose, { modalId: modal.id });
    }

    prefillModalForm(modal) {
        // Використовуємо централізований userData
        const user = userData.get();
        if (!user || Object.keys(user).length === 0) return;

        const nameField = modal.querySelector('input[name="name"]');
        const phoneField = modal.querySelector('input[name="phone"]');

        if (nameField && user.name) nameField.value = user.name;
        if (phoneField && user.phone) phoneField.value = user.phone;
    }

    // ===== FORMS =====
    setupForms() {
        const forms = document.querySelectorAll(CONFIG.selectors.form);

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

        // Loading state
        if (submitBtn) {
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
        }

        try {
            const formData = new FormData(form);
            const formType = form.getAttribute('data-form-type');

            // Зберігаємо user data через централізований storage
            if (formData.get('name')) userData.update('name', formData.get('name'));
            if (formData.get('phone')) userData.update('phone', formData.get('phone'));
            if (formData.get('email')) userData.update('email', formData.get('email'));

            // AJAX відправка
            const response = await this.submitForm(formData, formType);

            if (response.ok) {
                const data = await response.json();
                this.handleFormSuccess(data, formType);
                form.reset();
                this.closeModal();

                // Analytics через централізовану систему
                analytics.track(CONFIG.events.formSuccess, {
                    form_type: formType,
                });
            } else {
                throw new Error('Server error');
            }

        } catch (error) {
            console.error('Form error:', error);
            this.showNotification('Помилка відправки. Спробуйте ще раз.', 'error');
            
            analytics.track(CONFIG.events.formError, {
                error_message: error.message,
            });
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
            const value = field.value.trim();
            const isEmpty = !value;

            field.classList.toggle('error', isEmpty);
            field.setAttribute('aria-invalid', isEmpty ? 'true' : 'false');

            if (isEmpty) isValid = false;
        });

        return isValid;
    }

    async submitForm(formData, formType) {
        const url = formType === CONFIG.formTypes.test 
            ? CONFIG.endpoints.formTest 
            : CONFIG.endpoints.formSubmit;

        if (formType !== CONFIG.formTypes.test) {
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
        if (formType === CONFIG.formTypes.test && data.result) {
            this.showTestResult(data.result);
        } else {
            this.showNotification('Дякуємо! Ваша заявка відправлена.', 'success');
            this.openModal(CONFIG.modals.thankYou);
        }
    }

    showTestResult(result) {
        const modal = document.getElementById(CONFIG.modals.testResult);
        if (!modal) return;

        const projectTypeEl = modal.querySelector('#result-project-type');
        const priceEl = modal.querySelector('#result-price');
        const timelineEl = modal.querySelector('#result-timeline');

        if (projectTypeEl) projectTypeEl.textContent = result.project_type || '';
        if (priceEl) priceEl.textContent = result.price || '';
        if (timelineEl) timelineEl.textContent = result.timeline || '';

        this.openModal(CONFIG.modals.testResult);
    }

    // ===== LANGUAGE SWITCHER =====
    setupLanguageSwitcher() {
        this.elements.langSwitchers.forEach(switcher => {
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
        form.action = CONFIG.endpoints.languageSet;

        // CSRF
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

        // Next URL (clean)
        let nextUrl = window.location.pathname + window.location.search;
        nextUrl = nextUrl.replace(/^\/(uk|en)\//, '/');

        const nextInput = document.createElement('input');
        nextInput.type = 'hidden';
        nextInput.name = 'next';
        nextInput.value = nextUrl;
        form.appendChild(nextInput);

        document.body.appendChild(form);
        form.submit();

        // Analytics
        analytics.trackCustom('language_change', { language: langCode });
    }

    // ===== ACCESSIBILITY =====
    setupAccessibility() {
        // Keyboard navigation detection
        this.setupKeyboardNavigation();
        
        // Animate on scroll тепер через observers.js
        // Тут тільки базова accessibility
    }

    setupKeyboardNavigation() {
        let isTabbing = false;

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                isTabbing = true;
                document.body.classList.add('user-is-tabbing');
            }
        });

        document.addEventListener('mousedown', () => {
            isTabbing = false;
            document.body.classList.remove('user-is-tabbing');
        });
    }

    // ===== NOTIFICATIONS =====
    showNotification(message, type = 'info') {
        if (!CONFIG.features.enableNotifications) return;

        const notification = this.createNotificationElement(message, type);
        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('prometey-notification--show'), 50);
        setTimeout(() => this.removeNotification(notification), this.config.notificationDuration);
    }

    createNotificationElement(message, type) {
        const notification = document.createElement('div');
        notification.className = `prometey-notification prometey-notification--${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'polite');

        const messageSpan = document.createElement('span');
        messageSpan.textContent = message;

        const closeBtn = document.createElement('button');
        closeBtn.className = 'prometey-notification__close';
        closeBtn.textContent = '×';
        closeBtn.setAttribute('aria-label', 'Закрити');
        closeBtn.addEventListener('click', () => this.removeNotification(notification));

        notification.appendChild(messageSpan);
        notification.appendChild(closeBtn);

        return notification;
    }

    removeNotification(notification) {
        notification.classList.remove('prometey-notification--show');
        setTimeout(() => notification.remove(), 300);
    }

    // ===== UTILITIES =====
    getCSRFToken() {
        // Utils.js вже має цю логіку, але fallback тут
        if (window.PrometeyUtils?.getCSRFToken) {
            return window.PrometeyUtils.getCSRFToken();
        }

        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) return metaTag.getAttribute('content');

        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input) return input.value;

        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
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

    // ===== STATIC =====
    static getInstance() {
        if (!window.prometeyApp) {
            window.prometeyApp = new PrometeyApp();
        }
        return window.prometeyApp;
    }
}

// ===== NOTIFICATION STYLES (вже НЕ inline, в окремому CSS) =====
// Перенесено в components/notifications.css

// ===== INITIALIZATION =====
const app = PrometeyApp.getInstance();

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PrometeyApp;
}

export default PrometeyApp;

