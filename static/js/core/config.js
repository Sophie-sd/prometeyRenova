/**
 * GLOBAL CONFIGURATION (2025)
 * Централізовані константи та налаштування
 */

export const Config = {
    // Breakpoints (синхронізовані з CSS)
    breakpoints: {
        mobile: 767,
        tablet: 1024,
        desktop: 1200
    },
    
    // Animations
    animations: {
        duration: {
            fast: 150,
            normal: 300,
            slow: 500
        },
        easing: {
            default: 'ease-out',
            bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
            smooth: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }
    },
    
    // Video settings
    video: {
        loadStrategy: 'lazy', // 'eager', 'lazy', 'progressive'
        autoplay: true,
        preload: {
            mobile: 'metadata',
            desktop: 'auto'
        }
    },
    
    // Performance
    performance: {
        debounceDelay: 100,
        throttleDelay: 16, // ~60fps
        lazyLoadMargin: '50px'
    },
    
    // Debug
    debug: {
        enabled: false, // Буде перевизначено DebugManager
        logLevel: 'info'
    }
};

// Helper functions
export const isMobile = () => window.innerWidth <= Config.breakpoints.mobile;
export const isTablet = () => window.innerWidth > Config.breakpoints.mobile && 
                               window.innerWidth <= Config.breakpoints.tablet;
export const isDesktop = () => window.innerWidth > Config.breakpoints.tablet;

// Global access
window.Config = Config;

