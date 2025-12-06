/**
 * PORTFOLIO.JS - Portfolio page animations and interactions
 * Використовує: MobileCore, Intersection Observer
 * Версія: 2.0 (2025)
 */

class PortfolioPage {
    constructor() {
        this.cards = [];
        this.observer = null;
        this.initialized = false;

        this.init();
    }

    init() {
        console.log('[Portfolio] Initializing...');

        // Чекаємо на MobileCore ініціалізацію
        if (window.MobileCore?.isInitialized?.()) {
            console.log('[Portfolio] MobileCore already initialized');
            this.initWithDependencies();
        } else {
            console.log('[Portfolio] Waiting for MobileCore initialization...');
            document.addEventListener('mobilecore:initialized', () => {
                console.log('[Portfolio] MobileCore initialized, initializing portfolio...');
                this.initWithDependencies();
            }, { once: true });
        }
    }

    initWithDependencies() {
        console.log('[Portfolio] Initializing with dependencies...');

        // Кешуємо карточки проектів
        this.cards = Array.from(document.querySelectorAll('.project-card'));

        if (this.cards.length === 0) {
            console.warn('[Portfolio] No project cards found');
            return;
        }

        console.log(`[Portfolio] Found ${this.cards.length} project cards`);

        // Налаштування Intersection Observer для анімацій
        this.setupIntersectionObserver();

        // Інтеграція з MobileCore для viewport змін
        if (window.MobileCore?.onViewportChange) {
            window.MobileCore.onViewportChange(() => {
                console.log('[Portfolio] Viewport changed');
            });
        }

        this.initialized = true;
        console.log('[Portfolio] ✅ Initialization complete');
    }

    setupIntersectionObserver() {
        // Налаштування для Intersection Observer
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        // Додаємо клас для активації анімації
                        entry.target.classList.add('visible');

                        // Додаємо клас animated після невеликої затримки для CSS анімації
                        setTimeout(() => {
                            entry.target.classList.add('animated');
                        }, 100);

                        // Перестаємо спостерігати після появи для економії ресурсів
                        this.observer.unobserve(entry.target);
                    }
                });
            }, observerOptions);

            // Спостерігаємо за кожною карточкою
            this.cards.forEach(card => {
                this.observer.observe(card);
            });

            console.log('[Portfolio] Intersection Observer setup complete');
        } else {
            // Fallback для старих браузерів - показуємо всі карточки одразу
            console.warn('[Portfolio] Intersection Observer not supported, showing all cards');
            this.cards.forEach(card => {
                card.classList.add('visible');
                card.classList.add('animated');
            });
        }
    }

    // Публічний метод для розунспостерігання (якщо потрібно)
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
        this.cards = [];
        this.initialized = false;
        console.log('[Portfolio] ✅ Destroyed');
    }
}

// ===== INITIALIZATION =====

let portfolioInstance = null;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('[Portfolio] DOM loaded, creating instance...');
        portfolioInstance = new PortfolioPage();
    });
} else {
    console.log('[Portfolio] Document already loaded, creating instance immediately...');
    portfolioInstance = new PortfolioPage();
}

// Export для тестування та використання в інших скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PortfolioPage;
}
