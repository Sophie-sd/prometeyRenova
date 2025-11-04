/**
 * EVENTS.JS - Refactored v2.0
 * Без дублювань, чиста архітектура
 */

import CONFIG from '../core/config.js';
import { animateOnScroll } from '../core/observers.js';
import analytics from '../core/analytics.js';

class EventsPage {
    constructor() {
        this.currentFilters = {
            category: '',
            type: '',
            sort: '-start_date',
        };
        
        this.init();
    }

    init() {
        // Анімації
        this.initAnimations();

        // Filter system
        this.initFilterSystem();

        // Registration buttons
        this.initRegistrationButtons();

        // Active menu
        this.setActiveMenuLink();
    }

    initAnimations() {
        animateOnScroll('.event-card');
    }

    initFilterSystem() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        const eventsContainer = document.querySelector('.events-container');

        if (!filterButtons.length || !eventsContainer) return;

        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleFilterClick(button, eventsContainer);
            });
        });
    }

    handleFilterClick(button, container) {
        const filterType = this.getFilterType(button);
        if (!filterType) return;

        // Update active state
        this.updateActiveState(button);

        // Update filters
        this.currentFilters[filterType] = button.dataset[filterType];

        // Track analytics
        analytics.trackFilter(filterType, button.dataset[filterType]);

        // Apply filters
        this.applyFilters(container);
    }

    getFilterType(button) {
        if (button.dataset.category !== undefined) return 'category';
        if (button.dataset.type !== undefined) return 'type';
        if (button.dataset.sort !== undefined) return 'sort';
        return null;
    }

    updateActiveState(button) {
        const buttonGroup = button.closest('.filter-buttons');
        buttonGroup.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');
    }

    async applyFilters(container) {
        container.classList.add('loading-state');

        const params = new URLSearchParams();
        if (this.currentFilters.category) params.append('category', this.currentFilters.category);
        if (this.currentFilters.type) params.append('type', this.currentFilters.type);
        if (this.currentFilters.sort) params.append('sort', this.currentFilters.sort);

        try {
            const response = await fetch(`${CONFIG.endpoints.eventsFilter}?${params}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            const data = await response.json();

            if (data.events) {
                this.updateEventsGrid(data.events, container);
                this.updatePagination(data);
            }
        } catch (error) {
            console.error('Filter error:', error);
            // Fallback
            window.location.href = `/events/?${params}`;
        } finally {
            container.classList.remove('loading-state');
        }
    }

    updateEventsGrid(events, container) {
        container.innerHTML = '';

        if (events.length === 0) {
            container.innerHTML = `
                <div class="no-items">
                    <h3 class="text-medium color-brand-orange mb-sm">Події не знайдено</h3>
                    <p class="text-base">Спробуйте змінити фільтри</p>
                </div>
            `;
            return;
        }

        events.forEach((event, index) => {
            const card = this.createEventCard(event, index + 1);
            container.appendChild(card);
        });

        // Re-init animations для нових карток
        this.initAnimations();
    }

    createEventCard(event, number) {
        const card = document.createElement('article');
        card.className = 'event-card card';
        card.dataset.event = number;

        // Price logic
        const priceHtml = event.price !== 'Безкоштовно'
            ? `<span class="card__detail-value card__price--sale">${event.price}</span>`
            : `<span class="card__detail-value card__price--free">Безкоштовно</span>`;

        // Register button
        const registerBtn = event.is_registration_open
            ? `<button class="register-btn btn btn-primary mobile-touch-target" data-event-id="${event.id}">Реєстрація</button>`
            : `<span class="registration-closed text-small">Реєстрація закрита</span>`;

        card.innerHTML = `
            <div class="card__header">
                <span class="card__number text-page">${String(number).padStart(2, '0')}</span>
                <div class="card__meta">
                    <time class="card__date">${event.start_date}</time>
                    <span class="card__badge" style="background-color: ${event.category_color}">
                        ${event.event_type}
                    </span>
                </div>
            </div>
            
            <div class="card__content">
                <h2 class="text-medium mb-xs">
                    <a href="${event.url}" class="card__title">${event.title}</a>
                </h2>
                <p class="text-base mb-sm card__excerpt">${event.excerpt}</p>
                
                <div class="card__details">
                    <div class="card__detail-item">
                        <span class="card__detail-label">Категорія:</span>
                        <span class="card__detail-value">${event.category_name}</span>
                    </div>
                    <div class="card__detail-item">
                        <span class="card__detail-label">Ціна:</span>
                        ${priceHtml}
                    </div>
                </div>
            </div>
            
            <div class="card__footer">
                <a href="${event.url}" class="card__link">Детальніше →</a>
                ${registerBtn}
            </div>
        `;

        return card;
    }

    updatePagination(data) {
        const pagination = document.querySelector('.events-pagination');
        if (!pagination) return;

        if (data.total_pages <= 1) {
            pagination.style.display = 'none';
            return;
        }

        pagination.style.display = 'flex';

        let html = '';
        if (data.has_previous) {
            html += `<a href="?page=${data.current_page - 1}" class="pagination-link">← Попередня</a>`;
        }
        html += `<span class="pagination-info text-base">Сторінка ${data.current_page} з ${data.total_pages}</span>`;
        if (data.has_next) {
            html += `<a href="?page=${data.current_page + 1}" class="pagination-link">Наступна →</a>`;
        }

        pagination.innerHTML = html;
    }

    initRegistrationButtons() {
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.register-btn');
            if (!btn) return;

            e.preventDefault();
            const eventId = btn.dataset.eventId;
            
            if (eventId && window.prometeyApp) {
                // Встановлюємо event ID
                const modal = document.getElementById(CONFIG.modals.eventRegistration);
                const eventIdInput = modal?.querySelector('#event-id-input');
                if (eventIdInput) eventIdInput.value = eventId;

                // Відкриваємо modal
                window.prometeyApp.openModal(CONFIG.modals.eventRegistration);

                // Track
                analytics.trackCustom('event_registration_start', { event_id: eventId });
            }
        });
    }

    setActiveMenuLink() {
        const eventsLink = document.querySelector('.nav-link[href*="events"]');
        eventsLink?.classList.add('active');
    }
}

// ===== AUTO INIT =====
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new EventsPage());
} else {
    new EventsPage();
}

