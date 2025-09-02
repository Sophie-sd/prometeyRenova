/* DEVELOPER.JS - JavaScript для курсів */

document.addEventListener('DOMContentLoaded', function () {
    console.log('Developer page loaded');

    setupCourseCards();
    initDeveloperViewport();
});

function setupCourseCards() {
    const courseCards = document.querySelectorAll('.course-card');

    courseCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-5px)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Viewport height для iOS Safari на сторінці розробника
function initDeveloperViewport() {
    function setVH() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);

        // Додатковий фікс для iOS Safari
        const realVh = window.innerHeight;
        document.documentElement.style.setProperty('--real-vh', `${realVh}px`);

        // Фікс для developer секцій
        const developerSections = document.querySelectorAll('.developer-hero, .dark-split-section');
        developerSections.forEach(section => {
            section.style.height = `${realVh}px`;
        });
    }

    setVH();

    // Покращена обробка events
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(setVH, 150);
    });

    window.addEventListener('orientationchange', () => {
        setTimeout(setVH, 500);
    });

    // Фікс при завантаженні
    window.addEventListener('load', () => {
        setTimeout(setVH, 200);
    });
} 