/**
 * Scroll reveal + section rail for proposal page.
 */
(function () {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function revealAll() {
    document.querySelectorAll('[data-prop-reveal]').forEach(function (el) {
      el.classList.add('is-revealed');
    });
  }

  function initReveal() {
    const nodes = document.querySelectorAll('[data-prop-reveal]');
    if (!nodes.length) return;

    if (reduceMotion.matches || !('IntersectionObserver' in window)) {
      revealAll();
      return;
    }

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-revealed');
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -4% 0px' }
    );

    nodes.forEach(function (el) {
      observer.observe(el);
    });
  }

  function initRail() {
    const sections = document.querySelectorAll('[data-prop-section]');
    const label = document.querySelector('[data-prop-rail-label]');
    const fill = document.querySelector('[data-prop-rail-fill]');
    if (!sections.length || (!label && !fill)) return;
    if (!('IntersectionObserver' in window)) return;

    const ratios = new Map();

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          ratios.set(entry.target, entry.intersectionRatio);
        });

        let best = null;
        let bestRatio = 0;
        sections.forEach(function (section) {
          const ratio = ratios.get(section) || 0;
          if (ratio > bestRatio) {
            bestRatio = ratio;
            best = section;
          }
        });

        if (!best) return;
        const code = best.getAttribute('data-prop-section') || '01';
        if (label) label.textContent = code;

        if (fill) {
          const index = Array.prototype.indexOf.call(sections, best);
          const pct = ((index + 1) / sections.length) * 100;
          fill.style.setProperty('--rail-fill', pct.toFixed(1) + '%');
        }
      },
      { threshold: [0.15, 0.35, 0.55, 0.75] }
    );

    sections.forEach(function (section) {
      observer.observe(section);
    });
  }

  function initStickyHide() {
    const sticky = document.querySelector('.prop-sticky-cta');
    const finalCta = document.querySelector('.prop-section--cta');
    if (!sticky || !finalCta || !('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          sticky.classList.toggle('is-hidden', entry.isIntersecting);
        });
      },
      { threshold: 0.2 }
    );

    observer.observe(finalCta);
  }

  function init() {
    initReveal();
    initRail();
    initStickyHide();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
