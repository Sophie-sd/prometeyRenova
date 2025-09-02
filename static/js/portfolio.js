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

// =================================
// VIEWPORT HEIGHT ДЛЯ iOS SAFARI
// =================================

function initViewportHeight() {
    function updateVH() {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);

        // Також оновити активну секцію при зміні viewport
        setTimeout(updateActiveSection, 150);
    }

    // Оновити при завантаженні
    updateVH();

    // Оновити при зміні розміру з дебаунсом
    let resizeTimeout;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            updateVH();
            updateActiveSection();
        }, 100);
    });

    // iOS Safari viewport fix
    if (navigator.platform && /iPad|iPhone|iPod/.test(navigator.platform)) {
        window.addEventListener('orientationchange', function () {
            setTimeout(() => {
                updateVH();
                updateActiveSection();
            }, 150);
        });
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

    // Слухач скролу з оптимізованим throttle для мобільних
    let ticking = false;
    const isMobile = window.innerWidth <= 767;
    const throttleDelay = isMobile ? 100 : 16; // Більша затримка на мобільних

    window.addEventListener('scroll', function () {
        if (!ticking) {
            if (isMobile) {
                // На мобільних - використовуємо setTimeout замість RAF
                setTimeout(() => {
                    updateActiveSection();
                    ticking = false;
                }, throttleDelay);
            } else {
                // На десктопі - RAF як звичайно
                requestAnimationFrame(function () {
                    updateActiveSection();
                    ticking = false;
                });
            }
            ticking = true;
        }
    }, { passive: true });

    // Оновлення при зміні розміру
    window.addEventListener('resize', debounce(updateActiveSection, 100));
}

function updateActiveSection() {
    if (!heroSection || projectSections.length === 0) return;

    const scrollTop = window.pageYOffset;
    const heroHeight = heroSection.offsetHeight;
    const scrollAfterHero = Math.max(0, scrollTop - heroHeight);
    const isMobile = window.innerWidth <= 767;

    // Визначення висоти секції залежно від розміру екрану
    let sectionHeight = window.innerHeight;
    if (window.innerWidth <= 480) {
        sectionHeight = window.innerHeight * 1.1; // 110vh для дуже маленьких екранів
    } else if (window.innerWidth <= 767) {
        sectionHeight = window.innerHeight * 1.2; // 120vh для мобільних
    }

    // Визначення поточної активної секції
    const currentSectionIndex = Math.min(
        Math.floor(scrollAfterHero / sectionHeight),
        projectSections.length - 1
    );

    // Оптимізована логіка для мобільних
    projectSections.forEach((section, index) => {
        const isActive = index === currentSectionIndex && scrollTop >= heroHeight;

        if (isActive && !section.classList.contains('active')) {
            section.classList.add('active');

            // Менш агресивна робота з відео на мобільних
            if (!isMobile) {
                const video = section.querySelector('video');
                if (video) {
                    video.play().catch(() => { }); // Ignore autoplay policy errors
                    if (video.readyState >= 2) {
                        video.classList.add('loaded');
                    }
                }
            }
        } else if (!isActive && section.classList.contains('active')) {
            section.classList.remove('active');

            // Менш частий pause на мобільних
            if (!isMobile) {
                const video = section.querySelector('video');
                if (video && !video.paused) {
                    video.pause();
                }
            }
        }
    });
}

// =================================
// iOS ОПТИМІЗАЦІЇ
// =================================

function initIOSOptimizations() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);

    if (isIOS || isSafari) {
        // Додати клас для iOS-специфічних стилів
        document.body.classList.add('ios-device');

        // Вимкнути scroll bounce
        document.addEventListener('touchmove', function (e) {
            if (e.target.closest('.project-section')) {
                e.preventDefault();
            }
        }, { passive: false });

        // Оптимізація viewport
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute('content',
                'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover'
            );
        }

        // iOS Safari специфічні оптимізації
        if (isSafari) {
            // Примусове перерисування при скролі
            window.addEventListener('scroll', function () {
                document.body.style.transform = 'translateZ(0)';
                setTimeout(() => {
                    document.body.style.transform = '';
                }, 0);
            }, { passive: true });
        }
    }
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

    videos.forEach(video => {
        // Покращена оптимізація для мобільних пристроїв
        if (window.innerWidth < 768) {
            video.setAttribute('preload', 'metadata');
            video.setAttribute('muted', 'true');
        } else {
            video.setAttribute('preload', 'auto');
        }

        // Видаляємо плавне з'явлення для усунення мерехтінь
        video.style.willChange = 'transform, box-shadow';

        // Додати клас loaded для відео які вже завантажені
        if (video.readyState >= 2) {
            video.classList.add('loaded');
        } else {
            video.addEventListener('loadeddata', function () {
                this.classList.add('loaded');
            }, { once: true });
        }

        // Intersection Observer тільки для десктопу (на мобільних може викликати мерехтіння)
        if ('IntersectionObserver' in window && window.innerWidth > 767) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        video.play().catch(() => { });
                    } else {
                        video.pause();
                    }
                });
            }, {
                threshold: 0.3, // 30% відео видимо
                rootMargin: '10%'
            });

            observer.observe(video);
        }
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
    // Intersection Observer тільки на десктопі для уникнення мерехтінь на мобільних
    if ('IntersectionObserver' in window && window.innerWidth > 767) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-viewport');
                } else {
                    entry.target.classList.remove('in-viewport');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });

        projectSections.forEach(section => {
            observer.observe(section);
        });
    }
}

function optimizeScrollEvents() {
    // Passive scroll listeners для кращої продуктивності
    let scrollPosition = 0;
    let ticking = false;

    function updateScrollPosition() {
        scrollPosition = window.pageYOffset;

        // Оптимізація: приховати/показати елементи поза viewport
        projectSections.forEach((section, index) => {
            const rect = section.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight && rect.bottom > 0;

            if (isVisible && !section.classList.contains('visible')) {
                section.classList.add('visible');
            } else if (!isVisible && section.classList.contains('visible')) {
                section.classList.remove('visible');
            }
        });

        ticking = false;
    }

    window.addEventListener('scroll', function () {
        if (!ticking) {
            requestAnimationFrame(updateScrollPosition);
            ticking = true;
        }
    }, { passive: true });
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
