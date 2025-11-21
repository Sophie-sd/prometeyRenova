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
});

// ===== SERVICE CARDS ANIMATIONS =====
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
        threshold: 0.05,
        rootMargin: '0px 0px -20px 0px'
    });

    serviceCards.forEach(card => observer.observe(card));
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

// ===== PROJECT STORIES (Instagram Style) =====
function initProjectStories() {
    const storiesContainer = document.querySelector('.projects-stories-container');
    const projectStories = document.querySelectorAll('.project-story');

    if (!storiesContainer || projectStories.length === 0) return;

    // Horizontal drag scroll для stories
    setupStoriesDragScroll(storiesContainer);

    // Click handlers with navigation
    setupStoryClickHandlers(projectStories);

    // Keyboard navigation
    setupKeyboardNavigation(storiesContainer, projectStories);

    // Touch feedback для mobile
    setupTouchFeedback(projectStories);
}

function setupStoriesDragScroll(container) {
    let isDown = false;
    let startX;
    let scrollLeft;
    let velocity = 0;
    let lastX = 0;
    let lastTime = Date.now();

    // Mouse events для desktop (passive де можливо)
    container.addEventListener('mousedown', (e) => {
        if (e.target.closest('.project-story')) return;
        isDown = true;
        container.classList.add('grabbing');
        startX = e.pageX - container.offsetLeft;
        scrollLeft = container.scrollLeft;
        velocity = 0;
        lastX = e.pageX;
        lastTime = Date.now();
    }, { passive: true });

    container.addEventListener('mouseleave', () => {
        isDown = false;
        container.classList.remove('grabbing');
    }, { passive: true });

    container.addEventListener('mouseup', () => {
        isDown = false;
        container.classList.remove('grabbing');

        // Momentum scrolling
        if (Math.abs(velocity) > 0.5) {
            applyMomentumScroll(container, velocity);
        }
    }, { passive: true });

    // НЕ passive бо є preventDefault
    container.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - container.offsetLeft;
        const walk = (x - startX) * 2;
        container.scrollLeft = scrollLeft - walk;

        // Calculate velocity
        const now = Date.now();
        const dt = now - lastTime;
        if (dt > 0) {
            velocity = (e.pageX - lastX) / dt;
        }
        lastX = e.pageX;
        lastTime = now;
    });

    // Touch events для mobile (passive для performance)
    container.addEventListener('touchstart', (e) => {
        startX = e.touches[0].pageX;
        scrollLeft = container.scrollLeft;
    }, { passive: true });
}

function applyMomentumScroll(container, velocity) {
    let momentum = velocity * 15;
    const friction = 0.95;

    function step() {
        momentum *= friction;
        container.scrollLeft -= momentum;

        if (Math.abs(momentum) > 0.5) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}

function setupStoryClickHandlers(stories) {
    stories.forEach(story => {
        story.addEventListener('click', (e) => {
            e.preventDefault();

            const projectId = story.getAttribute('data-project-id');
            const projectUrl = story.getAttribute('href');

            // Mark as viewed (optional)
            story.classList.add('viewed');
            localStorage.setItem(`project_${projectId}_viewed`, 'true');

            // Navigate to project (коли додасте URL)
            if (projectUrl && projectUrl !== '#') {
                // Smooth transition before navigation
                story.classList.add('clicking');
                setTimeout(() => {
                    window.location.href = projectUrl;
                }, 200);
            } else {
                console.log(`Project ${projectId} clicked - URL not set yet`);
                // Show temporary notification
                showProjectNotification(projectId);
            }

            // Analytics tracking
            if (typeof gtag !== 'undefined') {
                gtag('event', 'project_click', {
                    project_id: projectId,
                    page_location: window.location.href
                });
            }
        });
    });

    // Load viewed state from localStorage
    stories.forEach(story => {
        const projectId = story.getAttribute('data-project-id');
        if (localStorage.getItem(`project_${projectId}_viewed`) === 'true') {
            story.classList.add('viewed');
        }
    });
}

function setupKeyboardNavigation(container, stories) {
    stories.forEach((story, index) => {
        // Make focusable
        story.setAttribute('tabindex', '0');

        story.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    story.click();
                    break;

                case 'ArrowRight':
                    e.preventDefault();
                    if (index < stories.length - 1) {
                        stories[index + 1].focus();
                        scrollToStory(container, stories[index + 1]);
                    }
                    break;

                case 'ArrowLeft':
                    e.preventDefault();
                    if (index > 0) {
                        stories[index - 1].focus();
                        scrollToStory(container, stories[index - 1]);
                    }
                    break;
            }
        });
    });
}

function scrollToStory(container, story) {
    const containerRect = container.getBoundingClientRect();
    const storyRect = story.getBoundingClientRect();
    const scrollLeft = story.offsetLeft - (containerRect.width / 2) + (storyRect.width / 2);

    container.scrollTo({
        left: scrollLeft,
        behavior: 'smooth'
    });
}

function setupTouchFeedback(stories) {
    // Touch feedback тільки для touch пристроїв
    if (!('ontouchstart' in window)) return;

    stories.forEach(story => {
        let touchStartTime = 0;
        let timeoutId;

        story.addEventListener('touchstart', () => {
            touchStartTime = Date.now();
            story.classList.add('touch-active');
            clearTimeout(timeoutId);
        }, { passive: true });

        story.addEventListener('touchend', () => {
            timeoutId = setTimeout(() => {
                story.classList.remove('touch-active');
            }, 100);
        }, { passive: true });

        story.addEventListener('touchcancel', () => {
            story.classList.remove('touch-active');
            clearTimeout(timeoutId);
        }, { passive: true });
    });
}

function showProjectNotification(projectId) {
    if (window.prometeyApp?.showNotification) {
        window.prometeyApp.showNotification(
            'Щоб отримати посилання на сайт, зверніться до PrometeyLabs',
            'info'
        );
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
