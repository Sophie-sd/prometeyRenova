/**
 * ANALYTICS.JS - Централізований tracking system
 * Замінює дублювання analytics коду
 * Версія: 2.0
 */

import CONFIG from './config.js';

/**
 * Analytics Manager
 */
class AnalyticsManager {
    constructor() {
        this.enabled = CONFIG.features.enableAnalytics;
        this.timeOnPage = 0;
        this.engagementTracked = false;
        this.scrollDepths = new Set();
        
        if (this.enabled) {
            this.init();
        }
    }

    /**
     * Ініціалізація
     */
    init() {
        this.trackPageView();
        this.trackTimeOnPage();
        this.setupClickTracking();
        this.setupScrollTracking();
        this.setupFormTracking();
    }

    /**
     * Відправка події
     */
    track(eventName, params = {}) {
        if (!this.enabled) return;

        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, params);
        }

        if (CONFIG.features.enableDebugLog) {
            console.log('[Analytics]', eventName, params);
        }
    }

    /**
     * Page View
     */
    trackPageView() {
        this.track('page_view', {
            page_title: document.title,
            page_location: window.location.href,
            page_path: window.location.pathname,
        });
    }

    /**
     * Час на сторінці
     */
    trackTimeOnPage() {
        setInterval(() => {
            this.timeOnPage += 1;

            // Engaged session після 30 секунд
            if (this.timeOnPage === CONFIG.analytics.engagementTime && !this.engagementTracked) {
                this.track('engaged_session', {
                    time_on_page: this.timeOnPage
                });
                this.engagementTracked = true;
            }
        }, 1000);
    }

    /**
     * Click Tracking
     */
    setupClickTracking() {
        document.addEventListener('click', (e) => {
            // Button clicks
            const button = e.target.closest('.btn, button[type="submit"]');
            if (button) {
                this.track('button_click', {
                    button_text: button.textContent.trim(),
                    button_class: button.className,
                    page_location: window.location.href,
                });
            }

            // Link clicks
            const link = e.target.closest('a');
            if (link && link.href) {
                const isExternal = link.hostname !== window.location.hostname;
                
                this.track('link_click', {
                    link_url: link.href,
                    link_text: link.textContent.trim(),
                    link_external: isExternal,
                    page_location: window.location.href,
                });
            }

            // Article clicks (blog, events)
            const articleLink = e.target.closest('.card__title, .article-link, .event-link');
            if (articleLink) {
                this.track('article_click', {
                    article_title: articleLink.textContent.trim(),
                    page_location: window.location.href,
                });
            }
        });
    }

    /**
     * Scroll Tracking
     */
    setupScrollTracking() {
        let ticking = false;

        const trackScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollPercentage = Math.round(
                        (window.pageYOffset / (document.documentElement.scrollHeight - window.innerHeight)) * 100
                    );

                    // Track scroll depths: 25%, 50%, 75%, 90%
                    [25, 50, 75, 90].forEach(depth => {
                        if (scrollPercentage >= depth && !this.scrollDepths.has(depth)) {
                            this.scrollDepths.add(depth);
                            this.track('scroll_depth', {
                                percent_scrolled: depth,
                                page_location: window.location.href,
                            });
                        }
                    });

                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', trackScroll, { passive: true });
    }

    /**
     * Form Tracking
     */
    setupFormTracking() {
        document.addEventListener('submit', (e) => {
            const form = e.target.closest('form[data-form-type]');
            if (form) {
                const formType = form.dataset.formType;
                
                this.track('form_submit', {
                    form_type: formType,
                    page_location: window.location.href,
                });
            }
        });
    }

    /**
     * Video Tracking
     */
    trackVideoPlay(videoSrc) {
        this.track('video_play', {
            video_src: videoSrc,
            page_location: window.location.href,
        });
    }

    trackVideoComplete(videoSrc) {
        this.track('video_complete', {
            video_src: videoSrc,
            page_location: window.location.href,
        });
    }

    /**
     * Event Registration
     */
    trackEventRegistration(eventId, eventTitle) {
        this.track('event_registration', {
            event_id: eventId,
            event_title: eventTitle,
            page_location: window.location.href,
        });
    }

    /**
     * Search
     */
    trackSearch(searchQuery, resultsCount) {
        this.track('search', {
            search_term: searchQuery,
            results_count: resultsCount,
            page_location: window.location.href,
        });
    }

    /**
     * Filter Usage
     */
    trackFilter(filterType, filterValue) {
        this.track('filter_used', {
            filter_type: filterType,
            filter_value: filterValue,
            page_location: window.location.href,
        });
    }

    /**
     * Custom Event
     */
    trackCustom(eventName, params) {
        this.track(eventName, params);
    }
}

// ===== GLOBAL INSTANCE (HYBRID) =====
const analytics = new AnalyticsManager();
window.Analytics = analytics;
window.trackEvent = trackEvent; // Для не-module скриптів

// ===== CONVENIENCE METHODS =====
export function trackEvent(eventName, params) {
    return analytics.track(eventName, params);
}

export function trackClick(element, customParams = {}) {
    return analytics.track('element_click', {
        element_text: element.textContent.trim(),
        element_class: element.className,
        ...customParams,
    });
}

// ===== EXPORT =====
export default analytics;

