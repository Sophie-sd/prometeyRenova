/**
 * DEVELOPER.JS - Developer page specific logic
 * Використовує: MobileCore, base.js
 * БЕЗ дублювань
 */

document.addEventListener('DOMContentLoaded', () => {
    initProgramNavigation();
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
