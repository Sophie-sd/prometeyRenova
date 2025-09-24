/* =================================
   PORTFOLIO JAVASCRIPT
   ================================= */

// Глобальні змінні
let projectSections = [];
let heroSection = null;
let isScrolling = false;
let scrollTimeout = null;

// =================================
// ІНІЦІАЛІЗАЦІЯ
// =================================

document.addEventListener('DOMContentLoaded', function () {
    initViewportHeight();
    initStickyScroll();
    initIOSOptimizations();
    initProjectButtons();
    initScrollOptimizations();

    console.log('Portfolio page initialized');
});

// ===== UTILITY FUNCTIONS =====
function isMobile() {
    return window.innerWidth <= 767 ||
        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0;
}

// =================================
// VIEWPORT HEIGHT - ВИКОРИСТОВУЄМО MOBILECORE
// =================================

function initViewportHeight() {
    // Делегуємо viewport управління MobileCore
    // Тільки оновлюємо активну секцію при зміні viewport
    function updateActiveOnViewportChange() {
        setTimeout(updateActiveSection, 100);
    }

    // Початкове оновлення
    setTimeout(updateActiveSection, 100);

    // Слухаємо події від MobileCore замість дублювання обробників
    if (window.MobileCore && window.MobileCore.isInitialized()) {
        // MobileCore вже керує viewport - тільки реагуємо на зміни
        document.addEventListener('mobilecore:viewportchange', updateActiveOnViewportChange);
    } else {
        // Fallback якщо MobileCore недоступний
        let resizeTimeout;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(updateActiveOnViewportChange, 150);
        }, { passive: true });
    }
}

// =================================
// STICKY SCROLL ЕФЕКТ
// =================================

