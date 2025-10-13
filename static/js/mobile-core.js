/**
 * MOBILE-CORE.JS - Модульна система мобільних оптимізацій (2025)
 * Єдине джерело для viewport, device detection, touch
 */

class MobileCore {
    constructor() {
        this.device = this.detectDevice();
        this.capabilities = this.detectCapabilities();
        this.initialized = false;
        this.viewportUpdateCallbacks = [];

        this.init();
    }

    // ===== DEVICE DETECTION (2025 підхід) =====
    detectDevice() {
        const ua = navigator.userAgent.toLowerCase();
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

        return {
            // Основні платформи
            iOS: /ipad|iphone|ipod/.test(ua) && !window.MSStream,
            android: /android/.test(ua),
            safari: /^((?!chrome|android).)*safari/i.test(navigator.userAgent),

            // Специфічні версії
            iOSVersion: this.getIOSVersion(ua),
            androidVersion: this.getAndroidVersion(ua),

            // Характеристики
            isTouch: isTouchDevice,
            isMobile: window.innerWidth <= 767 || isTouchDevice,
            isTablet: window.innerWidth > 767 && window.innerWidth <= 1024 && isTouchDevice,
            hasNotch: this.hasDisplayCutout(),

            // Performance indicators
            isLowEnd: this.detectLowEndDevice(),
            prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        };
    }

    detectCapabilities() {
        return {
            // Video capabilities
            canAutoplay: this.testAutoplaySupport(),
            supportsHEVC: this.testHEVCSupport(),
            supportsWebP: this.testWebPSupport(),

            // Modern features
            supportsIntersectionObserver: 'IntersectionObserver' in window,
            supportsResizeObserver: 'ResizeObserver' in window,
            supportsCustomProperties: CSS.supports && CSS.supports('color', 'var(--test)'),

            // PWA features
            supportsServiceWorker: 'serviceWorker' in navigator,
            supportsWebShare: 'share' in navigator,
            supportsVibration: 'vibrate' in navigator,

            // Display features
            supportsDisplayCutout: CSS.supports && CSS.supports('padding-top: env(safe-area-inset-top)'),
            supportsDynamicViewport: CSS.supports && CSS.supports('height: 100dvh')
        };
    }

    // ===== INITIALIZATION =====
    init() {
        if (this.initialized) return;

        this.setupViewportSystem();
        this.setupTouchOptimizations();
        this.setupPerformanceOptimizations();
        this.setupAccessibilityEnhancements();

        // Device-specific optimizations
        if (this.device.iOS) {
            this.setupIOSSafariOptimizations();
        }

        if (this.device.android) {
            this.setupAndroidOptimizations();
        }

        this.initialized = true;
        this.dispatchInitEvent();
    }

    // ===== VIEWPORT SYSTEM (2025 Standard) =====
    setupViewportSystem() {
        // Modern viewport approach using CSS Custom Properties
        const setViewportProperties = () => {
            const vw = window.innerWidth * 0.01;
            const vh = window.innerHeight * 0.01;

            // Standard viewport units
            document.documentElement.style.setProperty('--vw', `${vw}px`);
            document.documentElement.style.setProperty('--vh', `${vh}px`);

            // Safe viewport (accounting for UI elements)
            const safeVh = this.device.iOS ? window.innerHeight * 0.01 : vh;
            document.documentElement.style.setProperty('--safe-vh', `${safeVh}px`);

            // Dynamic viewport for modern browsers
            if (this.capabilities.supportsDynamicViewport) {
                document.documentElement.style.setProperty('--dvh', '1dvh');
                document.documentElement.style.setProperty('--svh', '1svh');
                document.documentElement.style.setProperty('--lvh', '1lvh');
            } else {
                // Fallback for older browsers
                document.documentElement.style.setProperty('--dvh', `${vh}px`);
                document.documentElement.style.setProperty('--svh', `${safeVh}px`);
                document.documentElement.style.setProperty('--lvh', `${vh}px`);
            }

            // Device-specific adjustments
            if (this.device.iOS && this.device.safari) {
                this.handleIOSViewportQuirks();
            }
        };

        // Initial setup
        setViewportProperties();

        // Optimized resize handling
        this.setupViewportResizeHandler(setViewportProperties);

        // Notify callbacks після встановлення
        this.notifyViewportChange();
    }

