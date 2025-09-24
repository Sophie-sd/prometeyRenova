/* DEVELOPER.JS - JavaScript для курсів (2025) */

document.addEventListener('DOMContentLoaded', function () {
    console.log('Developer page loaded');

    setupCourseCards();
    setupDeveloperOptimizations();

    // Чекаємо ініціалізації MobileCore
    if (window.MobileCore && window.MobileCore.isInitialized()) {
        initDeveloperWithMobileCore();
    } else {
        document.addEventListener('mobilecore:initialized', initDeveloperWithMobileCore);
    }
});

function setupCourseCards() {
    const courseCards = document.querySelectorAll('.course-card');

    courseCards.forEach(card => {
        // Desktop hover effects
        if (!('ontouchstart' in window)) {
            card.addEventListener('mouseenter', function () {
                this.style.transform = 'translateY(-5px)';
            });

            card.addEventListener('mouseleave', function () {
                this.style.transform = 'translateY(0)';
            });
        }

        // Mobile touch feedback integration
        if (window.MobileCore && window.MobileCore.getDevice().isTouch) {
            card.classList.add('mobile-touch-target');
        }
    });
}

function setupDeveloperOptimizations() {
    // Performance optimizations для відео
    const videoElements = document.querySelectorAll('.video-background');
    videoElements.forEach(video => {
        // ВИДАЛЕНО ПРОБЛЕМНИЙ КОД: video.classList.add('mobile-video');
        // Тепер CSS правила .desktop-video/.mobile-video працюватимуть правильно

        // Lazy loading для мобільних
        if (window.MobileCore && window.MobileCore.getDevice().isMobile) {
            video.setAttribute('preload', 'metadata');
        } else {
            // Для desktop - повне завантаження
            video.setAttribute('preload', 'auto');
        }
    });

    // Оптимізація анімацій на слабких пристроях
    if (window.MobileCore && window.MobileCore.getDevice().isLowEnd) {
        document.documentElement.classList.add('reduce-motion');
    }
}

function initDeveloperWithMobileCore() {
    const device = window.MobileCore.getDevice();
    const capabilities = window.MobileCore.getCapabilities();

    console.log('Initializing developer page with MobileCore', { device, capabilities });

    // Всі мобільні пристрої використовують однакові стилі
    console.log('Mobile device detected:', device.isMobile ? 'Yes' : 'No');

    // Touch device optimizations
    if (device.isTouch) {
        setupTouchDeveloperOptimizations();
    }

    // Video autoplay optimization - тільки якщо не підтримується
    if (!capabilities.canAutoplay) {
        console.log('Autoplay not supported, video will require user interaction');
        // ВИДАЛЕНО: setupVideoFallbacks(); - дозволяємо відео показуватись
    }
}

// iOS та Android використовують однакові мобільні оптимізації

function setupTouchDeveloperOptimizations() {
    // Touch-friendly кнопки
    const buttons = document.querySelectorAll('.btn, [data-modal]');
    buttons.forEach(btn => {
        btn.classList.add('mobile-touch-target');
    });

    // Haptic feedback для course cards
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach(card => {
        card.addEventListener('touchstart', () => {
            if ('vibrate' in navigator) {
                navigator.vibrate(10);
            }
        });
    });
}

// ФУНКЦІЯ setupVideoFallbacks ВИДАЛЕНА - дозволяємо відео працювати