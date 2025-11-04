/**
 * ANIMATIONS.JS - Централізовані animation utilities
 * Версія: 2.0
 */

import CONFIG from '../core/config.js';

/**
 * Animate element with CSS class
 */
export function animate(element, animationClass, duration = null) {
    return new Promise((resolve) => {
        element.classList.add(animationClass);

        const handleAnimationEnd = () => {
            element.removeEventListener('animationend', handleAnimationEnd);
            resolve();
        };

        element.addEventListener('animationend', handleAnimationEnd);

        if (duration) {
            setTimeout(() => {
                element.classList.remove(animationClass);
                resolve();
            }, duration);
        }
    });
}

/**
 * Stagger animation для списку елементів
 */
export function staggerAnimate(elements, animationClass, delay = 100) {
    elements.forEach((element, index) => {
        setTimeout(() => {
            animate(element, animationClass);
        }, index * delay);
    });
}

/**
 * Fade in element
 */
export function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms ease`;

    requestAnimationFrame(() => {
        element.style.opacity = '1';
    });

    return new Promise(resolve => {
        setTimeout(resolve, duration);
    });
}

/**
 * Fade out element
 */
export function fadeOut(element, duration = 300) {
    element.style.transition = `opacity ${duration}ms ease`;
    element.style.opacity = '0';

    return new Promise(resolve => {
        setTimeout(() => {
            element.style.display = 'none';
            resolve();
        }, duration);
    });
}

/**
 * Slide down (reveal)
 */
export function slideDown(element, duration = 300) {
    element.style.overflow = 'hidden';
    element.style.maxHeight = '0';
    element.style.transition = `max-height ${duration}ms ease`;

    requestAnimationFrame(() => {
        element.style.maxHeight = element.scrollHeight + 'px';
    });

    return new Promise(resolve => {
        setTimeout(() => {
            element.style.maxHeight = '';
            element.style.overflow = '';
            resolve();
        }, duration);
    });
}

/**
 * Slide up (hide)
 */
export function slideUp(element, duration = 300) {
    element.style.overflow = 'hidden';
    element.style.maxHeight = element.scrollHeight + 'px';
    element.style.transition = `max-height ${duration}ms ease`;

    requestAnimationFrame(() => {
        element.style.maxHeight = '0';
    });

    return new Promise(resolve => {
        setTimeout(() => {
            element.style.display = 'none';
            resolve();
        }, duration);
    });
}

/**
 * Scroll to element
 */
export function scrollToElement(element, offset = CONFIG.animation.scrollOffset) {
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
        top: offsetPosition,
        behavior: CONFIG.animation.scrollBehavior
    });
}

/**
 * Check if animations enabled
 */
export function isAnimationEnabled() {
    if (!CONFIG.features.enableAnimations) return false;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    return !prefersReducedMotion;
}

/**
 * Animation helper з перевіркою reduced motion
 */
export function safeAnimate(element, animationClass, duration = null) {
    if (!isAnimationEnabled()) {
        element.classList.add('visible');
        return Promise.resolve();
    }

    return animate(element, animationClass, duration);
}

// Export all
export default {
    animate,
    staggerAnimate,
    fadeIn,
    fadeOut,
    slideDown,
    slideUp,
    scrollToElement,
    isAnimationEnabled,
    safeAnimate,
};

