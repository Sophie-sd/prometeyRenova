/**
 * OBSERVERS.JS - Централізована IntersectionObserver система
 * Замінює дублювання в home.js, blog.js, events.js, developer.js
 * Версія: 2.0
 */

import CONFIG from './config.js';

/**
 * Observer Factory - створює та керує observers
 */
class ObserverFactory {
    constructor() {
        this.observers = new Map();
        this.observedElements = new WeakMap();
    }

    /**
     * Створює intersection observer з стандартними налаштуваннями
     */
    createIntersectionObserver(options = {}) {
        const defaultOptions = {
            threshold: CONFIG.animation.intersectionThreshold,
            rootMargin: CONFIG.animation.intersectionMargin,
        };

        const mergedOptions = { ...defaultOptions, ...options };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    
                    // Опціонально: unobserve після появи (для performance)
                    if (options.once) {
                        observer.unobserve(entry.target);
                    }
                    
                    // Викликаємо callback якщо є
                    if (options.onVisible) {
                        options.onVisible(entry.target, entry);
                    }
                }
            });
        }, mergedOptions);

        return observer;
    }

    /**
     * Observe елементи з анімацією появи
     */
    observeElements(selector, options = {}) {
        if (!('IntersectionObserver' in window)) {
            // Fallback: одразу показуємо
            document.querySelectorAll(selector).forEach(el => {
                el.classList.add('visible');
            });
            return null;
        }

        const elements = document.querySelectorAll(selector);
        if (elements.length === 0) return null;

        const observer = this.createIntersectionObserver(options);

        elements.forEach(element => {
            observer.observe(element);
            this.observedElements.set(element, observer);
        });

        // Зберігаємо observer для можливості cleanup
        const observerId = `observer_${Date.now()}`;
        this.observers.set(observerId, {
            observer,
            elements: Array.from(elements),
            selector,
        });

        return observerId;
    }

    /**
     * Unobserve конкретний елемент
     */
    unobserve(element) {
        const observer = this.observedElements.get(element);
        if (observer) {
            observer.unobserve(element);
            this.observedElements.delete(element);
        }
    }

    /**
     * Cleanup - видалити observer
     */
    cleanup(observerId) {
        const data = this.observers.get(observerId);
        if (data) {
            data.elements.forEach(el => {
                data.observer.unobserve(el);
            });
            data.observer.disconnect();
            this.observers.delete(observerId);
        }
    }

    /**
     * Cleanup всіх observers
     */
    cleanupAll() {
        this.observers.forEach((data, id) => {
            this.cleanup(id);
        });
    }

    /**
     * Lazy Image Observer
     */
    observeLazyImages(selector = 'img[data-src]') {
        if (!('IntersectionObserver' in window)) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.dataset.src;
                    
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '100px',
        });

        document.querySelectorAll(selector).forEach(img => {
            observer.observe(img);
        });

        return observer;
    }

    /**
     * Scroll Progress Observer
     */
    observeScrollProgress(callback) {
        let ticking = false;

        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
                    const progress = (scrollTop / scrollHeight) * 100;

                    callback(progress, scrollTop, scrollHeight);
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });

        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }
}

// ===== GLOBAL INSTANCE (HYBRID) =====
const observerFactory = new ObserverFactory();
window.ObserverFactory = observerFactory;
window.animateOnScroll = animateOnScroll; // Для не-module скриптів

// ===== CONVENIENCE METHODS =====

/**
 * Швидкий метод для анімації карток/елементів
 */
export function animateOnScroll(selector, options = {}) {
    return observerFactory.observeElements(selector, {
        once: true,
        ...options
    });
}

/**
 * Швидкий метод для lazy loading images
 */
export function lazyLoadImages(selector) {
    return observerFactory.observeLazyImages(selector);
}

/**
 * Швидкий метод для scroll progress
 */
export function trackScrollProgress(callback) {
    return observerFactory.observeScrollProgress(callback);
}

// ===== EXPORT =====
export default observerFactory;

