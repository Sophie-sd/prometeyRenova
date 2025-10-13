/**
 * EVENTS.JS - Events page logic
 * Використовує: base.js, VideoSystem
 * БЕЗ дублювань та inline styles
 */

document.addEventListener('DOMContentLoaded', () => {
    initFilterSystem();
    initEventAnimations();
    initRegistrationButtons();
    setActiveMenuLink();
});

// ===== FILTER SYSTEM =====
function initFilterSystem() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const eventsContainer = document.querySelector('.events-container');

    if (!filterButtons.length || !eventsContainer) return;

    const currentFilters = {
        category: '',
        type: '',
        sort: '-start_date'
    };

    filterButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();

            const filterType = button.dataset.category ? 'category' :
                               button.dataset.type ? 'type' :
                               button.dataset.sort ? 'sort' : null;

            if (!filterType) return;

            // Оновлення active state
            const buttonGroup = button.closest('.filter-buttons');
            buttonGroup.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            button.classList.add('active');

            // Оновлення фільтрів
            currentFilters[filterType] = button.dataset[filterType];

            // Застосування
            applyFilters(currentFilters, eventsContainer);
        });
    });
}

async function applyFilters(filters, container) {
    container.classList.add('loading-state');

    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.type) params.append('type', filters.type);
    if (filters.sort) params.append('sort', filters.sort);

    try {
        const response = await fetch(`/events/ajax/filter/?${params}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        const data = await response.json();

        if (data.events) {
            updateEventsGrid(data.events, container);
            updatePagination(data);
        }
    } catch (error) {
        console.error('Filter error:', error);
        // Fallback - reload page
        window.location.href = `/events/?${params}`;
    } finally {
        container.classList.remove('loading-state');
    }
}

function updateEventsGrid(events, container) {
    container.innerHTML = '';

    if (events.length === 0) {
        container.innerHTML = `
            <div class="no-events">
                <h3 class="text-medium color-red mb-sm">Події не знайдено</h3>
                <p class="text-base">Спробуйте змінити фільтри</p>
            </div>
        `;
        return;
    }

    events.forEach((event, index) => {
        const card = createEventCard(event, index + 1);
        container.appendChild(card);
    });

    // Перезапуск анімацій
    initEventAnimations();
}

function createEventCard(event, number) {
    const card = document.createElement('article');
    card.className = 'event-card';
    card.dataset.event = number;

    const priceHtml = event.price !== 'Безкоштовно'
        ? `<span class="detail-value price-value">${event.price}</span>`
        : `<span class="detail-value free-price">Безкоштовно</span>`;

    const registerBtn = event.is_registration_open
        ? `<button class="register-btn btn btn-primary" data-event-id="${event.id}">Реєстрація</button>`
        : `<span class="registration-closed text-small">Реєстрація закрита</span>`;

    card.innerHTML = `
        <div class="card-header">
            <span class="event-number text-page color-red">${String(number).padStart(2, '0')}</span>
            <div class="event-meta">
                <time class="event-date text-small">${event.start_date}</time>
                <span class="event-type" style="background-color: ${event.category_color}">
                    ${event.event_type}
                </span>
            </div>
        </div>
        
        <div class="card-content">
            <h2 class="text-medium mb-xs">
                <a href="${event.url}" class="event-link">${event.title}</a>
            </h2>
            <p class="text-base mb-sm event-excerpt">${event.excerpt}</p>
            
            <div class="event-details">
                <div class="detail-item">
                    <span class="detail-label">Категорія:</span>
                    <span class="detail-value">${event.category_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Ціна:</span>
                    ${priceHtml}
                </div>
            </div>
        </div>
        
        <div class="card-footer">
            <a href="${event.url}" class="event-details-link text-base color-red">Детальніше →</a>
            ${registerBtn}
        </div>
    `;

    return card;
}

function updatePagination(data) {
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

// ===== EVENT ANIMATIONS =====
function initEventAnimations() {
    const cards = document.querySelectorAll('.event-card');
    if (cards.length === 0) return;
    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    cards.forEach(card => observer.observe(card));
}

// ===== REGISTRATION BUTTONS =====
function initRegistrationButtons() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.register-btn');
        if (!btn) return;

        e.preventDefault();
        const eventId = btn.dataset.eventId;
        if (eventId) {
            // Використовуємо глобальну modal систему через base.js
            openEventRegistrationModal(eventId);
        }
    });
}

function openEventRegistrationModal(eventId) {
    const modal = document.getElementById('event-registration-modal');
    if (!modal) return;

    // Встановлюємо event ID
    const eventIdInput = modal.querySelector('#event-id-input');
    if (eventIdInput) {
        eventIdInput.value = eventId;
    }

    // Відкриваємо через base.js систему
    if (window.prometeyApp) {
        window.prometeyApp.openModal('event-registration-modal');
    }
}

// ===== ACTIVE MENU =====
function setActiveMenuLink() {
    const eventsLink = document.querySelector('.nav-link[href*="events"]');
    eventsLink?.classList.add('active');
}

// ===== ANALYTICS =====
function trackEventView(eventId, eventTitle) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'view_item', {
            item_id: eventId,
            item_name: eventTitle,
            item_category: 'events'
        });
    }
}
