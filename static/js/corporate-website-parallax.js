/**
 * Single fixed-layer parallax for corporate-website page.
 * Moves .cw-page-bg via translate3d on desktop only.
 * Touch/mobile: static fixed bg (no JS transform — avoids iOS jank).
 * Disabled when prefers-reduced-motion is set.
 */
(function () {
    'use strict';

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isTouchDevice = window.matchMedia('(pointer: coarse)').matches;

    if (reducedMotion || isTouchDevice) return;

    const bg = document.querySelector('.cw-page-bg');
    if (!bg) return;

    let ticking = false;
    const RATE = 0.08;
    const CLAMP = 120;

    function update() {
        ticking = false;
        const shift = Math.round(window.scrollY * RATE);
        const clamped = Math.max(-CLAMP, Math.min(CLAMP, shift));
        const t = `translate3d(0, ${clamped}px, 0)`;
        bg.style.transform = t;
        bg.style.webkitTransform = t;
    }

    function requestTick() {
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(update);
        }
    }

    window.addEventListener('scroll', requestTick, { passive: true });
    window.addEventListener('resize', requestTick, { passive: true });
    requestTick();
})();
