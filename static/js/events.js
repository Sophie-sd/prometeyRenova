// ===== EVENTS PAGE JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function () {
    initVideoSystem();
    initScrollNavigation();
    initFilterSystem();
    initEventAnimations();
    initRegistrationButtons();
    initViewportHeight();
    setActiveMenuLink();
});

// ===== VIDEO SYSTEM =====
function initVideoSystem() {
    const videos = document.querySelectorAll('.video-background');

    videos.forEach(video => {
        // Автопрогравання
        video.play().catch(error => {
            console.log('Video autoplay failed:', error);
        });

        // Обробка помилок
        video.addEventListener('error', function () {
            console.log('Video loading error:', video.src);
            video.style.display = 'none';
        });

        // Оптимізація для мобільних
        if (window.innerWidth <= 767) {
            video.setAttribute('playsinline', '');
            video.setAttribute('muted', '');
        }
    });

    // Зупинка при невидимості
    document.addEventListener('visibilitychange', function () {
        videos.forEach(video => {
            if (document.hidden) {
                video.pause();
            } else {
                video.play().catch(() => { });
            }
        });
    });
}

// ===== SCROLL NAVIGATION =====
function initScrollNavigation() {
    const nav = document.querySelector('.main-navigation');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function () {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }

        lastScrollTop = scrollTop;
    }, { passive: true });
}

// ===== FILTER SYSTEM =====
function initFilterSystem() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const eventsContainer = document.querySelector('.events-container');

    if (!filterButtons.length || !eventsContainer) return;

    let currentFilters = {
        category: '',
        type: '',
        sort: '-start_date'
    };

    filterButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            const filterType = this.dataset.category ? 'category' :
                this.dataset.type ? 'type' :
                    this.dataset.sort ? 'sort' : null;

            if (!filterType) return;

            const filterValue = this.dataset[filterType];

            // Оновлюємо активний стан кнопок
            const buttonGroup = this.closest('.filter-buttons');
            buttonGroup.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');

            // Оновлюємо фільтри
            currentFilters[filterType] = filterValue;

            // Застосовуємо фільтри
            applyFilters(currentFilters);
        });
    });
}

function applyFilters(filters) {
    const eventsContainer = document.querySelector('.events-container');
    if (!eventsContainer) return;

    // Показуємо індикатор завантаження
    eventsContainer.style.opacity = '0.5';

    // Формуємо URL параметри
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.type) params.append('type', filters.type);
    if (filters.sort) params.append('sort', filters.sort);

    // AJAX запит
    fetch(`/events/ajax/filter/?${params.toString()}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.events) {
                updateEventsGrid(data.events);
                updatePagination(data);
            }
        })
        .catch(error => {
            console.error('Filter error:', error);
            // Fallback - перезавантажуємо сторінку
            window.location.href = `/events/?${params.toString()}`;
        })
        .finally(() => {
            eventsContainer.style.opacity = '1';
        });
}

function updateEventsGrid(events) {
    const container = document.querySelector('.events-container');
    if (!container) return;

    container.innerHTML = '';

    if (events.length === 0) {
        container.innerHTML = `
            <div class="no-events">
                <h3 class="text-medium color-red mb-sm">Події не знайдено</h3>
                <p class="text-base">Спробуйте змінити фільтри або загляньте пізніше</p>
            </div>
        `;
        return;
    }

    events.forEach((event, index) => {
        const eventCard = createEventCard(event, index + 1);
        container.appendChild(eventCard);
    });

    // Перезапускаємо анімації
    initEventAnimations();
}

function createEventCard(event, number) {
    const card = document.createElement('article');
    card.className = 'event-card';
    card.dataset.event = number.toString().padStart(2, '0');

    const priceHtml = event.price !== 'Безкоштовно' ?
        `<span class="detail-value price-value">${event.price}</span>` :
        `<span class="detail-value free-price">Безкоштовно</span>`;

    const onlineHtml = event.is_online ?
        `<div class="detail-item">
            <span class="detail-label">Формат:</span>
            <span class="detail-value online-badge">Онлайн</span>
        </div>` : '';

    const spotsHtml = event.available_spots ?
        `<div class="detail-item">
            <span class="detail-label">Місця:</span>
            <span class="detail-value spots-available">${event.available_spots}</span>
        </div>` : '';

    const registerBtn = event.is_registration_open ?
        `<button class="register-btn btn btn-primary" data-event-id="${event.id}">Реєстрація</button>` :
        `<span class="registration-closed text-small">Реєстрація закрита</span>`;

    card.innerHTML = `
        <div class="card-header">
            <span class="event-number text-page color-red">${number.toString().padStart(2, '0')}</span>
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
                
                ${onlineHtml}
                ${spotsHtml}
            </div>
        </div>
        
        <div class="card-footer">
            <a href="${event.url}" class="event-details-link text-base color-red">
                Детальніше →
            </a>
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

    let paginationHtml = '';

    if (data.has_previous) {
        paginationHtml += `<a href="?page=${data.current_page - 1}" class="pagination-link">← Попередня</a>`;
    }

    paginationHtml += `<span class="pagination-info text-base">Сторінка ${data.current_page} з ${data.total_pages}</span>`;

    if (data.has_next) {
        paginationHtml += `<a href="?page=${data.current_page + 1}" class="pagination-link">Наступна →</a>`;
    }

    pagination.innerHTML = paginationHtml;
}

