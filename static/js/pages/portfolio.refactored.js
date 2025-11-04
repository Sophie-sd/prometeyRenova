/**
 * PORTFOLIO.JS - Refactored v2.0
 * Чиста архітектура без дублювань
 */

import CONFIG from '../core/config.js';
import analytics from '../core/analytics.js';

class PortfolioPage {
    constructor() {
        this.projectSections = [];
        this.heroSection = null;
        this.state = {
            menuOpen: false,
            activeProjectIndex: -1,
        };

        this.init();
    }

    init() {
        console.log('[Portfolio] Initializing...');

        // Чекаємо MobileCore
        if (window.MobileCore?.isInitialized()) {
            this.initWithDependencies();
        } else {
            document.addEventListener(CONFIG.events.mobileCoreInit, () => {
                this.initWithDependencies();
            });
        }
    }

    initWithDependencies() {
        console.log('[Portfolio] Initializing with dependencies...');

        // Cache elements
        this.heroSection = document.querySelector('.portfolio-hero, .hero-section');
        this.projectSections = Array.from(document.querySelectorAll('.project-section'));

        if (!this.heroSection || this.projectSections.length === 0) {
            console.warn('[Portfolio] Required elements not found');
            return;
        }

        // Setup systems
        this.setupStickyScroll();
        this.setupProjectButtons();
        this.setupVideoManagement();
        this.setupMenuIntegration();

        // MobileCore viewport changes
        window.MobileCore.onViewportChange(() => {
            this.updateActiveSection();
        });

        console.log('[Portfolio] ✅ Initialized');
    }

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

        // Initial
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

        // Update active sections
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

        // Video control через VideoSystem
        const video = this.getVisibleVideoForSection(section);
        if (video && window.VideoSystem) {
            window.VideoSystem.playVideo(video);
        }

        // Analytics
        analytics.trackCustom('project_view', {
            project_index: index + 1,
        });
    }

    deactivateSection(section) {
        section.classList.remove('active');

        const video = this.getVisibleVideoForSection(section);
        if (video && window.VideoSystem) {
            window.VideoSystem.pauseVideo(video);
        }
    }

    getVisibleVideoForSection(section) {
        const isMobile = window.innerWidth <= CONFIG.breakpoints.mobile;
        const selector = isMobile ? '.mobile-video' : '.desktop-video';
        return section.querySelector(selector);
    }

    setupVideoManagement() {
        if (!window.VideoSystem) return;

        // VideoSystem events
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

        // Hero video ready
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

    setupProjectButtons() {
        const buttons = document.querySelectorAll('.project-button');

        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleProjectOrder(button);
            });

            // Touch feedback (MobileCore вже додає, але додатковий візуальний ефект)
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

        // Animation
        button.classList.add('button-clicked');
        setTimeout(() => button.classList.remove('button-clicked'), 150);

        // Project names
        const projectNames = {
            'douit': 'DoUIT - Корпоративний сайт',
            'framejorney': 'Framejorney - Креативне агентство',
            'guide': 'Guide White Energy - Енергетична компанія',
            'polygraph': 'Polygraph - Детекція брехні',
            'prometeylabs': 'PrometeyLabs - IT компанія',
            'pulvas': 'Pulvas Shop - Інтернет-магазин'
        };

        const projectName = projectNames[projectType] || projectType;

        // Analytics
        analytics.trackCustom('project_order_click', {
            project_type: projectType,
            project_name: projectName,
        });

        // Redirect з transition
        document.body.classList.add('page-transition');
        setTimeout(() => {
            const url = `/contacts/?project=${projectType}&name=${encodeURIComponent(projectName)}`;
            window.location.href = url;
        }, 200);
    }

    setupMenuIntegration() {
        // Слухаємо події з app-core.js через CONFIG
        document.addEventListener(CONFIG.events.menuOpen, () => {
            this.state.menuOpen = true;
        });

        document.addEventListener(CONFIG.events.menuClose, () => {
            this.state.menuOpen = false;
            setTimeout(() => this.updateActiveSection(), 100);
        });
    }
}

// ===== AUTO INIT =====
let portfolioInstance = null;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        portfolioInstance = new PortfolioPage();
    });
} else {
    portfolioInstance = new PortfolioPage();
}

export default PortfolioPage;

