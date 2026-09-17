/* NAV-04 capsule morph: [data-morph-sentinel] IO з гістерезисом 0/48px. */
(function () {
  'use strict';

  function initMorphNav(root) {
    root = root || document;
    var morphs = root.querySelectorAll('.morph');
    morphs.forEach(function (morph) {
      var sentinel = morph.querySelector('[data-morph-sentinel]') || document.querySelector('[data-morph-sentinel]');
      if (!sentinel) return;

      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          morph.classList.toggle('is-collapsed', !entry.isIntersecting);
        });
      }, { rootMargin: '-48px 0px 0px 0px' });
      observer.observe(sentinel);

      morph.addEventListener('mouseenter', function () {
        if (morph.classList.contains('is-collapsed')) morph.classList.add('is-expanded');
      });
      morph.addEventListener('mouseleave', function () {
        morph.classList.remove('is-expanded');
      });
      morph.addEventListener('click', function () {
        morph.classList.toggle('is-expanded');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initMorphNav(document);
  });
})();
