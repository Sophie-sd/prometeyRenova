/**
 * VIDEO-SYSTEM.JS - Сучасна відео система з fallbacks (2025)
 * Розумне завантаження, autoplay detection, performance оптимізації
 */

class VideoSystem {
    constructor() {
        this.videos = new Map();
        this.autoplaySupported = null;
        this.loadingStrategy = this.determineLoadingStrategy();
        this.observer = null;

        this.init();
    }

    // ===== INITIALIZATION =====
    async init() {
        // Перевіряємо чи відключена система
        if (window.VideoSystemDisabled) {
            console.log('VideoSystem disabled for this page');
            return;
        }

        // Тест підтримки автоплею
        this.autoplaySupported = await this.testAutoplaySupport();

        // Налаштування спостерігача для lazy loading
        this.setupIntersectionObserver();

        // Обробка існуючих відео
        await this.processExistingVideos();

        // Слухачі подій
        this.setupEventListeners();

        console.log('VideoSystem initialized:', {
            autoplaySupported: this.autoplaySupported,
            loadingStrategy: this.loadingStrategy
        });
    }

    // ===== AUTOPLAY DETECTION =====
    async testAutoplaySupport() {
        try {
            const video = document.createElement('video');
            video.muted = true;
            video.playsInline = true;
            video.style.position = 'absolute';
            video.style.opacity = '0';
            video.style.pointerEvents = 'none';
            video.style.left = '-9999px';

            // Мінімальне тестове відео (1px, прозоре)
            video.src = 'data:video/mp4;base64,AAAAIGZ0eXBtcDQyAAACAEEQQOQCAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=';

            document.body.appendChild(video);

            const playPromise = video.play();

            if (playPromise instanceof Promise) {
                await playPromise;
                document.body.removeChild(video);
                return true;
            } else {
                document.body.removeChild(video);
                return false;
            }
        } catch (error) {
            console.log('Autoplay not supported:', error);
            return false;
        }
    }

    // ===== LOADING STRATEGY =====
    determineLoadingStrategy() {
        const device = window.MobileCore?.getDevice() || {};
        const connection = navigator.connection;

        // Визначаємо стратегію завантаження на основі пристрою та з'єднання
        if (device.isLowEnd || (connection && connection.effectiveType === 'slow-2g')) {
            return 'minimal'; // Тільки fallback зображення
        } else if (device.isMobile || (connection && connection.effectiveType === '2g')) {
            return 'lazy'; // Lazy loading з низькою якістю
        } else if (connection && connection.effectiveType === '3g') {
            return 'progressive'; // Прогресивне завантаження
        } else {
            return 'eager'; // Повне завантаження
        }
    }

