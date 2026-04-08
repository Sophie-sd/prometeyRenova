/**
 * Легкий паралакс для фонових зображень (internet-shop).
 * translate3d — сумісність з iOS Safari; без background-attachment: fixed.
 * Вимикається при prefers-reduced-motion.
 */
(function () {
    'use strict';

    const sections = [];
    let ticking = false;
    let reducedMotion = false;

    function init() {
        reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reducedMotion) {
            return;
        }

        document.querySelectorAll('[data-parallax-section]').forEach((section) => {
            const bg = section.querySelector('.is-parallax-section__bg');
            if (!bg) {
                return;
            }
            sections.push({ section, bg });
        });

        if (sections.length === 0) {
            return;
        }

        const io = new IntersectionObserver(
            () => {
                requestTick();
            },
            { root: null, rootMargin: '120px 0px', threshold: 0 }
        );

        sections.forEach(({ section }) => io.observe(section));

        window.addEventListener(
            'scroll',
            () => {
                requestTick();
            },
            { passive: true }
        );

        window.addEventListener(
            'resize',
            () => {
                requestTick();
            },
            { passive: true }
        );

        requestTick();
    }

    function requestTick() {
        if (ticking) {
            return;
        }
        ticking = true;
        window.requestAnimationFrame(update);
    }

    function update() {
        ticking = false;
        const vh = window.innerHeight || document.documentElement.clientHeight;
        const isNarrow = window.innerWidth < 768;
        const rate = isNarrow ? 0.05 : 0.1;

        sections.forEach(({ section, bg }) => {
            const rect = section.getBoundingClientRect();
            const visible = rect.bottom > -vh && rect.top < vh * 2;
            if (!visible) {
                bg.style.transform = '';
                bg.style.webkitTransform = '';
                return;
            }
            const shift = Math.round((vh / 2 - rect.top) * rate);
            const clamped = Math.max(-80, Math.min(80, shift));
            const t = `translate3d(0, ${clamped}px, 0)`;
            bg.style.transform = t;
            bg.style.webkitTransform = t;
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
