/* Scroll reveal: IO one-shot, --i stagger, data-reveal-hold пізніше (MERR-11/13). */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function markVisible(el) {
    el.classList.add('is-visible');
  }

  function initReveal(root) {
    root = root || document;
    var items = root.querySelectorAll('[data-reveal]');
    items.forEach(function (el, idx) {
      if (!el.style.getPropertyValue('--i')) {
        el.style.setProperty('--i', String(idx % 6));
      }
    });

    if (reduced) {
      items.forEach(markVisible);
      root.querySelectorAll('[data-reveal-hold]').forEach(markVisible);
      return;
    }

    var observer = new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            markVisible(entry.target);
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 },
    );
    items.forEach(function (el) {
      observer.observe(el);
    });

    var holdObserver = new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            markVisible(entry.target);
            obs.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '0px 0px -22% 0px' },
    );
    root.querySelectorAll('[data-reveal-hold]').forEach(function (el) {
      holdObserver.observe(el);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initReveal(document);
  });
  document.body.addEventListener('htmx:afterSwap', function (event) {
    initReveal(event.target);
  });

  window.demotenant = window.demotenant || {};
  window.demotenant.initReveal = initReveal;
})();
