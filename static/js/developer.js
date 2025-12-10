/**
 * DEVELOPER.JS - Developer page specific logic
 * Використовує: MobileCore, base.js
 * БЕЗ дублювань
 */

document.addEventListener('DOMContentLoaded', () => {
    initProgramNavigation();
    initParallaxBackgrounds();
    initMobileOptimizations();
});

// ===== SMOOTH SCROLL TO PROGRAMS SECTION =====
function initProgramNavigation() {
    const programLinks = document.querySelectorAll('a[href="#programs"]');
    
    programLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.getElementById('programs');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// ===== PARALLAX BACKGROUNDS =====
function initParallaxBackgrounds() {
    // Перевірити підтримку reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;
    
    // Перевірити, чи це мобільний пристрій
    const isMobile = window.innerWidth <= 767;
    
    // Отримати всі элементи з паралакс фоном
    const parallaxSections = document.querySelectorAll('.parallax-background');
    if (parallaxSections.length === 0) return;
    
    // Зберігати активні елементи для оптимізації
    const parallaxElements = new Map();
    let scrolling = false;
    let rafId = null;
    
    // Налаштування паралаксу залежно від пристрою
    const parallaxSpeed = isMobile ? 0 : 0.4; // Без паралаксу на мобільних
    
    // Інициалізувати спостереження за видимістю
    const observerOptions = {
        root: null,
        rootMargin: '50px',
        threshold: 0.01
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const section = entry.target;
            const image = section.querySelector('.parallax-background__image');
            
            if (!image) return;
            
            if (entry.isIntersecting) {
                parallaxElements.set(section, { image, active: true });
                image.classList.remove('parallax-inactive');
            } else {
                const elem = parallaxElements.get(section);
                if (elem) {
                    elem.active = false;
                    image.classList.add('parallax-inactive');
                }
            }
        });
    }, observerOptions);
    
    // Спостерігати за всіма секціями
    parallaxSections.forEach(section => {
        observer.observe(section);
    });
    
    // Функція обчислення паралаксу
    function updateParallax() {
        scrolling = false;
        
        parallaxElements.forEach(({ image, active }) => {
            if (!active || parallaxSpeed === 0) return;
            
            const section = image.parentElement;
            const rect = section.getBoundingClientRect();
            
            // Обчислити, наскільки секція виходить за межі viewport
            const offset = (window.innerHeight - rect.top) * parallaxSpeed;
            
            // Застосувати трансформацію з GPU acceleration
            image.style.transform = `translate3d(0, ${offset}px, 0)`;
        });
    }
    
    // Обробник прокручування з requestAnimationFrame
    function onScroll() {
        if (!scrolling) {
            scrolling = true;
            rafId = requestAnimationFrame(updateParallax);
        }
    }
    
    // Додати обробник scroll з passive flag
    window.addEventListener('scroll', onScroll, { passive: true });
    
    // Очистити ресурси при переході на іншу сторінку
    window.addEventListener('beforeunload', () => {
        window.removeEventListener('scroll', onScroll);
        observer.disconnect();
        if (rafId) {
            cancelAnimationFrame(rafId);
        }
    });
    
    // Виконати один раз при завантаженні
    updateParallax();
}

// ===== MOBILE OPTIMIZATIONS =====
function initMobileOptimizations() {
    if (!window.MobileCore?.getDevice().isTouch) return;

    // Add mobile touch targets for interactive elements
    const interactiveElements = document.querySelectorAll('.btn, .program-card, .target-audience-card, .benefit-item');
    
    interactiveElements.forEach(element => {
        element.classList.add('mobile-touch-target');
        
        // Add haptic feedback for touch devices
        if ('vibrate' in navigator) {
            element.addEventListener('touchstart', () => {
                navigator.vibrate(10);
            }, { passive: true });
        }
    });
}
