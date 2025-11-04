/**
 * HOME.JS - Refactored v2.0
 * Без дублювань, використовує централізовані системи
 */

import { animateOnScroll } from '../core/observers.js';
import analytics from '../core/analytics.js';

class HomePage {
    constructor() {
        this.init();
    }

    init() {
        // Service cards анімація (замість дублювання IntersectionObserver)
        animateOnScroll('.service-card');

        // Analytics вже налаштована глобально в analytics.js
        // Специфічний tracking якщо потрібен
        this.setupPageSpecificTracking();
    }

    setupPageSpecificTracking() {
        // Tracking service card interactions
        document.querySelectorAll('.service-card').forEach(card => {
            card.addEventListener('click', () => {
                const serviceNum = card.dataset.service;
                analytics.trackCustom('service_card_click', {
                    service_number: serviceNum,
                });
            });
        });
    }
}

// ===== AUTO INIT =====
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new HomePage());
} else {
    new HomePage();
}

