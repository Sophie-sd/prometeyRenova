/**
 * MOBILE-CORE.JS - Модульна система мобільних оптимізацій (2025)
 * Єдине джерело для viewport, device detection, touch
 *
 * Легкий sync-init (класи + reduce-motion), важкий touch/viewport — після first paint.
 * Anti-zoom iOS і overscroll — через CSS (base-bundle), без inline style / reflow.
 */

class MobileCore {
    constructor() {
        this.device = this.detectDevice();
        this.capabilities = this.detectCapabilities();
        this.initialized = false;
        this.viewportUpdateCallbacks = [];
        this._touchBound = false;

        this.init();
    }

    // ===== DEVICE DETECTION (2025 підхід) =====
    detectDevice() {
        const ua = navigator.userAgent.toLowerCase();
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

        return {
            iOS: /ipad|iphone|ipod/.test(ua) && !window.MSStream,
            android: /android/.test(ua),
            safari: /^((?!chrome|android).)*safari/i.test(navigator.userAgent),

            iOSVersion: this.getIOSVersion(ua),
            androidVersion: this.getAndroidVersion(ua),

            isTouch: isTouchDevice,
            isMobile: window.innerWidth <= 767 || isTouchDevice,
            isTablet: window.innerWidth > 767 && window.innerWidth <= 1024 && isTouchDevice,
            hasNotch: CSS.supports && (CSS.supports('padding-top: env(safe-area-inset-top)') || CSS.supports('padding-top: constant(safe-area-inset-top)')),

            isLowEnd: this.detectLowEndDevice(),
            prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        };
    }

    detectCapabilities() {
        return {
            supportsIntersectionObserver: 'IntersectionObserver' in window,
            supportsResizeObserver: 'ResizeObserver' in window,
            supportsCustomProperties: CSS.supports && CSS.supports('color', 'var(--test)'),

            supportsServiceWorker: 'serviceWorker' in navigator,
            supportsWebShare: 'share' in navigator,
            supportsVibration: 'vibrate' in navigator,

            supportsDisplayCutout: CSS.supports && CSS.supports('padding-top: env(safe-area-inset-top)'),
            supportsDynamicViewport: CSS.supports && CSS.supports('height: 100dvh')
        };
    }

    // ===== INITIALIZATION =====
    init() {
        if (this.initialized) return;

        this.setupPerformanceOptimizations();
        this.applyPlatformClasses();

        this.initialized = true;
        this.dispatchInitEvent();

        const runHeavy = () => {
            this.setupViewportSystem();
            this.setupTouchOptimizations();
            if (this.device.iOS) {
                this.optimizeIOSSafariPerformance();
            }
        };

        if (typeof requestAnimationFrame === 'function') {
            requestAnimationFrame(() => {
                requestAnimationFrame(runHeavy);
            });
        } else {
            setTimeout(runHeavy, 0);
        }
    }

    applyPlatformClasses() {
        if (this.device.iOS) {
            document.documentElement.classList.add('ios', 'safari');
            if (this.device.iOSVersion >= 17) {
                document.documentElement.classList.add('ios-17');
            }
        }
        if (this.device.android) {
            document.documentElement.classList.add('android');
        }
    }

    // ===== VIEWPORT SYSTEM (2025 Standard) =====
    setupViewportSystem() {
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };

