/**
 * DEVELOPER.JS - Refactored v2.0
 * Мінімальна логіка
 */

import { animateOnScroll } from '../core/observers.js';
import analytics from '../core/analytics.js';

class DeveloperPage {
    constructor() {
        this.init();
    }

    init() {
        // Animations
        animateOnScroll('.course-card, .stat-item');

        // Course card interactions
        this.initCourseCards();

        // Haptic feedback
        this.initHapticFeedback();

        // Active menu
        this.setActiveMenuLink();
    }

    initCourseCards() {
        const courseCards = document.querySelectorAll('.course-card');

        courseCards.forEach(card => {
            // Touch target клас додається MobileCore
            if (window.MobileCore?.getDevice().isTouch) {
                card.classList.add('mobile-touch-target');
            }

            // Click tracking
            card.addEventListener('click', () => {
                const courseTitle = card.querySelector('.course-title')?.textContent;
                analytics.trackCustom('course_card_click', {
                    course_title: courseTitle,
                });
            });
        });
    }

    initHapticFeedback() {
        if (!('vibrate' in navigator)) return;
        if (!window.MobileCore?.getDevice().isTouch) return;

        const interactiveElements = document.querySelectorAll('.course-card, [data-modal]');

        interactiveElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                navigator.vibrate(10);
            }, { passive: true });
        });
    }

    setActiveMenuLink() {
        const developerLink = document.querySelector('.nav-link[href*="developer"]');
        developerLink?.classList.add('active');
    }
}

// ===== AUTO INIT =====
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new DeveloperPage());
} else {
    new DeveloperPage();
}

