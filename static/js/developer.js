/**
 * DEVELOPER.JS - Developer page specific logic
 * Використовує: MobileCore, base.js
 * БЕЗ дублювань
 */

document.addEventListener('DOMContentLoaded', () => {
    initCourseCards();
    initHapticFeedback();
});

// ===== COURSE CARDS =====
function initCourseCards() {
    const courseCards = document.querySelectorAll('.course-card');

    courseCards.forEach(card => {
        // Desktop hover працює через CSS - не потрібен JS

        // Touch target для mobile (MobileCore додає стилі)
        if (window.MobileCore?.getDevice().isTouch) {
            card.classList.add('mobile-touch-target');
        }
    });
}

// ===== HAPTIC FEEDBACK =====
function initHapticFeedback() {
    if (!('vibrate' in navigator)) return;
    if (!window.MobileCore?.getDevice().isTouch) return;

    const interactiveElements = document.querySelectorAll('.course-card, [data-modal]');

    interactiveElements.forEach(element => {
        element.addEventListener('touchstart', () => {
            navigator.vibrate(10);
        }, { passive: true });
    });
}
