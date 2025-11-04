/**
 * UTILS.JS - Утилітарні функції для всього проєкту
 * Версія: 2.0 - Розширена функціональність
 */

const Utils = {
    /**
     * Debounce function
     */
    debounce(func, wait = 100) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function
     */
    throttle(func, limit = 100) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Get CSRF token (multiple sources)
     */
    getCSRFToken() {
        // Method 1: Meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            const token = metaTag.getAttribute('content');
            if (token) return token;
        }

        // Method 2: Hidden input
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input?.value) return input.value;

        // Method 3: Cookie
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        if (match) return match[1];

        console.warn('CSRF token not found');
        return '';
    },

    /**
     * SessionStorage helpers з error handling
     */
    storage: {
        set(key, value) {
            try {
                sessionStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error('Storage set error:', error);
                return false;
            }
        },

        get(key, defaultValue = null) {
            try {
                const item = sessionStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error('Storage get error:', error);
                return defaultValue;
            }
        },

        remove(key) {
            try {
                sessionStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Storage remove error:', error);
                return false;
            }
        },

        clear() {
            try {
                sessionStorage.clear();
                return true;
            } catch (error) {
                console.error('Storage clear error:', error);
                return false;
            }
        }
    },

    /**
     * Element helpers
     */
    element: {
        /**
         * Кешований querySelector
         */
        cache: new Map(),

        get(selector, bustCache = false) {
            if (bustCache || !this.cache.has(selector)) {
                const element = document.querySelector(selector);
                this.cache.set(selector, element);
            }
            return this.cache.get(selector);
        },

        getAll(selector) {
            return Array.from(document.querySelectorAll(selector));
        },

        /**
         * Створення елемента з класами та атрибутами
         */
        create(tag, options = {}) {
            const element = document.createElement(tag);

            if (options.className) {
                element.className = options.className;
            }

            if (options.id) {
                element.id = options.id;
            }

            if (options.attributes) {
                Object.entries(options.attributes).forEach(([key, value]) => {
                    element.setAttribute(key, value);
                });
            }

            if (options.innerHTML) {
                element.innerHTML = options.innerHTML;
            }

            if (options.textContent) {
                element.textContent = options.textContent;
            }

            return element;
        }
    },

    /**
     * Smooth scroll до елемента
     */
    scrollTo(selector, offset = 80) {
        const element = typeof selector === 'string'
            ? document.querySelector(selector)
            : selector;

        if (!element) return;

        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    },

    /**
     * Event Bus для міжмодульної комунікації
     */
    events: {
        listeners: new Map(),

        on(eventName, callback) {
            if (!this.listeners.has(eventName)) {
                this.listeners.set(eventName, []);
            }
            this.listeners.get(eventName).push(callback);
        },

        off(eventName, callback) {
            if (!this.listeners.has(eventName)) return;

            const callbacks = this.listeners.get(eventName);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        },

        emit(eventName, data = null) {
            // Custom DOM event
            const event = new CustomEvent(eventName, { detail: data });
            document.dispatchEvent(event);

            // Internal listeners
            if (this.listeners.has(eventName)) {
                this.listeners.get(eventName).forEach(callback => {
                    callback(data);
                });
            }
        }
    },

    /**
     * Animation helpers
     */
    animation: {
        /**
         * Request animation frame wrapper
         */
        raf(callback) {
            return window.requestAnimationFrame
                ? window.requestAnimationFrame(callback)
                : setTimeout(callback, 16);
        },

        /**
         * Cancel animation frame wrapper
         */
        caf(id) {
            return window.cancelAnimationFrame
                ? window.cancelAnimationFrame(id)
                : clearTimeout(id);
        }
    },

    /**
     * Device detection
     */
    device: {
        isMobile() {
            return window.innerWidth <= 767 ||
                'ontouchstart' in window ||
                navigator.maxTouchPoints > 0;
        },

        isTablet() {
            const width = window.innerWidth;
            return width > 767 && width <= 1024;
        },

        isDesktop() {
            return window.innerWidth > 1024;
        },

        isTouch() {
            return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        }
    }
};

// Глобальний доступ
window.PrometeyUtils = Utils;