// ===== EVENT ANIMATIONS =====
function initEventAnimations() {
    const eventCards = document.querySelectorAll('.event-card');

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    eventCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `all 0.6s ease-out ${index * 0.1}s`;
        observer.observe(card);
    });
}

// ===== REGISTRATION BUTTONS =====
function initRegistrationButtons() {
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('register-btn')) {
            e.preventDefault();
            const eventId = e.target.dataset.eventId;
            if (eventId) {
                openRegistrationModal(eventId);
            }
        }
    });
}

function openRegistrationModal(eventId) {
    // Створюємо модальне вікно для реєстрації
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-backdrop"></div>
        <div class="modal-content">
            <button class="modal-close" type="button" aria-label="Закрити модальне вікно">&times;</button>
            
            <div class="modal-header">
                <h3 class="text-medium color-red mb-sm">Реєстрація на подію</h3>
                <p class="text-base mb-md">Заповніть форму для реєстрації на подію</p>
            </div>
            
            <form class="modal-form" id="event-registration-form" method="post" action="/events/registration/${eventId}/">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCSRFToken()}">
                
                <div class="form-group">
                    <label for="event-name" class="form-label">Ім'я</label>
                    <input type="text" id="event-name" name="name" class="form-input" required 
                           placeholder="Введіть ваше ім'я">
                </div>
                
                <div class="form-group">
                    <label for="event-email" class="form-label">Email</label>
                    <input type="email" id="event-email" name="email" class="form-input" required 
                           placeholder="your@email.com">
                </div>
                
                <div class="form-group">
                    <label for="event-phone" class="form-label">Телефон</label>
                    <input type="tel" id="event-phone" name="phone" class="form-input" required 
                           placeholder="+380XX XXX XX XX">
                </div>
                
                <div class="form-group">
                    <label for="event-company" class="form-label">Компанія (необов'язково)</label>
                    <input type="text" id="event-company" name="company" class="form-input" 
                           placeholder="Назва компанії">
                </div>
                
                <div class="form-group">
                    <label for="event-message" class="form-label">Додаткова інформація</label>
                    <textarea id="event-message" name="message" class="form-input" rows="3" 
                              placeholder="Ваші питання або побажання"></textarea>
                </div>
                
                <button type="submit" class="btn btn-primary form-submit">
                    Зареєструватися
                </button>
            </form>
        </div>
    `;

    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';

    // Фокус на перше поле
    setTimeout(() => {
        const firstInput = modal.querySelector('input[type="text"]');
        if (firstInput) firstInput.focus();
    }, 100);

    // Закриття модалки
    const closeBtn = modal.querySelector('.modal-close');
    const backdrop = modal.querySelector('.modal-backdrop');

    function closeModal() {
        modal.remove();
        document.body.style.overflow = '';
    }

    closeBtn.addEventListener('click', closeModal);
    backdrop.addEventListener('click', closeModal);

    // ESC для закриття
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });

    // Обробка форми
    const form = modal.querySelector('form');
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const submitBtn = form.querySelector('.form-submit');
        const originalText = submitBtn.textContent;

        submitBtn.textContent = 'Відправляємо...';
        submitBtn.disabled = true;

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
            .then(response => {
                if (response.ok) {
                    closeModal();
                    showSuccessMessage('Реєстрація успішна! Ми зв\'яжемося з вами найближчим часом.');
                } else {
                    throw new Error('Registration failed');
                }
            })
            .catch(error => {
                console.error('Registration error:', error);
                alert('Помилка реєстрації. Спробуйте ще раз.');
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
    });
}

// ===== UTILITY FUNCTIONS =====
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function showSuccessMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'success-message';
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 15px 20px;
        border-radius: 4px;
        z-index: 10000;
        font-weight: 600;
    `;
    messageDiv.textContent = message;

    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

function initViewportHeight() {
    // Фікс для iOS Safari viewport height
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);

    window.addEventListener('resize', () => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    });
}

function setActiveMenuLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// ===== PERFORMANCE OPTIMIZATION =====
function optimizePerformance() {
    // Lazy loading для зображень
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
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

function trackEventRegistration(eventId, eventTitle) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'begin_checkout', {
            item_id: eventId,
            item_name: eventTitle,
            item_category: 'events'
        });
    }
} 