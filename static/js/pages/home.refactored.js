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
        animateOnScroll('.service-card');
        this.setupServiceModals();
        this.setupPageSpecificTracking();
    }

    setupServiceModals() {
        document.querySelectorAll('.service-card').forEach(card => {
            card.addEventListener('click', () => {
                const serviceType = card.dataset.service;
                const modalId = `service-${serviceType}-modal`;
                const modal = document.getElementById(modalId);
                
                if (modal) {
                    modal.classList.add('active');
                    document.body.style.overflow = 'hidden';
                    
                    const closeModal = () => {
                        modal.classList.remove('active');
                        document.body.style.overflow = '';
                    };
                    
                    modal.querySelector('.modal-close').addEventListener('click', closeModal);
                    modal.querySelector('.modal-backdrop').addEventListener('click', closeModal);
                    
                    document.addEventListener('keydown', function escHandler(e) {
                        if (e.key === 'Escape') {
                            closeModal();
                            document.removeEventListener('keydown', escHandler);
                        }
                    });
                }
            });
        });
    }

    setupPageSpecificTracking() {
        document.querySelectorAll('.service-card').forEach(card => {
            card.addEventListener('click', () => {
                const serviceNum = card.dataset.service;
                analytics.trackCustom('service_card_click', {
                    service_type: serviceNum,
                });
            });
        });
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new HomePage());
} else {
    new HomePage();
}

