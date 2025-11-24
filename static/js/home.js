/**
 * HOME.JS - Home page specific logic
 * Використовує: MobileCore, VideoSystem, base.js
 * БЕЗ дублювань viewport/scroll/modal logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initServiceAnimations();
    initServiceModals();
    initProjectStories();
    initAnalytics();
    initLazyBackgrounds();
    initWhyChooseAnimations();
});

function initServiceAnimations() {
    const serviceCards = document.querySelectorAll('.service-card');
    if (serviceCards.length === 0) return;
    if (!('IntersectionObserver' in window)) {
        serviceCards.forEach(card => card.classList.add('visible'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                setTimeout(() => {
                    entry.target.style.willChange = 'auto';
                }, 600);
                
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.01,
        rootMargin: '0px'
    });

    serviceCards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const isInViewport = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (isInViewport) {
            card.classList.add('visible');
            setTimeout(() => {
                card.style.willChange = 'auto';
            }, 600);
        } else {
            observer.observe(card);
        }
    });
}

function initServiceModals() {
    let savedScrollPosition = 0;

    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', () => {
            const serviceType = card.dataset.service;
            const modalId = `service-${serviceType}-modal`;
            const modal = document.getElementById(modalId);
            
            if (modal) {
                savedScrollPosition = window.pageYOffset || document.documentElement.scrollTop;

                modal.classList.add('active');
                document.body.style.top = `-${savedScrollPosition}px`;
                document.body.classList.add('modal-open');
                
                const closeModal = () => {
                    modal.classList.remove('active');
                    document.body.style.top = '';
                    document.body.classList.remove('modal-open');
                    window.scrollTo({
                        top: savedScrollPosition,
                        behavior: 'auto'
                    });
                };
                
                const closeBtn = modal.querySelector('.modal-close');
                const backdrop = modal.querySelector('.modal-backdrop');
                
                closeBtn.removeEventListener('click', closeModal);
                backdrop.removeEventListener('click', closeModal);
                
                closeBtn.addEventListener('click', closeModal);
                backdrop.addEventListener('click', closeModal);
                
                document.addEventListener('keydown', function escHandler(e) {
                    if (e.key === 'Escape') {
                        closeModal();
                        document.removeEventListener('keydown', escHandler);
                    }
                });
            }
        });
    });
}

// ===== PROJECT STORIES MARQUEE =====
function initProjectStories() {
    const container = document.querySelector('.projects-stories-container');
    if (!container) return;
    
    waitForImages(container).then(() => {
        initMarqueeAnimation(container);
    }).catch(() => {
        setTimeout(() => initMarqueeAnimation(container), 500);
    });
}

function waitForImages(container) {
    return new Promise((resolve, reject) => {
        const images = container.querySelectorAll('img');
        if (images.length === 0) {
            resolve();
            return;
        }
        
        let loadedCount = 0;
        const totalImages = images.length;
        const timeout = setTimeout(() => reject('timeout'), 3000);
        
        images.forEach(img => {
            if (img.complete) {
                loadedCount++;
                if (loadedCount === totalImages) {
                    clearTimeout(timeout);
                    resolve();
                }
            } else {
                img.addEventListener('load', () => {
                    loadedCount++;
                    if (loadedCount === totalImages) {
                        clearTimeout(timeout);
                        resolve();
                    }
                }, { once: true });
                
                img.addEventListener('error', () => {
                    loadedCount++;
                    if (loadedCount === totalImages) {
                        clearTimeout(timeout);
                        resolve();
                    }
                }, { once: true });
            }
        });
    });
}

function initMarqueeAnimation(container) {
    const stories = container.querySelectorAll('.project-story:not(.story-clone)');
    if (stories.length === 0) return;
    
    const containerStyles = window.getComputedStyle(container);
    const gap = parseFloat(containerStyles.gap) || 24;
    
    const firstStory = stories[0];
    const lastStory = stories[stories.length - 1];
    const setWidth = (lastStory.offsetLeft + lastStory.offsetWidth + gap) - firstStory.offsetLeft;
    
    container.style.setProperty('--marquee-distance', `${setWidth}px`);
    container.setAttribute('aria-label', 'Наші проєкти - автоматична демонстрація');
    container.setAttribute('role', 'marquee');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    requestAnimationFrame(() => {
                        container.classList.add('marquee-active');
                    });
                    observer.unobserve(container);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        observer.observe(container);
    } else {
        requestAnimationFrame(() => {
            container.classList.add('marquee-active');
        });
    }
}

// ===== ANALYTICS =====
function initAnalytics() {
    // Tracking button clicks (passive listener)
    document.addEventListener('click', (e) => {
        const button = e.target.closest('.btn');
        if (button && typeof gtag !== 'undefined') {
            gtag('event', 'button_click', {
                button_text: button.textContent.trim(),
                page_location: window.location.href
            });
        }
    }, { passive: true });

    // Time on page tracking (оптимізовано)
    let timeOnPage = 0;
    let trackedEngagement = false;

    const timeTracker = setInterval(() => {
        timeOnPage += 1;
        if (timeOnPage === 30 && !trackedEngagement && typeof gtag !== 'undefined') {
            gtag('event', 'engaged_session', {
                time_on_page: timeOnPage
            });
            trackedEngagement = true;
            clearInterval(timeTracker); // Зупинити після трекінгу
        }
    }, 1000);
}

function initLazyBackgrounds() {
    const lazyBgElements = document.querySelectorAll('.lazy-bg');
    if (lazyBgElements.length === 0) return;

    if (!('IntersectionObserver' in window)) {
        lazyBgElements.forEach(el => loadBackground(el));
        return;
    }

    const bgObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadBackground(entry.target);
                bgObserver.unobserve(entry.target);
            }
        });
    }, {
        rootMargin: '0px',
        threshold: 0.01
    });

    lazyBgElements.forEach(el => {
        const rect = el.getBoundingClientRect();
        const isInViewport = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (isInViewport) {
            loadBackground(el);
        } else {
            bgObserver.observe(el);
        }
    });
}

function loadBackground(element) {
    const isMobile = window.innerWidth <= 767;
    const bgUrl = isMobile 
        ? element.getAttribute('data-bg-mobile') 
        : element.getAttribute('data-bg-desktop');
    
    if (bgUrl) {
        const img = new Image();
        img.onload = () => {
            element.style.backgroundImage = `url('${bgUrl}')`;
            element.classList.add('lazy-bg-loaded');
            element.classList.remove('lazy-bg');
        };
        img.src = bgUrl;
    }
}

function initWhyChooseAnimations() {
    const whyCards = document.querySelectorAll('.why-card');
    if (whyCards.length === 0) return;

    if (!('IntersectionObserver' in window)) {
        whyCards.forEach(card => card.classList.add('visible'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = entry.target.dataset.delay || 0;
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, delay);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px'
    });

    whyCards.forEach(card => observer.observe(card));
}
