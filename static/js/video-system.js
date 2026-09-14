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

        this.sharedKeepaliveTimer = null;
    }

    // ===== INITIALIZATION =====
    async init() {
        // Перевірка autoplay
        this.autoplaySupported = await this.testAutoplaySupport();

        // Визначення стратегії
        this.loadingStrategy = this.determineLoadingStrategy();

        // Налаштування observers
        this.setupObservers();

        // Обробка відео на сторінці
        await this.processPageVideos();

        this.setupSharedVideoGroups();

        // Event listeners
        this.setupEventListeners();
    }

    getSharedVideoLeader(element) {
        const key = element.getAttribute('data-shared-video');
        if (!key) {
            return null;
        }

        const siblings = document.querySelectorAll(`video[data-shared-video="${key}"]`);
        for (const sibling of siblings) {
            const siblingData = this.videos.get(sibling);
            if (siblingData?.loaded && sibling.readyState >= 2) {
                return sibling;
            }
        }

        return null;
    }

    setupSharedVideoGroups() {
        const sharedVideos = document.querySelectorAll('video[data-shared-video]');
        if (!sharedVideos.length) {
            return;
        }

        const groups = new Map();
        sharedVideos.forEach((video) => {
            const key = video.getAttribute('data-shared-video');
            if (!groups.has(key)) {
                groups.set(key, []);
            }
            groups.get(key).push(video);
        });

        const keepGroupPlaying = (videos) => {
            if (document.hidden) {
                return;
            }

            videos.forEach((video) => {
                if (video.paused && video.readyState >= 2) {
                    video.play().catch(() => { });
                }
            });
        };

        groups.forEach((videos) => {
            if (videos.length < 2) {
                return;
            }

            const leader = videos[0];

            leader.addEventListener('timeupdate', () => {
                const time = leader.currentTime;
                videos.forEach((video) => {
                    if (video === leader) {
                        return;
                    }
                    if (Math.abs(video.currentTime - time) > 0.35) {
                        try {
                            video.currentTime = time;
                        } catch (error) {
                            /* ignore seek errors on iOS */
                        }
                    }
                });
            });

            videos.forEach((video) => {
                video.addEventListener('pause', () => {
                    if (!document.hidden) {
                        window.setTimeout(() => keepGroupPlaying(videos), 50);
                    }
                });
                video.addEventListener('stalled', () => keepGroupPlaying(videos));
                video.addEventListener('waiting', () => keepGroupPlaying(videos));
            });

            keepGroupPlaying(videos);
        });

        if (this.sharedKeepaliveTimer) {
            window.clearInterval(this.sharedKeepaliveTimer);
        }

        this.sharedKeepaliveTimer = window.setInterval(() => {
            groups.forEach((videos) => keepGroupPlaying(videos));
        }, 2500);
    }

    // ===== AUTOPLAY DETECTION =====
    async testAutoplaySupport() {
        const video = document.createElement('video');
        video.muted = true;
        video.playsInline = true;
        video.hidden = true;
        video.width = 1;
        video.height = 1;
        video.setAttribute('aria-hidden', 'true');

        try {
            const testVideoSrc = 'data:video/mp4;base64,AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQAAAu1tZGF0';
            video.src = testVideoSrc;

            document.body.appendChild(video);

            const playPromise = video.play();

            if (playPromise instanceof Promise) {
                await playPromise;
                return true;
            }

            return false;
        } catch (error) {
            return false;
        } finally {
            video.remove();
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
                if (entry.isIntersecting) {
                    this.loadVideoForElement(entry.target);
                }
            });
        }, {
            rootMargin: this.config.lazyLoadMargin,
            threshold: this.config.lazyLoadThreshold
        });
    }

    isMobileViewport() {
        return window.matchMedia('(max-width: 767px)').matches;
    }

    isVideoForCurrentViewport(video) {
        const isMobile = this.isMobileViewport();
        if (video.classList.contains('desktop-video') && isMobile) return false;
        if (video.classList.contains('mobile-video') && !isMobile) return false;
        return true;
    }

    lazyObserveRoot(video) {
        return video.closest('section, .hero-section, .cta-section, .project-section')
            || video.parentElement
            || video;
    }

    applyViewportSource(video) {
        const sources = Array.from(video.querySelectorAll('source'));
        if (!sources.length && !video.getAttribute('data-src')) {
            return;
        }

        if (video.currentSrc) {
            const already = sources.some((source) => {
                const url = source.getAttribute('src') || source.getAttribute('data-src');
                return url && video.currentSrc.indexOf(url) !== -1;
            });
            if (already) {
                video.removeAttribute('data-src');
                sources.forEach((source) => source.removeAttribute('data-src'));
                return;
            }
        }

        let chosenUrl = null;
        for (const source of sources) {
            const media = source.getAttribute('media');
            const url = source.getAttribute('src') || source.getAttribute('data-src');
            if (!url) continue;
            if (!media || window.matchMedia(media).matches) {
                chosenUrl = url;
                break;
            }
        }
        if (!chosenUrl && sources.length) {
            const last = sources[sources.length - 1];
            chosenUrl = last.getAttribute('src') || last.getAttribute('data-src');
        }
        if (!chosenUrl) {
            chosenUrl = video.getAttribute('data-src');
        }
        if (chosenUrl && video.getAttribute('src') !== chosenUrl) {
            video.src = chosenUrl;
        }
        video.removeAttribute('data-src');
        sources.forEach((source) => source.removeAttribute('data-src'));
    }

    // ===== PAGE VIDEOS PROCESSING =====
    async processPageVideos() {
        const standardVideos = document.querySelectorAll(
            '.video-background:not(.lazy-video), .hero-video:not(.lazy-video)'
        );

        for (const video of standardVideos) {
            if (!this.isVideoForCurrentViewport(video)) continue;
            await this.processVideo(video, 'standard');
        }

        const lazyVideos = document.querySelectorAll('.lazy-video');

        lazyVideos.forEach(video => {
            if (!this.isVideoForCurrentViewport(video)) return;

            const videoData = {
                element: video,
                mode: 'lazy',
                loaded: false,
                playing: false,
                container: video.closest('[data-video-container]') || video.parentElement
            };

            this.videos.set(video, videoData);
            this.optimizeVideoAttributes(video);

            if (this.observers.intersection) {
                this.observers.intersection.observe(this.lazyObserveRoot(video));
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
            const isMobile = this.isMobileViewport();
            const selector = isMobile
                ? 'video.lazy-video.mobile-video, video.lazy-video:not(.desktop-video)'
                : 'video.lazy-video.desktop-video, video.lazy-video:not(.mobile-video)';
            video = element.querySelector(selector);

            if (!video) {
                video = element.querySelector('video.lazy-video');
            }
        }

        if (video && !this.isVideoForCurrentViewport(video)) {
            return;
        }

        if (!video) {
            return;
        }

        const videoData = this.videos.get(video);
        if (!videoData) {
            // Якщо відео не зареєстроване, реєструємо його
            await this.processVideo(video, 'lazy');
            return;
        }

        if (videoData.loaded) {
            return;
        }

        await this.loadVideo(videoData);
    }

    isHeroBackgroundVideo(element) {
        return element.classList.contains('video-background') && !element.classList.contains('lazy-video');
    }

    async loadVideo(videoData) {
        const { element, container } = videoData;
        const isHeroBackground = this.isHeroBackgroundVideo(element);

        try {
            this.applyViewportSource(element);
            element.classList.remove('lazy-video');

            const sharedLeader = this.getSharedVideoLeader(element);

            if (sharedLeader && sharedLeader !== element) {
                if (element.readyState < 2) {
                    element.load();
                    await this.waitForVideoReady(element);
                }

                try {
                    element.currentTime = sharedLeader.currentTime;
                } catch (error) {
                    /* ignore seek errors */
                }

                videoData.loaded = true;

                if (isHeroBackground || this.autoplaySupported) {
                    await this.attemptAutoplay(videoData);
                }

                this.emit('video:loaded', { element, container });
                return;
            }

            const hasSource = Boolean(element.src || element.querySelector('source[src]'));
            const alreadyReady = element.readyState >= 2;

            if (!(isHeroBackground && hasSource && alreadyReady)) {
                element.load();
            }

            await this.waitForVideoReady(element);

            videoData.loaded = true;

            if (isHeroBackground || this.autoplaySupported) {
                await this.attemptAutoplay(videoData);
            }

            this.emit('video:loaded', { element, container });

        } catch (error) {
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

        if (video.classList.contains('lazy-video')) {
            video.preload = 'none';
            return;
        }

        video.preload = this.loadingStrategy === 'minimal' ? 'none' : 'metadata';
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
            element.classList.add('is-playing');
            this.emit('video:playing', { element });
        } catch (error) {
            this.emit('video:autoplay-failed', { element });
        }
    }

    handleVideoError(videoData, error) {
        const { element, container } = videoData;

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
            const { element } = videoData;
            if (!element.paused) {
                element.pause();
            }
            videoData.playing = false;
        });
    }

    resumeAll() {
        this.videos.forEach((videoData) => {
            const { element } = videoData;
            if (videoData.loaded && element.paused) {
                element.play().then(() => {
                    videoData.playing = true;
                }).catch(() => { });
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
