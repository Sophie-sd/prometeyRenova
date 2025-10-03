/* =================================
   PORTFOLIO JAVASCRIPT
   ================================= */

// Глобальні змінні
let projectSections = [];
let heroSection = null;
let isScrolling = false;
let scrollTimeout = null;
let isMenuOpen = false;
let scrollHandler = null;

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

    // ОПТИМІЗОВАНИЙ scroll handler - відключається коли меню відкрите
    let ticking = false;
    const isMobile = window.innerWidth <= 767;

    scrollHandler = function () {
        // Не обробляємо scroll якщо меню відкрите
        if (isMenuOpen) return;

        if (!ticking) {
            requestAnimationFrame(() => {
                updateActiveSection();
                ticking = false;
            });
            ticking = true;
        }
    };

    // Використовуємо більш простий підхід для всіх пристроїв
    window.addEventListener('scroll', scrollHandler, { passive: true });

    // Слухаємо події меню
    window.addEventListener('menu:opened', () => {
        isMenuOpen = true;
        console.log('Portfolio: Menu opened, scroll handlers paused');
    });

    window.addEventListener('menu:closed', () => {
        isMenuOpen = false;
        console.log('Portfolio: Menu closed, scroll handlers resumed');
    });

    // Оновлення при зміні розміру (тільки якщо MobileCore не керує цим)
    if (!window.MobileCore || typeof window.MobileCore.isInitialized !== 'function' || !window.MobileCore.isInitialized()) {
        window.addEventListener('resize', debounce(updateActiveSection, 150), { passive: true });
        console.log('Portfolio: Added fallback resize listener');
    }
}

function updateActiveSection() {
    if (!heroSection || projectSections.length === 0) return;

    // Пропускаємо якщо меню відкрите
    if (isMenuOpen) return;

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

    // ОПТИМІЗОВАНА логіка активації секцій - стилі + автопрогравання
    projectSections.forEach((section, index) => {
        const isActive = index === currentSectionIndex && scrollTop >= heroHeight;

        if (isActive && !section.classList.contains('active')) {
            section.classList.add('active');
            // Відтворюємо відео якщо воно вже завантажене
            if (section.classList.contains('video-loaded')) {
                playVideoForActiveSection(section);
            }
        } else if (!isActive && section.classList.contains('active')) {
            section.classList.remove('active');
            // Паузимо відео при деактивації
            pauseVideoForSection(section);
        }
    });
}

// ===== LAZY LOADING ВІДЕО ПРИ ПОЯВІ НА ЕКРАНІ =====
function loadVideoForSection(section) {
    const videos = section.querySelectorAll('video.lazy-video');
    const isMobile = window.innerWidth <= 767;

    if (videos.length === 0) {
        // Відео вже завантажені
        section.classList.add('video-loaded');
        return;
    }

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

            // Відстежуємо завантаження
            video.addEventListener('loadeddata', () => {
                console.log(`Portfolio: Video loaded for section ${section.dataset.project}`);
                section.classList.add('video-loaded');
                section.classList.remove('video-loading');

                // Автовідтворення тільки для активних секцій
                if (section.classList.contains('active')) {
                    video.play().catch(() => {
                        console.log('Portfolio: Autoplay prevented for section', section.dataset.project);
                    });
                }
            }, { once: true });

            // Обробляємо помилки завантаження
            video.addEventListener('error', () => {
                console.error(`Portfolio: Failed to load video for section ${section.dataset.project}`);
                section.classList.add('video-error');
                section.classList.remove('video-loading');
            }, { once: true });

            // Починаємо завантаження
            video.load();
        }
    });
}

function pauseVideoForSection(section) {
    const videos = section.querySelectorAll('video:not(.lazy-video)');
    videos.forEach(video => {
        if (!video.paused) {
            video.pause();
            console.log(`Portfolio: Paused video for section ${section.dataset.project}`);
        }
    });
}

// ===== ВІДЕО АВТОПРОГРАВАННЯ ДЛЯ АКТИВНИХ СЕКЦІЙ =====
function playVideoForActiveSection(section) {
    const videos = section.querySelectorAll('video:not(.lazy-video)');
    const isMobile = window.innerWidth <= 767;

    videos.forEach(video => {
        // Відтворюємо тільки відповідне відео для пристрою
        const shouldPlay = (isMobile && video.classList.contains('mobile-video')) ||
            (!isMobile && video.classList.contains('desktop-video'));

        if (shouldPlay && video.paused && video.readyState >= 2) {
            video.play().catch(() => {
                console.log(`Portfolio: Autoplay prevented for section ${section.dataset.project}`);
            });
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
        // Мобільна версія: плавний scroll зі snap-ефектом
        console.log('Portfolio: Mobile mode - using smooth scroll with snap');

        // Додаємо клас для мобільної оптимізації
        document.body.classList.add('portfolio-mobile');
    } else {
        // Desktop: залишаємо sticky поведінку
        console.log('Portfolio: Desktop mode - using sticky sections');
        document.body.classList.add('portfolio-desktop');
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
    // Анімація кнопки без inline стилів
    button.classList.add('button-clicked');
    setTimeout(() => {
        button.classList.remove('button-clicked');
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

        // Smooth transition без inline стилів
        document.body.classList.add('page-transition');
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

    // Intersection Observer для lazy loading відео при появі на екрані
    initVideoVisibilityObserver();

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

    // Intersection Observer керує завантаженням, не потрібно примусове предзавантаження
    console.log('Portfolio: Videos will be loaded when sections become visible');
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

// ===== INTERSECTION OBSERVER ДЛЯ РАННЬОГО ЗАВАНТАЖЕННЯ ВІДЕО =====
function initVideoVisibilityObserver() {
    // Перевіряємо підтримку Intersection Observer
    if (!('IntersectionObserver' in window)) {
        console.log('Portfolio: Intersection Observer not supported, using fallback');
        return;
    }

    // Створюємо observer для project sections
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const section = entry.target;

            if (entry.isIntersecting) {
                // Секція з'явилася на екрані - завантажуємо відео
                if (!section.classList.contains('video-loading') && !section.classList.contains('video-loaded')) {
                    section.classList.add('video-loading');
                    console.log(`Portfolio: Loading video for section ${section.dataset.project}`);
                    loadVideoForSection(section);
                }
            } else {
                // Секція поза екраном - паузимо відео для економії ресурсів
                pauseVideoForSection(section);
            }
        });
    }, {
        // Починаємо завантаження коли 20% секції видимо
        threshold: 0.2,
        // Додаємо трохи простору для раннього завантаження
        rootMargin: '100px 0px'
    });

    // Спостерігаємо за всіма project sections
    projectSections.forEach(section => {
        observer.observe(section);
    });

    console.log(`Portfolio: Video visibility observer initialized for ${projectSections.length} sections`);
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
