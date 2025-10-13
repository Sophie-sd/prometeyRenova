/**
 * VIDEO-SYSTEM.JS - Універсальна відео система (2025)
 * Підтримує: hero videos, background videos, lazy project videos
 * БЕЗ конфліктів, єдина система для всіх сторінок
 */

class VideoSystem {
    constructor() {
        this.videos = new Map();
        this.autoplaySupported = null;
        this.loadingStrategy = null;
        this.observers = {
            intersection: null,
            visibility: null
        };

        this.config = {
            lazyLoadMargin: '100px',
            lazyLoadThreshold: 0.2,
            loadTimeout: 10000
        };
    }

    // ===== INITIALIZATION =====
    async init() {
        console.log('[VideoSystem] Starting initialization...');

        // Перевірка autoplay
        this.autoplaySupported = await this.testAutoplaySupport();
        console.log('[VideoSystem] Autoplay supported:', this.autoplaySupported);

        // Визначення стратегії
        this.loadingStrategy = this.determineLoadingStrategy();
        console.log('[VideoSystem] Loading strategy:', this.loadingStrategy);

        // Налаштування observers
        this.setupObservers();
        console.log('[VideoSystem] Observers set up');

        // Обробка відео на сторінці
        await this.processPageVideos();
        console.log('[VideoSystem] Page videos processed');

        // Event listeners
        this.setupEventListeners();
        console.log('[VideoSystem] Event listeners set up');

        console.log('[VideoSystem] ✅ Initialization complete:', {
            autoplay: this.autoplaySupported,
            strategy: this.loadingStrategy,
            registeredVideos: this.videos.size
        });
    }

    // ===== AUTOPLAY DETECTION =====
    async testAutoplaySupport() {
        try {
            const video = document.createElement('video');
            video.muted = true;
            video.playsInline = true;
            video.style.cssText = 'position:absolute;opacity:0;left:-9999px';

            // Мінімальне тестове відео
            const testVideoSrc = 'data:video/mp4;base64,AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQAAAu1tZGF0';
            video.src = testVideoSrc;

            document.body.appendChild(video);

            const playPromise = video.play();

            if (playPromise instanceof Promise) {
                await playPromise;
                video.remove();
                return true;
            }

            video.remove();
            return false;
        } catch (error) {
            return false;
        }
    }

    // ===== LOADING STRATEGY =====
    determineLoadingStrategy() {
        const device = window.MobileCore?.getDevice() || {};
        const connection = navigator.connection;

        if (device.isLowEnd || connection?.effectiveType === 'slow-2g') {
            return 'minimal';
        } else if (device.isMobile || connection?.effectiveType === '2g') {
            return 'lazy';
        } else if (connection?.effectiveType === '3g') {
            return 'progressive';
        }
        return 'eager';
    }

