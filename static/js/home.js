// HOME.JS - JavaScript для головної сторінки з відео

document.addEventListener('DOMContentLoaded', function () {
    // Ініціалізація всіх систем
    initVideoSystem();
    initScrollNavigation();
    initServiceAnimations();
    initModalSystem();
    initViewportHeight();
});

// Система фонових відео
function initVideoSystem() {
    const videos = document.querySelectorAll('.video-background');

    videos.forEach(video => {
        // Забезпечуємо автоплей на iOS
        video.setAttribute('playsinline', '');
        video.setAttribute('webkit-playsinline', '');
        video.muted = true;

        // Перезапуск відео при завершенні (fallback)
        video.addEventListener('ended', () => {
            video.currentTime = 0;
            video.play();
        });

        // Обробка помилок завантаження відео
        video.addEventListener('error', () => {
            console.log('Video loading error, applying fallback background');
            video.style.display = 'none';
            document.querySelector('.hero-section').style.background =
                'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)';
        });
    });

    // Оптимізація для мобільних пристроїв
    if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
        optimizeForMobile();
    }
}

// Оптимізація для мобільних
function optimizeForMobile() {
    const mobileVideo = document.querySelector('.mobile-video');
    if (mobileVideo) {
        // Зменшуємо якість для мобільних
        mobileVideo.setAttribute('preload', 'metadata');

        // Призупиняємо відео при переході в background
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                mobileVideo.pause();
            } else {
                mobileVideo.play();
            }
        });
    }
}

// Навігація з прозорим хедером для відео сторінок
function initScrollNavigation() {
    const nav = document.querySelector('.main-navigation');

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset;

        if (scrollTop > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });
}

// Анімація сервісів при скролі
function initServiceAnimations() {
    const serviceItems = document.querySelectorAll('.service-item');

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    serviceItems.forEach(item => {
        observer.observe(item);
    });
}

// Система модальних вікон
function initModalSystem() {
    // Кнопки відкриття модалок
    const modalTriggers = document.querySelectorAll('[data-modal]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = trigger.getAttribute('data-modal');
            openModal(modalId);
        });
    });

    // Кнопки закриття модалок
    const closeButtons = document.querySelectorAll('.modal-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            closeAllModals();
        });
    });

    // Закриття при кліку на backdrop
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('modal-backdrop')) {
                closeAllModals();
            }
        });
    });

    // Закриття по ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });

    // Обробка форм в модалках
    initModalForms();
}

// Відкриття модального вікна
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

        // Фокус на першому input
        const firstInput = modal.querySelector('input[type="text"], input[type="tel"]');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

// Закриття всіх модальних вікон
function closeAllModals() {
    const modals = document.querySelectorAll('.modal.active');
    modals.forEach(modal => {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
    });
    document.body.style.overflow = '';
}

// Глобальна функція для закриття конкретної модалки (викликається з HTML)
window.closeModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
};

// Обробка форм в модалках
function initModalForms() {
    const forms = document.querySelectorAll('.modal-form');

    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitButton = form.querySelector('.form-submit');
            const originalText = submitButton.textContent;

            // Показуємо стан завантаження
            submitButton.textContent = 'Відправляємо...';
            submitButton.disabled = true;

            try {
                const formData = new FormData(form);
                const response = await fetch('/forms/submit/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                if (response.ok) {
                    closeAllModals();
                    openModal('thank-you-modal');
                    form.reset();
                } else {
                    alert('Помилка відправки. Спробуйте ще раз.');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                alert('Помилка відправки. Перевірте інтернет з\'єднання.');
            } finally {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    });
}

// Viewport height для iOS Safari
function initViewportHeight() {
    function setVH() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    setVH();
    window.addEventListener('resize', setVH);
    window.addEventListener('orientationchange', () => {
        setTimeout(setVH, 100);
    });
}

// Tracking для аналітики
function trackButtonClick(buttonText) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'button_click', {
            button_text: buttonText,
            page_location: window.location.href
        });
    }
}

// Додаємо tracking до кнопок
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('btn')) {
        trackButtonClick(e.target.textContent.trim());
    }
});

// SEO Enhancement - відслідковування часу на сторінці
let timeOnPage = 0;
setInterval(() => {
    timeOnPage += 1;
    if (timeOnPage === 30 && typeof gtag !== 'undefined') {
        gtag('event', 'engaged_session', {
            time_on_page: timeOnPage
        });
    }
}, 1000); 