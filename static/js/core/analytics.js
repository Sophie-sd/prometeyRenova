/**
 * ANALYTICS.JS — Deferred analytics initialization.
 * Loaded with `defer` to reduce TBT and improve LCP/FCP.
 *
 * Responsibilities:
 *  1. Activate async CSS links (loaded with media="print" trick)
 *  2. Initialize Facebook Pixel after DOM is ready
 */

// 1. Activate any CSS that was loaded non-blocking (media="print" swap)
//    This runs synchronously when the deferred script executes (DOM is parsed,
//    browser is about to fire DOMContentLoaded) → minimal or no visible FOUC.
document.querySelectorAll('link[data-async-css]').forEach((link) => {
    link.media = 'all';
});

// 2. Facebook Pixel — deferred init
const pixelId = document.documentElement.dataset.pixelId;
if (pixelId) {
    // Standard FB Pixel snippet (external source only — no inline eval)
    const fbScript = document.createElement('script');
    fbScript.async = true;
    fbScript.src = 'https://connect.facebook.net/en_US/fbevents.js';
    document.head.appendChild(fbScript);

    // fbq stub so calls queue up before fbevents.js is ready
    if (!window.fbq) {
        const fbq = function () {
            fbq.callMethod
                ? fbq.callMethod.apply(fbq, arguments)
                : fbq.queue.push(arguments);
        };
        fbq.push = fbq;
        fbq.loaded = true;
        fbq.version = '2.0';
        fbq.queue = [];
        window.fbq = fbq;
        window._fbq = fbq;
    }

    window.fbq('init', pixelId);
    window.fbq('track', 'PageView');
}
