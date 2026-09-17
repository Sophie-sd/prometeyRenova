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
                    // Не чіпати ще не завантажені follower-и (readyState 0):
                    // desktop-приховані відео не повинні ініціювати мережевий запит.
                    if (video.readyState < 1) {
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
        let video = null;
        try {
            video = document.createElement('video');
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
                return true;
            }

            return false;
        } catch (error) {
            return false;
        } finally {
            // Прибираємо тестовий елемент завжди — і при успіху, і при відхиленні
            // play(), щоб не лишати мертвий <video> у DOM на кожному завантаженні.
            if (video) {
                video.remove();
            }
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

        // Observer для follower-відео (piano/cta): активуємо, коли секція
        // наближається до viewport (fallback, якщо leader ще не в кеші).
        // Не активний на сторінках без data-video-role="follower" розмітки.
        this.observers.followers = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const activate = this._followerActivators?.get(entry.target);
                if (activate) activate();
                this.observers.followers.unobserve(entry.target);
            });
        }, {
            rootMargin: '100% 0px',
            threshold: 0
        });
    }

    // ===== PAGE VIDEOS PROCESSING =====
    async processPageVideos() {
        // Standard videos (hero, cta)
        const allVideos = document.querySelectorAll(
            '.video-background:not(.lazy-video), .hero-video:not(.lazy-video)'
        );

        // Follower-відео (piano/cta, тільки якщо є data-video-role="follower" —
        // сьогодні це виключно homepage-розмітка, тому на решті сторінок цей
        // блок ніколи не спрацьовує і поведінка лишається незмінною).
        const followerVideos = [];
        const standardVideos = Array.from(allVideos).filter(video => {
            if (video.getAttribute('data-video-role') === 'follower') {
                followerVideos.push(video);
                return false;
            }
            return true;
        });

        for (const video of standardVideos) {
            await this.processVideo(video, 'standard');
        }

        if (followerVideos.length) {
            if (window.innerWidth <= 767) {
                const leader = standardVideos.find(v => v.getAttribute('data-video-role') === 'leader') || standardVideos[0];
                this.scheduleFollowers(leader, followerVideos);
            }

            if (!this._followerMediaQuery) {
                this._followerMediaQuery = window.matchMedia('(max-width: 767px)');
                this._followerMediaQuery.addEventListener('change', (event) => {
                    if (!event.matches) return;
                    const pending = followerVideos.filter(video => !this.videos.get(video)?.loaded);
                    if (!pending.length) return;
                    const leader = document.querySelector('video[data-video-role="leader"]') || standardVideos[0];
                    this.scheduleFollowers(leader, pending);
                });
            }
        }

        // Lazy videos (portfolio projects)
        const lazyVideos = document.querySelectorAll('.lazy-video');

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
                this.observers.intersection.observe(container);
            }
        });
    }

    /**
     * Follower-відео (piano/cta) активуються тільки на mobile, тільки коли:
     *  a) leader повністю в буфері (0 нових байтів — грає з HTTP-кешу), або
     *  b) секція follower-а наближається до viewport (fallback на повільній мережі), або
     *  c) 10s таймаут / помилка leader-а (щоб ніколи не залишити секцію без відео).
     */
    scheduleFollowers(leader, followers) {
        if (!leader || !followers || !followers.length) return;

        const pending = new Map();
        followers.forEach(video => {
            if (this.videos.get(video)?.loaded) return;
            pending.set(video, video.closest('section') || video.parentElement);
        });

        if (!pending.size) return;

        let settled = false;
        let timeoutId = null;

        const cleanup = () => {
            clearTimeout(timeoutId);
            leader.removeEventListener('progress', onLeaderProgress);
            leader.removeEventListener('canplaythrough', onLeaderProgress);
            leader.removeEventListener('error', onLeaderError);
            if (this.observers.followers) {
                pending.forEach((section) => {
                    if (section) this.observers.followers.unobserve(section);
                });
            }
        };

        const activateAll = () => {
            if (settled) return;
            settled = true;
            cleanup();
            pending.forEach((section, video) => this.processVideo(video, 'standard'));
        };

        const activateOne = (video) => {
            if (settled || !pending.has(video)) return;
            pending.delete(video);
            this.processVideo(video, 'standard');
            if (!pending.size) {
                settled = true;
                cleanup();
            }
        };

        const onLeaderProgress = () => {
            if (!leader.duration || !leader.buffered || !leader.buffered.length) return;
            try {
                const bufferedEnd = leader.buffered.end(leader.buffered.length - 1);
                if (bufferedEnd >= leader.duration - 0.3) {
                    activateAll();
                }
            } catch (error) {
                /* ignore TimeRanges edge cases */
            }
        };

        const onLeaderError = () => activateAll();

        timeoutId = window.setTimeout(activateAll, this.config.loadTimeout);

        leader.addEventListener('progress', onLeaderProgress);
        leader.addEventListener('canplaythrough', onLeaderProgress);
        leader.addEventListener('error', onLeaderError, { once: true });
        onLeaderProgress();

        if (this.observers.followers) {
            this._followerActivators = this._followerActivators || new WeakMap();
            pending.forEach((section, video) => {
                if (!section) return;
                this._followerActivators.set(section, () => activateOne(video));
                this.observers.followers.observe(section);
            });
        }
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
        const sharedLeader = this.getSharedVideoLeader(element);

        try {
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

            // Якщо є data-src, переносимо в src
            if (element.hasAttribute('data-src')) {
                const dataSrc = element.getAttribute('data-src');
                element.src = dataSrc;
                element.removeAttribute('data-src');

                // Також для source
                const source = element.querySelector('source[data-src]');
                if (source) {
                    const sourceSrc = source.getAttribute('data-src');
                    source.src = sourceSrc;
                    source.removeAttribute('data-src');
                }

                element.classList.remove('lazy-video');
            }

            const hasSource = Boolean(element.src || element.querySelector('source[src]'));
            const alreadyReady = element.readyState >= 2;

            if (!(isHeroBackground && hasSource && alreadyReady)) {
                element.load();
            }

            await this.waitForVideoReady(element);

            videoData.loaded = true;
            this.ensureResponsiveSource(element);

            if (isHeroBackground || this.autoplaySupported) {
                await this.attemptAutoplay(videoData);
            }

            this.emit('video:loaded', { element, container });

        } catch (error) {
            this.handleVideoError(videoData, error);
        }
    }

    /**
     * Захист для браузерів, які ігнорують <source media="..."> (напр. дуже старі
     * Chromium/WebView): після завантаження leader-а звіряємо currentSrc з тим,
     * що мало би підійти під поточний viewport, і за потреби перемикаємо вручну.
     */
    ensureResponsiveSource(video) {
        if (video.getAttribute('data-video-role') !== 'leader') return;

        const sources = Array.from(video.querySelectorAll('source[media]'));
        if (!sources.length) return;

        let matched = sources.find(source => {
            const query = source.getAttribute('media');
            return query && window.matchMedia(query).matches;
        });

        if (!matched) {
            matched = video.querySelector('source:not([media])');
        }
        if (!matched || !matched.src) return;

        const matchedUrl = new URL(matched.src, location.href).href;
        const currentUrl = video.currentSrc ? new URL(video.currentSrc, location.href).href : '';

        if (currentUrl && currentUrl !== matchedUrl) {
            const wasPlaying = !video.paused;
            video.src = matched.src;
            video.load();
            if (wasPlaying) {
                video.play().catch(() => { });
            }
        }
    }

    optimizeVideoAttributes(video) {
        video.muted = true;
        video.playsInline = true;
        video.loop = true;
        video.controls = false;

        video.setAttribute('playsinline', '');
        video.setAttribute('webkit-playsinline', '');

        if (this.isHeroBackgroundVideo(video)) {
            video.preload = 'auto';
            return;
        }

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
