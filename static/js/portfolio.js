/**
 * PORTFOLIO.JS - Portfolio page logic
 * Використовує: MobileCore, VideoSystem
 * БЕЗ дублювань, чиста архітектура
 */

class PortfolioPage {
    constructor() {
        this.projectSections = [];
        this.heroSection = null;
        this.state = {
            menuOpen: false,
            activeProjectIndex: -1
        };

        this.init();
    }

    init() {
        // Чекаємо MobileCore
        if (window.MobileCore?.isInitialized()) {
            this.initWithDependencies();
        } else {
            document.addEventListener('mobilecore:initialized', () => {
                this.initWithDependencies();
            });
        }
    }

    initWithDependencies() {
        // Кешуємо елементи
        this.heroSection = document.querySelector('.portfolio-hero');
        this.projectSections = Array.from(document.querySelectorAll('.project-section'));

        if (!this.heroSection || this.projectSections.length === 0) {
            console.warn('Portfolio elements not found');
            return;
        }

        // Налаштування систем
        this.setupStickyScroll();
        this.setupProjectButtons();
        this.setupVideoManagement();
        this.setupMenuIntegration();

        // Підписка на MobileCore viewport changes
        window.MobileCore.onViewportChange(() => {
            this.updateActiveSection();
        });

        console.log('Portfolio initialized');
    }

    // ===== STICKY SCROLL SYSTEM =====
    setupStickyScroll() {
        let ticking = false;

        const handleScroll = () => {
            if (this.state.menuOpen) return;

            if (!ticking) {
                window.requestAnimationFrame(() => {
                    this.updateActiveSection();
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });

        // Початкова активація
        this.updateActiveSection();
    }

    updateActiveSection() {
        if (!this.heroSection || this.projectSections.length === 0) return;
        if (this.state.menuOpen) return;

        const scrollTop = window.pageYOffset;
        const heroHeight = this.heroSection.offsetHeight;
        const scrollAfterHero = Math.max(0, scrollTop - heroHeight);
        const sectionHeight = window.innerHeight;

        const currentIndex = Math.min(
            Math.floor(scrollAfterHero / sectionHeight),
            this.projectSections.length - 1
        );

        // Оновлюємо активні секції
        this.projectSections.forEach((section, index) => {
            const isActive = index === currentIndex && scrollTop >= heroHeight;

            if (isActive && !section.classList.contains('active')) {
                this.activateSection(section, index);
            } else if (!isActive && section.classList.contains('active')) {
                this.deactivateSection(section);
            }
        });

        this.state.activeProjectIndex = currentIndex;
    }

    activateSection(section, index) {
        section.classList.add('active');

        // Відтворення відео через VideoSystem
        const video = this.getVisibleVideoForSection(section);
        if (video && window.VideoSystem) {
            window.VideoSystem.playVideo(video);
        }
    }

    deactivateSection(section) {
        section.classList.remove('active');

        // Пауза відео через VideoSystem
        const video = this.getVisibleVideoForSection(section);
        if (video && window.VideoSystem) {
            window.VideoSystem.pauseVideo(video);
        }
    }

    getVisibleVideoForSection(section) {
        const isMobile = window.innerWidth <= 767;
        const selector = isMobile ? '.mobile-video' : '.desktop-video';
        return section.querySelector(selector);
    }

    // ===== VIDEO MANAGEMENT =====
    setupVideoManagement() {
        // Слухаємо VideoSystem events
        if (window.VideoSystem) {
            window.VideoSystem.on('video:loaded', (e) => {
                const section = e.detail.element.closest('.project-section');
                if (section) {
                    section.classList.add('video-loaded');
                    section.classList.remove('video-loading');
                }
            });

            window.VideoSystem.on('video:error', (e) => {
                const section = e.detail.element?.closest('.project-section');
                if (section) {
                    section.classList.add('video-error');
                    section.classList.remove('video-loading');
                }
            });
        }

        // Позначаємо сторінку готовою
        const heroVideo = this.heroSection.querySelector('video');
        if (heroVideo) {
            if (heroVideo.readyState >= 2) {
                document.body.classList.add('portfolio-ready');
            } else {
                heroVideo.addEventListener('canplaythrough', () => {
                    document.body.classList.add('portfolio-ready');
                }, { once: true });
            }
        }
    }

    // ===== PROJECT BUTTONS =====
    setupProjectButtons() {
        const buttons = document.querySelectorAll('.project-button');

        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleProjectOrder(button);
            });

            // Touch feedback
            if ('ontouchstart' in window) {
                button.addEventListener('touchstart', () => {
                    button.classList.add('button-clicked');
                }, { passive: true });

                button.addEventListener('touchend', () => {
                    setTimeout(() => button.classList.remove('button-clicked'), 150);
                }, { passive: true });
            }
        });
    }

    handleProjectOrder(button) {
        const projectType = button.getAttribute('data-project');
        if (!projectType) return;

        // Анімація кнопки
        button.classList.add('button-clicked');
        setTimeout(() => button.classList.remove('button-clicked'), 150);

        // Словник проектів
        const projectNames = {
            'douit': 'DoUIT - Корпоративний сайт',
            'framejorney': 'Framejorney - Креативне агентство',
            'guide': 'Guide White Energy - Енергетична компанія',
            'polygraph': 'Polygraph - Детекція брехні',
            'prometeylabs': 'PrometeyLabs - IT компанія',
            'pulvas': 'Pulvas Shop - Інтернет-магазин'
        };

        const projectName = projectNames[projectType] || projectType;

        // Перенаправлення з transition
        document.body.classList.add('page-transition');
        setTimeout(() => {
            const url = `/contacts/?project=${projectType}&name=${encodeURIComponent(projectName)}`;
            window.location.href = url;
        }, 200);
    }

    // ===== MENU INTEGRATION =====
    setupMenuIntegration() {
        // Слухаємо події меню з base.js
        document.addEventListener('menu:opened', () => {
            this.state.menuOpen = true;
        });

        document.addEventListener('menu:closed', () => {
            this.state.menuOpen = false;
            // Оновлюємо active section після закриття меню
            setTimeout(() => this.updateActiveSection(), 100);
        });
    }
}

// ===== INITIALIZATION =====
let portfolioInstance = null;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        portfolioInstance = new PortfolioPage();
    });
} else {
    portfolioInstance = new PortfolioPage();
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PortfolioPage;
}
