/**
 * VIEWPORT MANAGER (2025)
 * 
 * Централізована система управління viewport для всього додатка.
 * Замінює дублікати viewport логіки з base.js, mobile-core.js, portfolio.js.
 * 
 * @example
 * // Підписатися на зміни viewport
 * ViewportManager.on('viewport:changed', (data) => {
 *     console.log('New viewport:', data.vw, data.vh);
 * });
 * 
 * // Отримати поточний viewport
 * const viewport = ViewportManager.getViewport();
 * if (viewport.isMobile) {
 *     // Mobile specific code
 * }
 */

class ViewportManager {
    constructor() {
        this.device = null;
        this.listeners = {};
        this.initialized = false;
        
        // Інтеграція з MobileCore якщо доступний
        if (window.MobileCore) {
            this.device = window.MobileCore.getDevice();
        }
        
        this.init();
    }
    
    init() {
        if (this.initialized) return;
        
        this.setupViewportVars();
        this.setupEventListeners();
        
        this.initialized = true;
        this.dispatch('viewport:initialized');
        
        if (window.Debug) {
            window.Debug.log('ViewportManager initialized');
        }
    }
    
    setupViewportVars() {
        const setVars = () => {
            const vh = window.innerHeight * 0.01;
            const vw = window.innerWidth * 0.01;
            
            document.documentElement.style.setProperty('--vh', `${vh}px`);
            document.documentElement.style.setProperty('--vw', `${vw}px`);
            
            // iOS specific
            if (this.device?.iOS) {
                document.documentElement.style.setProperty(
                    '--mobile-vh', 
                    `${window.innerHeight}px`
                );
                document.body.classList.add('ios-device');
            }
            
            this.dispatch('viewport:changed', {
                vw: window.innerWidth,
                vh: window.innerHeight,
                isMobile: window.innerWidth <= 767,
                isTablet: window.innerWidth > 767 && window.innerWidth <= 1024,
                isDesktop: window.innerWidth > 1024
            });
        };
        
        setVars();
        
        // Debounced resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(setVars, 100);
        }, { passive: true });
        
        // Orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(setVars, 100);
        });
    }
    
    setupEventListeners() {
        // Делегувати до MobileCore якщо доступний
        if (window.MobileCore && window.MobileCore.isInitialized && window.MobileCore.isInitialized()) {
            document.addEventListener('mobilecore:viewportchange', (e) => {
                this.dispatch('viewport:changed', e.detail);
            });
        }
    }
    
    // Event system
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    off(event, callback) {
        if (!this.listeners[event]) return;
        this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
    
    dispatch(event, data = {}) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
        
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }
    
    // Public API
    getViewport() {
        return {
            width: window.innerWidth,
            height: window.innerHeight,
            isMobile: window.innerWidth <= 767,
            isTablet: window.innerWidth > 767 && window.innerWidth <= 1024,
            isDesktop: window.innerWidth > 1024
        };
    }
    
    isInitialized() {
        return this.initialized;
    }
}

// Global instance
window.ViewportManager = new ViewportManager();

// Export for modules
export default ViewportManager;