    // ===== OBSERVERS SETUP =====
    setupObservers() {
        if (!('IntersectionObserver' in window)) return;

        // Observer для lazy loading
        this.observers.intersection = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                console.log('[VideoSystem] Intersection change:', {
                    target: entry.target,
                    isIntersecting: entry.isIntersecting,
                    intersectionRatio: entry.intersectionRatio
                });

                if (entry.isIntersecting) {
                    console.log('[VideoSystem] Element became visible, loading video');
                    this.loadVideoForElement(entry.target);
                }
            });
        }, {
            rootMargin: this.config.lazyLoadMargin,
            threshold: this.config.lazyLoadThreshold
        });
    }

    // ===== PAGE VIDEOS PROCESSING =====
    async processPageVideos() {
        // Standard videos (hero, cta)
        const standardVideos = document.querySelectorAll(
            '.video-background:not(.lazy-video), .hero-video:not(.lazy-video)'
        );

        console.log('[VideoSystem] Found standard videos:', standardVideos.length);

        for (const video of standardVideos) {
            await this.processVideo(video, 'standard');
        }

        // Lazy videos (portfolio projects)
        const lazyVideos = document.querySelectorAll('.lazy-video');

        console.log('[VideoSystem] Found lazy videos:', lazyVideos.length);

        lazyVideos.forEach(video => {
            // Реєструємо відео в системі але не завантажуємо
            const videoData = {
                element: video,
                mode: 'lazy',
                loaded: false,
                playing: false,
                container: video.closest('[data-video-container]') || video.parentElement
            };

            this.videos.set(video, videoData);
            this.optimizeVideoAttributes(video);

            // Спостерігаємо за контейнером
            if (this.observers.intersection) {
                const container = video.closest('.project-section') || video;
                console.log('[VideoSystem] Observing lazy video:', video, 'in container:', container);
                this.observers.intersection.observe(container);
            }
        });
    }

    // ===== VIDEO PROCESSING =====
    async processVideo(videoElement, mode = 'standard') {
        if (!videoElement) return;

        const videoData = {
            element: videoElement,
            mode,
            loaded: false,
            playing: false,
            container: videoElement.closest('[data-video-container]') || videoElement.parentElement
        };

        this.videos.set(videoElement, videoData);

        // Оптимізація атрибутів
        this.optimizeVideoAttributes(videoElement);

        // Стратегія завантаження
        if (mode === 'lazy' || videoElement.classList.contains('lazy-video')) {
            await this.setupLazyVideo(videoData);
        } else {
            await this.loadVideo(videoData);
        }
    }

    async setupLazyVideo(videoData) {
        const { element } = videoData;

        // Чекаємо поки відео стане видимим
        // Observer вже налаштований в processPageVideos
    }

    async loadVideoForElement(element) {
        let video = null;

        if (element.tagName === 'VIDEO') {
            video = element;
        } else {
            // Визначаємо яке відео завантажувати (desktop або mobile)
            const isMobile = window.innerWidth <= 767;
            const selector = isMobile ? 'video.lazy-video.mobile-video' : 'video.lazy-video.desktop-video';
            video = element.querySelector(selector);

            // Fallback на будь-яке lazy відео
            if (!video) {
                video = element.querySelector('video.lazy-video');
            }
        }

        if (!video) {
            console.log('[VideoSystem] No video found in element:', element);
            return;
        }

        console.log('[VideoSystem] Loading video for element:', video);

        const videoData = this.videos.get(video);
        if (!videoData) {
            console.log('[VideoSystem] No video data, registering video:', video);
            // Якщо відео не зареєстроване, реєструємо його
            await this.processVideo(video, 'lazy');
            return;
        }

        if (videoData.loaded) {
            console.log('[VideoSystem] Video already loaded:', video);
            return;
        }

        await this.loadVideo(videoData);
    }

    async loadVideo(videoData) {
        const { element, container } = videoData;

        try {
            console.log('[VideoSystem] Loading video:', element);

            // Якщо є data-src, переносимо в src
            if (element.hasAttribute('data-src')) {
                const dataSrc = element.getAttribute('data-src');
                console.log('[VideoSystem] Setting src from data-src:', dataSrc);
                element.src = dataSrc;
                element.removeAttribute('data-src');

                // Також для source
                const source = element.querySelector('source[data-src]');
                if (source) {
                    const sourceSrc = source.getAttribute('data-src');
                    console.log('[VideoSystem] Setting source src:', sourceSrc);
                    source.src = sourceSrc;
                    source.removeAttribute('data-src');
                }

                element.classList.remove('lazy-video');
            }

            // Завантаження
            element.load();

            // Очікування готовності
            await this.waitForVideoReady(element);

            videoData.loaded = true;
            console.log('[VideoSystem] Video loaded successfully:', element.src);

            // Автоплей якщо підтримується
            if (this.autoplaySupported) {
                await this.attemptAutoplay(videoData);
            }

            // Event
            this.emit('video:loaded', { element, container });

        } catch (error) {
            console.error('[VideoSystem] Video load error:', error);
            this.handleVideoError(videoData, error);
        }
    }

    optimizeVideoAttributes(video) {
        video.muted = true;
        video.playsInline = true;
        video.loop = true;
        video.controls = false;

        video.setAttribute('playsinline', '');
        video.setAttribute('webkit-playsinline', '');

        // Preload strategy
        const isMobile = window.innerWidth <= 767;
        if (isMobile) {
            video.preload = this.loadingStrategy === 'minimal' ? 'none' : 'metadata';
        } else {
            video.preload = video.classList.contains('lazy-video') ? 'none' : 'auto';
        }
    }

    async waitForVideoReady(video) {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Video loading timeout'));
            }, this.config.loadTimeout);

            const onReady = () => {
                clearTimeout(timeout);
                cleanup();
                resolve();
            };

            const onError = (error) => {
                clearTimeout(timeout);
                cleanup();
                reject(error);
            };

            const cleanup = () => {
                video.removeEventListener('loadeddata', onReady);
                video.removeEventListener('error', onError);
            };

            if (video.readyState >= 2) {
                resolve();
            } else {
                video.addEventListener('loadeddata', onReady);
                video.addEventListener('error', onError);
            }
        });
    }

    async attemptAutoplay(videoData) {
        const { element } = videoData;

        try {
            await element.play();
            videoData.playing = true;
            this.emit('video:playing', { element });
        } catch (error) {
            console.log('Autoplay prevented:', error);
            this.emit('video:autoplay-failed', { element });
        }
    }

    handleVideoError(videoData, error) {
        const { element, container } = videoData;

        console.error('Video error:', error);
        element.style.display = 'none';

        this.emit('video:error', { element, container, error });
    }

    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // Visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAll();
            } else {
                this.resumeAll();
            }
        });

        // Connection change
        if (navigator.connection) {
            navigator.connection.addEventListener('change', () => {
                this.handleConnectionChange();
            });
        }
    }

    handleConnectionChange() {
        const connection = navigator.connection;
        if (connection?.effectiveType === 'slow-2g' || connection?.effectiveType === '2g') {
            this.pauseAll();
        }
    }

    // ===== CONTROL METHODS =====
    pauseAll() {
        this.videos.forEach((videoData) => {
            if (videoData.playing && !videoData.element.paused) {
                videoData.element.pause();
            }
        });
    }

    resumeAll() {
        this.videos.forEach((videoData) => {
            if (videoData.loaded && !videoData.playing && this.autoplaySupported) {
                videoData.element.play().catch(() => { });
            }
        });
    }

    pauseVideo(videoElement) {
        const videoData = this.videos.get(videoElement);
        if (videoData && !videoElement.paused) {
            videoElement.pause();
            videoData.playing = false;
        }
    }

    playVideo(videoElement) {
        const videoData = this.videos.get(videoElement);
        if (videoData && videoElement.paused && videoData.loaded) {
            videoElement.play().catch(() => { });
            videoData.playing = true;
        }
    }

    // ===== PUBLIC API =====
    async addVideo(videoElement, mode = 'standard') {
        await this.processVideo(videoElement, mode);
    }

    removeVideo(videoElement) {
        this.videos.delete(videoElement);
    }

    getVideoData(videoElement) {
        return this.videos.get(videoElement);
    }

    isAutoplaySupported() {
        return this.autoplaySupported;
    }

    /**
     * Register element for lazy loading
     */
    observeLazy(element) {
        if (this.observers.intersection) {
            this.observers.intersection.observe(element);
        }
    }

    /**
     * Unregister from lazy loading
     */
    unobserveLazy(element) {
        if (this.observers.intersection) {
            this.observers.intersection.unobserve(element);
        }
    }

    // ===== EVENT BUS =====
    emit(eventName, data) {
        const event = new CustomEvent(`videosystem:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }

    on(eventName, callback) {
        document.addEventListener(`videosystem:${eventName}`, callback);
    }

    off(eventName, callback) {
        document.removeEventListener(`videosystem:${eventName}`, callback);
    }
}

// ===== GLOBAL INSTANCE =====
window.VideoSystem = new VideoSystem();

// Auto initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.VideoSystem.init();
    });
} else {
    window.VideoSystem.init();
}
