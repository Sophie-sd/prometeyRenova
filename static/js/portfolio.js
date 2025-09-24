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

// ПРАВИЛЬНА ІНІЦІАЛІЗАЦІЯ - чекаємо MobileCore
function initPortfolio() {
    initViewportHeight();
    initStickyScroll();
    initIOSOptimizations();
    initProjectButtons();
    initScrollOptimizations();

    console.log('Portfolio page initialized with MobileCore support');
}

// Чекаємо ініціалізації MobileCore або fallback до DOMContentLoaded
if (window.MobileCore && typeof window.MobileCore.isInitialized === 'function' && window.MobileCore.isInitialized()) {
    // MobileCore вже готовий
    console.log('Portfolio: MobileCore already initialized');
    document.addEventListener('DOMContentLoaded', initPortfolio);
} else {
    console.log('Portfolio: Waiting for MobileCore or using fallback');
    // Чекаємо події MobileCore або fallback
    let portfolioInitialized = false;

    document.addEventListener('mobilecore:initialized', function () {
        if (!portfolioInitialized) {
            portfolioInitialized = true;
            initPortfolio();
        }
    });

    // Fallback якщо MobileCore не завантажився через 2 секунди
    document.addEventListener('DOMContentLoaded', function () {
        setTimeout(() => {
            if (!portfolioInitialized) {
                console.warn('Portfolio: MobileCore timeout, initializing without it');
                portfolioInitialized = true;
                initPortfolio();
            }
        }, 2000);
    });
}

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
    if (window.MobileCore && typeof window.MobileCore.isInitialized === 'function' && window.MobileCore.isInitialized()) {
        // MobileCore вже керує viewport - тільки реагуємо на зміни
        document.addEventListener('mobilecore:viewportchange', updateActiveOnViewportChange);
        console.log('Portfolio: Using MobileCore viewport events');
    } else {
        // Fallback якщо MobileCore недоступний
        console.log('Portfolio: Using fallback viewport handling');
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
    if (!window.MobileCore || typeof window.MobileCore.isInitialized !== 'function' || !window.MobileCore.isInitialized()) {
        window.addEventListener('resize', debounce(updateActiveSection, 150), { passive: true });
        console.log('Portfolio: Added fallback resize listener');
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

    // ОПТИМІЗОВАНА логіка активації секцій з lazy loading відео
    projectSections.forEach((section, index) => {
        const isActive = index === currentSectionIndex && scrollTop >= heroHeight;

        if (isActive && !section.classList.contains('active')) {
            section.classList.add('active');

            // LAZY LOAD відео тільки для активної секції
            loadVideoForSection(section);
        } else if (!isActive && section.classList.contains('active')) {
            section.classList.remove('active');

            // Паузимо відео в неактивних секціях для економії ресурсів
            pauseVideoForSection(section);
        }
    });
}

// ===== LAZY LOADING ВІДЕО =====
function loadVideoForSection(section) {
    const videos = section.querySelectorAll('video.lazy-video');
    const isMobile = window.innerWidth <= 767;

    videos.forEach(video => {
        // Завантажуємо тільки потрібне відео (mobile/desktop)
        const shouldLoad = (isMobile && video.classList.contains('mobile-video')) ||
            (!isMobile && video.classList.contains('desktop-video'));

        if (shouldLoad && video.hasAttribute('data-src')) {
            // Переносимо src з data-src
            const dataSrc = video.getAttribute('data-src');
            const source = video.querySelector('source');

            if (source && source.hasAttribute('data-src')) {
                source.src = source.getAttribute('data-src');
                source.removeAttribute('data-src');
            }

            video.src = dataSrc;
            video.removeAttribute('data-src');
            video.classList.remove('lazy-video');

            // Починаємо відтворення після завантаження
            video.addEventListener('loadeddata', () => {
                if (section.classList.contains('active')) {
                    video.play().catch(() => {
                        console.log('Autoplay prevented for video in section', section);
                    });
                }
            }, { once: true });

            // Завантажуємо відео
            video.load();
        }
    });
}

function pauseVideoForSection(section) {
    const videos = section.querySelectorAll('video:not(.lazy-video)');
    videos.forEach(video => {
        if (!video.paused) {
            video.pause();
        }
    });
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
    console.log('Portfolio: Video optimization initialized with lazy loading');

    // Hero відео завантажуємо одразу (тільки одне буде видиме)
    const heroVideos = document.querySelectorAll('.hero-video');
    heroVideos.forEach(video => {
        video.addEventListener('loadeddata', function () {
            this.classList.add('loaded');
            console.log('Hero video loaded:', video.className);
        }, { once: true });
    });

    // Project відео будуть завантажені через lazy loading в updateActiveSection
    const projectVideos = document.querySelectorAll('.project-video video.lazy-video');
    console.log(`Portfolio: ${projectVideos.length} project videos will be lazy loaded`);

    // Предзавантажити перше відео для кращого UX
    setTimeout(() => {
        const firstSection = document.querySelector('.project-section[data-project="1"]');
        if (firstSection) {
            console.log('Portfolio: Pre-loading first project video');
            loadVideoForSection(firstSection);
        }
    }, 2000); // Через 2 секунди після завантаження сторінки
}

function preloadCriticalResources() {
    console.log('Portfolio: Critical resources preloaded via HTML preload tags');

    // Перевіряємо чи завантажились критичні відео
    const isMobile = window.innerWidth <= 767;
    const heroVideoSrc = isMobile ?
        '/static/videos/mobile/portfoliomobile.mp4' :
        '/static/videos/desktop/portfolio.mp4';

    // Простий метод перевірки готовності відео
    const heroVideo = document.querySelector(isMobile ? '.mobile-hero-video' : '.desktop-hero-video');
    if (heroVideo && heroVideo.readyState < 2) {
        console.log('Portfolio: Waiting for hero video to load...');
        heroVideo.addEventListener('canplaythrough', () => {
            console.log('Portfolio: Hero video ready');
            document.body.classList.add('portfolio-ready');
        }, { once: true });
    } else {
        document.body.classList.add('portfolio-ready');
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