function initStickyScroll() {
    heroSection = document.querySelector('.portfolio-hero');
    projectSections = Array.from(document.querySelectorAll('.project-section'));

    if (!heroSection || projectSections.length === 0) {
        console.warn('Portfolio sections not found');
        return;
    }

    // Початкова активна секція
    updateActiveSection();

    // СПРОЩЕНИЙ scroll handler - менше навантаження
    let ticking = false;
    const isMobile = window.innerWidth <= 767;

    // Використовуємо більш простий підхід для всіх пристроїв
    window.addEventListener('scroll', function () {
        if (!ticking) {
            requestAnimationFrame(() => {
                updateActiveSection();
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    // Оновлення при зміні розміру (тільки якщо MobileCore не керує цим)
    if (!window.MobileCore || !window.MobileCore.isInitialized()) {
        window.addEventListener('resize', debounce(updateActiveSection, 150), { passive: true });
    }
}

function updateActiveSection() {
    if (!heroSection || projectSections.length === 0) return;

    const scrollTop = window.pageYOffset;
    const heroHeight = heroSection.offsetHeight;
    const scrollAfterHero = Math.max(0, scrollTop - heroHeight);
    const isMobile = window.innerWidth <= 767;

    // СПРОЩЕНА логіка висоти секції
    const sectionHeight = window.innerHeight;

    // Визначення поточної активної секції
    const currentSectionIndex = Math.min(
        Math.floor(scrollAfterHero / sectionHeight),
        projectSections.length - 1
    );

    // СПРОЩЕНА логіка активації секцій
    projectSections.forEach((section, index) => {
        const isActive = index === currentSectionIndex && scrollTop >= heroHeight;

        // Просто додаємо/видаляємо клас без складної відео логіки
        if (isActive && !section.classList.contains('active')) {
            section.classList.add('active');
        } else if (!isActive && section.classList.contains('active')) {
            section.classList.remove('active');
        }
    });

    // ВИДАЛЕНО всю складну відео логіку - викликала тормоза
}

// =================================
// iOS ОПТИМІЗАЦІЇ - ДЕЛЕГУЄМО MOBILECORE
// =================================

function initIOSOptimizations() {
    // MobileCore тепер відповідає за всі iOS оптимізації
    // Тут залишаємо тільки portfolio-специфічні налаштування

    const isMobile = window.innerWidth <= 767;

    if (isMobile) {
        // Мобільна версія: звичайний scroll без блокування
        console.log('Portfolio: Mobile mode - using standard scroll');

        // Видаляємо всі sticky ефекти на мобільних для покращення швидкодії
        projectSections.forEach(section => {
            section.style.position = 'relative';
            section.style.top = 'auto';
        });
    } else {
        // Desktop: залишаємо sticky поведінку
        console.log('Portfolio: Desktop mode - using sticky sections');
    }

    // Всі інші iOS оптимізації делегуємо MobileCore
}

// =================================
// ОБРОБКА КНОПОК ПРОЕКТІВ
// =================================

function initProjectButtons() {
    const projectButtons = document.querySelectorAll('.project-button');

    projectButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            const projectType = this.getAttribute('data-project');
            handleProjectOrder(projectType, this);
        });

        // Додати hover ефекти для тач пристроїв
        button.addEventListener('touchstart', function () {
            this.classList.add('touch-active');
        }, { passive: true });

        button.addEventListener('touchend', function () {
            setTimeout(() => {
                this.classList.remove('touch-active');
            }, 150);
        });
    });
}

function handleProjectOrder(projectType, button) {
    // Анімація кнопки
    button.style.transform = 'scale(0.95)';
    setTimeout(() => {
        button.style.transform = '';
    }, 150);

    // Логіка замовлення проекту
    console.log(`Ordering project type: ${projectType}`);

    // Словник проектів для зрозумілих повідомлень
    const projectNames = {
        'douit': 'DoUIT - Корпоративний сайт',
        'framejorney': 'Framejorney - Креативне агентство',
        'guide': 'Guide White Energy - Енергетична компанія',
        'polygraph': 'Polygraph - Детекція брехні',
        'prometeylabs': 'PrometeyLabs - IT компанія',
        'pulvas': 'Pulvas Shop - Інтернет-магазин'
    };

    const projectName = projectNames[projectType] || projectType;

    // Перенаправлення на контакти з параметром проекту
    if (typeof window !== 'undefined') {
        const contactsUrl = `/contacts/?project=${projectType}&name=${encodeURIComponent(projectName)}`;

        // Smooth transition
        document.body.style.opacity = '0.8';
        setTimeout(() => {
            window.location.href = contactsUrl;
        }, 200);
    }
}

// =================================
// ОПТИМІЗАЦІЇ ПРОДУКТИВНОСТІ
// =================================

function initScrollOptimizations() {
    // Preload критичних ресурсів
    preloadCriticalResources();

    // Intersection Observer для lazy loading
    initIntersectionObserver();

    // Throttle scroll events
    optimizeScrollEvents();

    // Відео оптимізація
    initVideoOptimizations();
}

function initVideoOptimizations() {
    const videos = document.querySelectorAll('.project-video video');
    const isMobile = window.innerWidth <= 767;

    videos.forEach(video => {
        // СПРОЩЕНА логіка для кращої продуктивності
        if (isMobile) {
            // На мобільних - мінімальні налаштування для швидкодії
            video.setAttribute('preload', 'none'); // Не завантажуємо відео заздалегідь
            video.setAttribute('muted', 'true');
            video.removeAttribute('autoplay'); // Відключаємо autoplay на мобільних
        } else {
            // На десктопі - можемо дозволити більше
            video.setAttribute('preload', 'metadata');
            video.setAttribute('muted', 'true');
        }

        // Простий контроль завантаження без надмірної логіки
        video.addEventListener('loadeddata', function () {
            this.classList.add('loaded');
        }, { once: true });

        // ВИДАЛЕНО INTERSECTION OBSERVER - викликав конфлікти
        // Замість цього використовуємо просту логіку в updateActiveSection
    });
}

function preloadCriticalResources() {
    // Preload критичних стилів
    const criticalCSS = document.querySelector('link[href*="portfolio.css"]');
    if (criticalCSS) {
        criticalCSS.setAttribute('rel', 'preload');
        criticalCSS.setAttribute('as', 'style');
        criticalCSS.setAttribute('onload', "this.onload=null;this.rel='stylesheet'");
    }
}

function initIntersectionObserver() {
    // ВИДАЛЕНО - викликало конфлікти з іншими системами
    // Тепер використовуємо тільки просту scroll логіку в updateActiveSection
    console.log('Portfolio: Intersection Observer disabled for better performance');
}

function optimizeScrollEvents() {
    // ВИДАЛЕНО - дублювало функціональність з initStickyScroll
    // Тепер використовуємо тільки один scroll handler в initStickyScroll
    console.log('Portfolio: Scroll optimization delegated to main handler');
}

// =================================
// UTILITY FUNCTIONS
// =================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            timeout = null;
            func(...args);
        };
        const callNow = !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function () {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// =================================
// ERROR HANDLING
// =================================

window.addEventListener('error', function (e) {
    console.error('Portfolio JS Error:', e.error);
});

// Graceful degradation для старих браузерів
if (!window.requestAnimationFrame) {
    window.requestAnimationFrame = function (callback) {
        return setTimeout(callback, 16);
    };
}

if (!window.cancelAnimationFrame) {
    window.cancelAnimationFrame = function (id) {
        clearTimeout(id);
    };
}

// =================================
// EXPORT FOR TESTING
// =================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initStickyScroll,
        updateActiveSection,
        initViewportHeight,
        handleProjectOrder
    };
}
