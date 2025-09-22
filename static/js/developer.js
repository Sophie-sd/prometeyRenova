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
        video.classList.add('mobile-video');

        // Lazy loading для мобільних
        if (window.MobileCore && window.MobileCore.getDevice().isMobile) {
            video.setAttribute('preload', 'metadata');
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

    // Video autoplay optimization
    if (!capabilities.canAutoplay) {
        setupVideoFallbacks();
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

function setupVideoFallbacks() {
    const videos = document.querySelectorAll('.video-background');
    videos.forEach(video => {
        const container = video.closest('.developer-hero');
        if (container) {
            // Додаємо fallback background
            container.style.backgroundImage = 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'100\' height=\'100\' viewBox=\'0 0 100 100\'%3E%3Crect width=\'100\' height=\'100\' fill=\'%23000\'/%3E%3C/svg%3E")';
            container.style.backgroundSize = 'cover';
            container.style.backgroundPosition = 'center';
        }
    });
} 