    // ===== INTERSECTION OBSERVER =====
    setupIntersectionObserver() {
        if (!('IntersectionObserver' in window)) {
            // Fallback для старих браузерів
            this.observer = null;
            return;
        }

        const options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.1
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const container = entry.target;
                    this.loadVideoForContainer(container);
                    this.observer.unobserve(container);
                }
            });
        }, options);
    }

    // ===== VIDEO PROCESSING =====
    async processExistingVideos() {
        const videoContainers = document.querySelectorAll('.video-background, .hero-video, .project-video video');

        for (const container of videoContainers) {
            await this.processVideoContainer(container);
        }
    }

    async processVideoContainer(container) {
        const videoElement = container.tagName === 'VIDEO' ? container : container.querySelector('video');
        if (!videoElement) return;

        const videoData = {
            element: videoElement,
            container: container,
            fallbackImage: this.extractFallbackImage(videoElement),
            loaded: false,
            playing: false
        };

        this.videos.set(container, videoData);

        // Застосування стратегії завантаження
        switch (this.loadingStrategy) {
            case 'minimal':
                await this.showFallbackOnly(videoData);
                break;

            case 'lazy':
                await this.setupLazyLoading(videoData);
                break;

            case 'progressive':
                await this.setupProgressiveLoading(videoData);
                break;

            case 'eager':
            default:
                await this.loadVideoEagerly(videoData);
                break;
        }
    }

    // ===== LOADING STRATEGIES =====

    async showFallbackOnly(videoData) {
        const { element, container, fallbackImage } = videoData;

        if (fallbackImage) {
            container.style.backgroundImage = `url(${fallbackImage})`;
            container.style.backgroundSize = 'cover';
            container.style.backgroundPosition = 'center';
        }

        element.style.display = 'none';
        this.addPlayButton(container, videoData);
    }

    async setupLazyLoading(videoData) {
        const { container } = videoData;

        if (this.observer) {
            this.observer.observe(container);
        } else {
            // Fallback без Intersection Observer
            await this.loadVideoForContainer(container);
        }
    }

    async setupProgressiveLoading(videoData) {
        const { element } = videoData;

        // Встановлюємо низьку якість спочатку
        element.preload = 'metadata';

        if (this.observer) {
            this.observer.observe(videoData.container);
        } else {
            await this.loadVideoForContainer(videoData.container);
        }
    }

    async loadVideoEagerly(videoData) {
        await this.loadVideo(videoData);
    }

    // ===== VIDEO LOADING =====
    async loadVideoForContainer(container) {
        const videoData = this.videos.get(container);
        if (!videoData || videoData.loaded) return;

        await this.loadVideo(videoData);
    }

    async loadVideo(videoData) {
        const { element, container, fallbackImage } = videoData;

        try {
            // Показати fallback під час завантаження
            if (fallbackImage && !container.style.backgroundImage) {
                container.style.backgroundImage = `url(${fallbackImage})`;
                container.style.backgroundSize = 'cover';
                container.style.backgroundPosition = 'center';
            }

            // Оптимізація відео атрибутів
            this.optimizeVideoElement(element);

            // Завантаження відео
            element.load();

            // Очікування готовності
            await this.waitForVideoReady(element);

            // Спроба автоплею
            if (this.autoplaySupported) {
                await this.attemptAutoplay(videoData);
            } else {
                this.addPlayButton(container, videoData);
            }

            videoData.loaded = true;

        } catch (error) {
            console.warn('Failed to load video:', error);
            this.handleVideoError(videoData, error);
        }
    }

    // ===== VIDEO OPTIMIZATION =====
    optimizeVideoElement(video) {
        // Базові оптимізації
        video.muted = true;
        video.playsInline = true;
        video.controls = false;
        video.loop = true;

        // iOS Safari специфіка
        video.setAttribute('playsinline', '');
        video.setAttribute('webkit-playsinline', '');

        // Performance оптимізації
        video.style.willChange = 'transform';

        // Responsive відео
        const isMobile = window.innerWidth <= 767;
        if (isMobile) {
            video.preload = this.loadingStrategy === 'minimal' ? 'none' : 'metadata';
        } else {
            video.preload = 'auto';
        }
    }

    async waitForVideoReady(video) {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Video loading timeout'));
            }, 10000); // 10 секунд timeout

            const onReady = () => {
                clearTimeout(timeout);
                video.removeEventListener('loadeddata', onReady);
                video.removeEventListener('error', onError);
                resolve();
            };

            const onError = (error) => {
                clearTimeout(timeout);
                video.removeEventListener('loadeddata', onReady);
                video.removeEventListener('error', onError);
                reject(error);
            };

            if (video.readyState >= 2) {
                resolve();
            } else {
                video.addEventListener('loadeddata', onReady);
                video.addEventListener('error', onError);
            }
        });
    }

    // ===== AUTOPLAY HANDLING =====
    async attemptAutoplay(videoData) {
        const { element, container } = videoData;

        try {
            const playPromise = element.play();

            if (playPromise instanceof Promise) {
                await playPromise;
                videoData.playing = true;
                this.hideBackgroundImage(container);
                this.removePlayButton(container);
            }

        } catch (error) {
            console.log('Autoplay failed, showing play button:', error);
            this.addPlayButton(container, videoData);
        }
    }

    // ===== PLAY BUTTON =====
    addPlayButton(container, videoData) {
        // Перевіряємо чи вже існує кнопка
        if (container.querySelector('.mobile-video-play-button')) return;

        const playButton = document.createElement('button');
        playButton.className = 'mobile-video-play-button mobile-touch-target';
        playButton.setAttribute('aria-label', 'Відтворити відео');
        playButton.type = 'button';

        playButton.addEventListener('click', async () => {
            await this.handlePlayButtonClick(playButton, videoData);
        });

        container.style.position = 'relative';
        container.appendChild(playButton);
    }

    async handlePlayButtonClick(button, videoData) {
        const { element, container } = videoData;

        try {
            // Показати індикатор завантаження
            button.style.opacity = '0.5';
            button.style.pointerEvents = 'none';

            // Якщо відео не завантажене, завантажуємо
            if (!videoData.loaded) {
                await this.loadVideo(videoData);
            }

            // Відтворення
            await element.play();
            videoData.playing = true;

            // Приховуємо fallback та кнопку
            this.hideBackgroundImage(container);
            this.removePlayButton(container);

            // Haptic feedback
            if (navigator.vibrate) {
                navigator.vibrate(10);
            }

        } catch (error) {
            console.error('Failed to play video:', error);

            // Відновлюємо кнопку
            button.style.opacity = '1';
            button.style.pointerEvents = 'auto';
        }
    }

    removePlayButton(container) {
        const playButton = container.querySelector('.mobile-video-play-button');
        if (playButton) {
            playButton.remove();
        }
    }

    // ===== UTILITY METHODS =====
    extractFallbackImage(videoElement) {
        // Шукаємо fallback зображення в різних місцях
        const poster = videoElement.poster;
        const dataFallback = videoElement.getAttribute('data-fallback');
        const containerFallback = videoElement.closest('[data-video-fallback]')?.getAttribute('data-video-fallback');

        return poster || dataFallback || containerFallback || null;
    }

    hideBackgroundImage(container) {
        container.style.backgroundImage = 'none';
    }

    handleVideoError(videoData, error) {
        const { container, fallbackImage } = videoData;

        console.error('Video error:', error);

        // Показуємо fallback зображення
        if (fallbackImage) {
            container.style.backgroundImage = `url(${fallbackImage})`;
            container.style.backgroundSize = 'cover';
            container.style.backgroundPosition = 'center';
        }

        // Приховуємо відео елемент
        videoData.element.style.display = 'none';
    }

    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // Обробка зміни з'єднання
        if (navigator.connection) {
            navigator.connection.addEventListener('change', () => {
                this.handleConnectionChange();
            });
        }

        // Обробка видимості сторінки
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });

        // Обробка зміни орієнтації
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.handleOrientationChange(), 250);
        });
    }

    handleConnectionChange() {
        const connection = navigator.connection;
        if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
            // Призупиняємо всі відео при повільному з'єднанні
            this.pauseAllVideos();
        }
    }

    handleVisibilityChange() {
        if (document.hidden) {
            this.pauseAllVideos();
        } else {
            // Відновлюємо автоплей відео при поверненні на сторінку
            this.resumeAutoplayVideos();
        }
    }

    handleOrientationChange() {
        // Перераховуємо розміри відео після зміни орієнтації
        this.videos.forEach((videoData) => {
            if (videoData.playing) {
                this.optimizeVideoElement(videoData.element);
            }
        });
    }

    // ===== CONTROL METHODS =====
    pauseAllVideos() {
        this.videos.forEach((videoData) => {
            if (videoData.playing) {
                videoData.element.pause();
            }
        });
    }

    resumeAutoplayVideos() {
        this.videos.forEach((videoData) => {
            if (videoData.loaded && !videoData.playing && this.autoplaySupported) {
                videoData.element.play().catch(() => {
                    // Ignore autoplay failures
                });
            }
        });
    }

    // ===== PUBLIC API =====
    async addVideo(videoElement) {
        await this.processVideoContainer(videoElement.parentElement);
    }

    removeVideo(videoElement) {
        const container = videoElement.parentElement;
        this.videos.delete(container);
    }

    getVideoData(container) {
        return this.videos.get(container);
    }

    isAutoplaySupported() {
        return this.autoplaySupported;
    }
}

// ===== GLOBAL INSTANCE =====
window.VideoSystem = new VideoSystem();

// ===== AUTO INITIALIZATION =====
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('VideoSystem ready');
    });
} else {
    console.log('VideoSystem ready');
}

// ===== MODERN MODULE EXPORT =====
export default VideoSystem;
