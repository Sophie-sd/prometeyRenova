/**
 * HOME.JS - Home page specific logic
 * Використовує: MobileCore, VideoSystem, base.js
 * БЕЗ дублювань viewport/scroll/modal logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initServiceAnimations();
    initAnalytics();
});

// ===== SERVICE CARDS ANIMATIONS =====
function initServiceAnimations() {
    const serviceCards = document.querySelectorAll('.service-card');
    if (serviceCards.length === 0) return;
    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    serviceCards.forEach(card => observer.observe(card));
}

// ===== ANALYTICS =====
function initAnalytics() {
    // Tracking button clicks
    document.addEventListener('click', (e) => {
        const button = e.target.closest('.btn');
        if (button && typeof gtag !== 'undefined') {
            gtag('event', 'button_click', {
                button_text: button.textContent.trim(),
                page_location: window.location.href
            });
        }
    });

    // Time on page tracking
    let timeOnPage = 0;
    setInterval(() => {
        timeOnPage += 1;
        if (timeOnPage === 30 && typeof gtag !== 'undefined') {
            gtag('event', 'engaged_session', {
                time_on_page: timeOnPage
            });
        }
    }, 1000);
}