    setupViewportResizeHandler(callback) {
        let resizeTimeout;
        let orientationTimeout;

        const debouncedCallback = () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                callback();
                // Відправляємо подію для інших систем
                this.dispatchViewportChangeEvent();
                // Викликаємо callbacks
                this.notifyViewportChange();
            }, 100);
        };

        // Standard resize
        window.addEventListener('resize', debouncedCallback, { passive: true });

        // Orientation change (mobile-specific)
        window.addEventListener('orientationchange', () => {
            clearTimeout(orientationTimeout);
            orientationTimeout = setTimeout(() => {
                callback();
                this.handleOrientationChange();
                this.dispatchViewportChangeEvent();
            }, 250);
        });

        // Visual viewport API (modern browsers)
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', debouncedCallback, { passive: true });
        }
    }

    // ===== iOS SAFARI OPTIMIZATIONS =====
    setupIOSSafariOptimizations() {
        // Add iOS class for CSS targeting
        document.documentElement.classList.add('ios', 'safari');

        if (this.device.iOSVersion >= 17) {
            document.documentElement.classList.add('ios-17');
        }

        // Handle iOS Safari viewport bugs
        this.fixIOSSafariScrollBounce();
        this.optimizeIOSSafariPerformance();

        // Prevent zoom on input focus (accessibility compliant)
        this.preventIOSZoomOnInputs();
    }

    handleIOSViewportQuirks() {
        // iOS Safari changes viewport when URL bar shows/hides
        const initialHeight = window.innerHeight;
        let isURLBarVisible = false;

        const checkURLBar = () => {
            const currentHeight = window.innerHeight;
            const heightDiff = Math.abs(initialHeight - currentHeight);

            if (heightDiff > 40) { // URL bar threshold
                isURLBarVisible = currentHeight < initialHeight;
                document.documentElement.classList.toggle('url-bar-visible', isURLBarVisible);
            }
        };

        window.addEventListener('resize', checkURLBar, { passive: true });

        // Prevent elastic scrolling issues
        document.addEventListener('touchmove', (e) => {
            if (this.isRootScrollableElement(e.target)) {
                const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
                const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight;
                const clientHeight = document.documentElement.clientHeight || window.innerHeight;

                // Prevent overscroll at top/bottom
                if ((scrollTop === 0 && e.touches[0].clientY > e.changedTouches[0].clientY) ||
                    (scrollTop + clientHeight >= scrollHeight && e.touches[0].clientY < e.changedTouches[0].clientY)) {
                    e.preventDefault();
                }
            }
        }, { passive: false });
    }

    // ===== TOUCH OPTIMIZATIONS =====
    setupTouchOptimizations() {
        if (!this.device.isTouch) return;

        // Modern touch handling
        this.setupTouchFeedback();
        this.setupTouchAccessibility();
        this.optimizeTouchPerformance();

        // Prevent accidental zoom
        this.preventAccidentalZoom();
    }

    setupTouchFeedback() {
        // Add touch-active class for instant feedback
        const touchElements = document.querySelectorAll(
            'button, [role="button"], .btn, .nav-link, .card-link, [onclick], [data-modal]'
        );

        touchElements.forEach(element => {
            this.addTouchFeedback(element);
        });

        // Observer for dynamically added elements
        if (this.capabilities.supportsIntersectionObserver) {
            this.observeNewTouchElements();
        }
    }

    addTouchFeedback(element) {
        let touchStartTime = 0;
        let touchTimeout;

        element.addEventListener('touchstart', (e) => {
            touchStartTime = Date.now();
            element.classList.add('touch-active');

            // Haptic feedback for supported devices
            if (this.capabilities.supportsVibration && this.device.iOS) {
                navigator.vibrate(10);
            }

            clearTimeout(touchTimeout);
        }, { passive: true });

        element.addEventListener('touchend', (e) => {
            const touchDuration = Date.now() - touchStartTime;

            // Maintain feedback for minimum time for visual consistency
            const minFeedbackTime = 100;
            const remainingTime = Math.max(0, minFeedbackTime - touchDuration);

            touchTimeout = setTimeout(() => {
                element.classList.remove('touch-active');
            }, remainingTime);
        }, { passive: true });

        element.addEventListener('touchcancel', () => {
            element.classList.remove('touch-active');
            clearTimeout(touchTimeout);
        }, { passive: true });
    }

    // ===== PERFORMANCE OPTIMIZATIONS =====
    setupPerformanceOptimizations() {
        // Optimize animations based on device capabilities
        if (this.device.isLowEnd || this.device.prefersReducedMotion) {
            document.documentElement.classList.add('reduce-motion');
        }

        // Optimize scroll performance
        this.setupOptimizedScrolling();

        // Lazy loading optimizations
        this.setupIntelligentLazyLoading();

        // Memory management
        this.setupMemoryOptimizations();
    }

    setupOptimizedScrolling() {
        let isScrolling = false;
        let scrollTimeout;

        const handleScroll = () => {
            if (!isScrolling) {
                document.documentElement.classList.add('is-scrolling');
                isScrolling = true;
            }

            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                document.documentElement.classList.remove('is-scrolling');
                isScrolling = false;
            }, 150);
        };

        // Use passive listeners for better performance
        window.addEventListener('scroll', handleScroll, { passive: true });
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
        // Heuristics for low-end device detection
        const memory = navigator.deviceMemory || 4; // Default to 4GB if unknown
        const cores = navigator.hardwareConcurrency || 4;
        const connection = navigator.connection;

        return memory < 3 || cores < 4 ||
            (connection && (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g'));
    }

    async testAutoplaySupport() {
        try {
            const video = document.createElement('video');
            video.muted = true;
            video.playsInline = true;
            video.src = 'data:video/mp4;base64,AAAAHGZ0eXBNUDQyAAACAEEQQOQCAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';

            const playResult = await video.play();
            return true;
        } catch (error) {
            return false;
        }
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

    /**
     * Реєстрація callback для viewport updates
     * Дозволяє іншим модулям підписатись на зміни viewport
     */
    onViewportChange(callback) {
        this.viewportUpdateCallbacks.push(callback);
    }

    /**
     * Виклик всіх зареєстрованих callbacks
     */
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

    // Додаткові методи для зовнішнього використання
    testHEVCSupport() {
        return false; // TODO: implement
    }

    testWebPSupport() {
        return false; // TODO: implement
    }

    setupIntelligentLazyLoading() {
        // Placeholder для майбутньої реалізації
    }

    setupMemoryOptimizations() {
        // Placeholder для майбутньої реалізації
    }

    observeNewTouchElements() {
        // Placeholder для майбутньої реалізації
    }

    setupTouchAccessibility() {
        // Placeholder для майбутньої реалізації
    }

    optimizeTouchPerformance() {
        // Placeholder для майбутньої реалізації
    }

    preventAccidentalZoom() {
        // Базовий метод для запобігання zoom
        const inputs = document.querySelectorAll(
            'input[type="text"], input[type="tel"], input[type="email"], textarea, select'
        );

        inputs.forEach(input => {
            if (!input.style.fontSize || parseInt(input.style.fontSize) < 16) {
                input.style.fontSize = '16px';
            }
        });
    }

    setupAndroidOptimizations() {
        // Android-specific optimizations
        document.documentElement.classList.add('android');
    }

    fixIOSSafariScrollBounce() {
        // Prevent elastic scroll
        document.documentElement.style.overscrollBehavior = 'none';
    }

    optimizeIOSSafariPerformance() {
        // Performance optimizations для iOS
        const videos = document.querySelectorAll('video');
        videos.forEach(video => {
            video.setAttribute('playsinline', '');
            video.setAttribute('webkit-playsinline', '');
        });
    }

    preventIOSZoomOnInputs() {
        this.preventAccidentalZoom();
    }

    handleOrientationChange() {
        // Placeholder
    }
}

// ===== GLOBAL INSTANCE =====
window.MobileCore = new MobileCore();