        setVH();

        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                setVH();
                this.notifyViewportChange();
            }, 250);
        });

        this.notifyViewportChange();
    }

    // ===== iOS SAFARI OPTIMIZATIONS =====
    setupIOSSafariOptimizations() {
        this.applyPlatformClasses();
        this.optimizeIOSSafariPerformance();
    }

    // ===== TOUCH OPTIMIZATIONS =====
    setupTouchOptimizations() {
        if (!this.device.isTouch) return;
        this.setupTouchFeedback();
    }

    setupTouchFeedback() {
        if (this._touchBound) return;
        this._touchBound = true;

        const selector = 'button, [role="button"], .btn, .nav-link, .card-link, [data-modal]';
        let activeEl = null;
        let touchTimeout;

        const clearActive = () => {
            if (activeEl) {
                activeEl.classList.remove('touch-active');
                activeEl = null;
            }
            clearTimeout(touchTimeout);
        };

        document.addEventListener('touchstart', (e) => {
            const el = e.target.closest && e.target.closest(selector);
            if (!el) return;
            clearActive();
            activeEl = el;
            el.classList.add('touch-active');
            if (this.capabilities.supportsVibration && this.device.iOS) {
                navigator.vibrate(10);
            }
        }, { passive: true });

        document.addEventListener('touchend', () => {
            if (!activeEl) return;
            const el = activeEl;
            touchTimeout = setTimeout(() => {
                el.classList.remove('touch-active');
                if (activeEl === el) activeEl = null;
            }, 100);
        }, { passive: true });

        document.addEventListener('touchcancel', clearActive, { passive: true });
    }

    // ===== PERFORMANCE OPTIMIZATIONS =====
    setupPerformanceOptimizations() {
        if (this.device.isLowEnd || this.device.prefersReducedMotion) {
            document.documentElement.classList.add('reduce-motion');
        }
    }

    // ===== UTILITY METHODS =====
    getIOSVersion(ua) {
        const match = ua.match(/os (\d+)_(\d+)_?(\d+)?/);
        return match ? parseInt(match[1], 10) : 0;
    }

    getAndroidVersion(ua) {
        const match = ua.match(/android\s([\d\.]+)/);
        return match ? parseFloat(match[1]) : 0;
    }

    hasDisplayCutout() {
        return this.capabilities.supportsDisplayCutout &&
            (CSS.supports('padding-top: env(safe-area-inset-top)') ||
                CSS.supports('padding-top: constant(safe-area-inset-top)'));
    }

    detectLowEndDevice() {
        const memory = navigator.deviceMemory || 4;
        const cores = navigator.hardwareConcurrency || 4;
        const connection = navigator.connection;

        return memory < 3 || cores < 4 ||
            (connection && (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g'));
    }

    isRootScrollableElement(element) {
        return element === document.documentElement ||
            element === document.body ||
            element.closest('[data-prevent-overscroll]');
    }

    dispatchInitEvent() {
        const event = new CustomEvent('mobilecore:initialized', {
            detail: {
                device: this.device,
                capabilities: this.capabilities
            }
        });
        document.dispatchEvent(event);
    }

    dispatchViewportChangeEvent() {
        const event = new CustomEvent('mobilecore:viewportchange', {
            detail: {
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                device: this.device
            }
        });
        document.dispatchEvent(event);
    }

    // ===== PUBLIC API =====
    getDevice() {
        return this.device;
    }

    getCapabilities() {
        return this.capabilities;
    }

    isInitialized() {
        return this.initialized;
    }

    onViewportChange(callback) {
        this.viewportUpdateCallbacks.push(callback);
    }

    notifyViewportChange() {
        this.viewportUpdateCallbacks.forEach(callback => {
            try {
                callback({
                    width: window.innerWidth,
                    height: window.innerHeight,
                    device: this.device
                });
            } catch (error) {
                console.error('Viewport callback error:', error);
            }
        });
    }

    /** @deprecated Anti-zoom via CSS font-size: 16px (base-bundle). Kept as no-op for callers. */
    preventAccidentalZoom() {}

    setupAndroidOptimizations() {
        document.documentElement.classList.add('android');
    }

    /** @deprecated overscroll via html.ios in CSS. Kept as no-op for callers. */
    fixIOSSafariScrollBounce() {}

    optimizeIOSSafariPerformance() {
        const videos = document.querySelectorAll('video');
        videos.forEach(video => {
            video.setAttribute('playsinline', '');
            video.setAttribute('webkit-playsinline', '');
        });
    }

    preventIOSZoomOnInputs() {
        this.preventAccidentalZoom();
    }
}

// ===== GLOBAL INSTANCE =====
window.MobileCore = new MobileCore();
