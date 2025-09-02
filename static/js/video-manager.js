/* =================================
   PARALLAX VIDEO MANAGER
   Advanced background video system
   ================================= */

'use strict';

class VideoManager {
    constructor() {
        this.videos = new Map();
        this.currentVideo = null;
        this.container = null;
        this.isVisible = false;
        this.isMobile = window.innerWidth <= 768;
        
        this.config = {
            fadeSpeed: 600,
            intersectionThreshold: 0.1,
            preloadTimeout: 10000
        };
        
        this.init();
    }
    
    init() {
        this.createContainer();
        this.setupIntersectionObserver();
        this.bindEvents();
        this.loadCurrentPageVideo();
        
        console.log('🎬 VideoManager initialized');
    }
    
    createContainer() {
        // Remove existing
        const existing = document.querySelector('.parallax-video-container');
        if (existing) existing.remove();
        
        // Create container
        this.container = document.createElement('div');
        this.container.className = 'parallax-video-container';
        
        // Add overlay
        const overlay = document.createElement('div');
        overlay.className = 'parallax-video-overlay';
        this.container.appendChild(overlay);
        
        // Insert at body start
        document.body.insertBefore(this.container, document.body.firstChild);
    }
    
    setupIntersectionObserver() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.target.classList.contains('main-content')) {
                    this.isVisible = entry.isIntersecting;
                    this.updateVideoVisibility();
                }
            });
        }, { threshold: this.config.intersectionThreshold });
        
        const mainContent = document.querySelector('.main-content');
        if (mainContent) this.observer.observe(mainContent);
    }
    
    bindEvents() {
        // Resize handler
        window.addEventListener('resize', this.throttle(() => {
            const wasMobile = this.isMobile;
            this.isMobile = window.innerWidth <= 768;
            
            if (wasMobile !== this.isMobile) {
                this.loadCurrentPageVideo();
            }
        }, 250));
        
        // Visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseCurrentVideo();
            } else {
                this.playCurrentVideo();
            }
        });
        
        // Reduced motion
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        mediaQuery.addEventListener('change', () => {
            if (mediaQuery.matches) {
                this.hideVideo();
            } else {
                this.showVideo();
            }
        });
    }
    
    getCurrentPage() {
        const path = window.location.pathname;
        
        if (path === '/' || path === '/home/') return 'main';
        if (path.includes('/portfolio/')) return 'portfolio';
        if (path.includes('/blog/')) return 'blog';
        if (path.includes('/events/')) return 'events';
        if (path.includes('/developer/')) return 'study';
        
        return 'main'; // fallback
    }
    
    loadCurrentPageVideo() {
        const page = this.getCurrentPage();
        this.loadVideo(page);
    }
    
    async loadVideo(pageName) {
        try {
            const deviceType = this.isMobile ? 'mobile' : 'desktop';
            const videoName = this.isMobile ? `${pageName}mobile.mp4` : `${pageName}.mp4`;
            const videoPath = `/static/videos/${deviceType}/${videoName}`;
            
            if (this.videos.has(videoPath)) {
                this.switchToVideo(videoPath);
                return;
            }
            
            const video = this.createVideoElement(videoPath);
            await this.preloadVideo(video);
            
            this.videos.set(videoPath, video);
            this.switchToVideo(videoPath);
            
            console.log(`✅ Video loaded: ${videoName}`);
            
        } catch (error) {
            console.warn('❌ Video load failed:', error);
            this.hideVideo();
        }
    }
    
    createVideoElement(videoPath) {
        const video = document.createElement('video');
        video.className = 'parallax-video';
        video.src = videoPath;
        video.muted = true;
        video.loop = true;
        video.playsInline = true;
        video.preload = 'metadata';
        video.setAttribute('playsinline', 'true');
        video.setAttribute('webkit-playsinline', 'true');
        
        return video;
    }
    
    preloadVideo(video) {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Video load timeout'));
            }, this.config.preloadTimeout);
            
            video.addEventListener('loadeddata', () => {
                clearTimeout(timeout);
                resolve();
            }, { once: true });
            
            video.addEventListener('error', () => {
                clearTimeout(timeout);
                reject(new Error('Video load error'));
            }, { once: true });
            
            video.load();
        });
    }
    
    switchToVideo(videoPath) {
        const newVideo = this.videos.get(videoPath);
        if (!newVideo) return;
        
        // Fade out current
        if (this.currentVideo) {
            this.fadeOutVideo(this.currentVideo);
        }
        
        // Add new video
        if (!this.container.contains(newVideo)) {
            this.container.appendChild(newVideo);
        }
        
        // Fade in new
        this.fadeInVideo(newVideo);
        this.currentVideo = newVideo;
        
        // Cleanup
        this.cleanupOldVideos(videoPath);
    }
    
    fadeInVideo(video) {
        video.classList.remove('fade-out');
        video.classList.add('active');
        this.playVideo(video);
    }
    
    fadeOutVideo(video) {
        video.classList.add('fade-out');
        video.classList.remove('active');
        
        setTimeout(() => {
            if (video.classList.contains('fade-out')) {
                this.pauseVideo(video);
            }
        }, this.config.fadeSpeed);
    }
    
    async playVideo(video) {
        try {
            if (this.isVisible && !document.hidden) {
                await video.play();
            }
        } catch (error) {
            console.warn('Video play failed:', error);
        }
    }
    
    pauseVideo(video) {
        try {
            video.pause();
        } catch (error) {
            console.warn('Video pause failed:', error);
        }
    }
    
    playCurrentVideo() {
        if (this.currentVideo) {
            this.playVideo(this.currentVideo);
        }
    }
    
    pauseCurrentVideo() {
        if (this.currentVideo) {
            this.pauseVideo(this.currentVideo);
        }
    }
    
    updateVideoVisibility() {
        if (this.isVisible) {
            this.showVideo();
        } else {
            this.hideVideo();
        }
    }
    
    showVideo() {
        if (this.container) {
            this.container.style.display = 'block';
            this.playCurrentVideo();
        }
    }
    
    hideVideo() {
        if (this.container) {
            this.container.style.display = 'none';
            this.pauseCurrentVideo();
        }
    }
    
    cleanupOldVideos(currentVideoPath) {
        this.videos.forEach((video, path) => {
            if (path !== currentVideoPath && this.container.contains(video)) {
                setTimeout(() => {
                    if (this.container.contains(video)) {
                        this.container.removeChild(video);
                    }
                }, this.config.fadeSpeed + 100);
            }
        });
    }
    
    // Utility methods
    throttle(func, delay) {
        let timeoutId;
        let lastExecTime = 0;
        
        return function (...args) {
            const currentTime = Date.now();
            
            if (currentTime - lastExecTime > delay) {
                func.apply(this, args);
                lastExecTime = currentTime;
            } else {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    func.apply(this, args);
                    lastExecTime = Date.now();
                }, delay - (currentTime - lastExecTime));
            }
        };
    }
    
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        
        if (this.container) {
            this.container.remove();
        }
        
        this.videos.clear();
        this.currentVideo = null;
        
        console.log('🎬 VideoManager destroyed');
    }
}

// Initialize video manager
document.addEventListener('DOMContentLoaded', function() {
    window.videoManager = new VideoManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.videoManager) {
        window.videoManager.destroy();
    }
});

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VideoManager;
}
