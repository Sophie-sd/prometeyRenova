/* Demo corporate site (Figma 2026-10): sticky header shadow + scroll carousels. */
(function () {
  'use strict';

  function initHeader() {
    var header = document.querySelector('.dc-header');
    if (!header) return;
    var update = function () { header.classList.toggle('is-scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  function step(track) {
    var item = track.firstElementChild;
    if (!item) return track.clientWidth;
    var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    return item.getBoundingClientRect().width + gap;
  }

  function initCarousels() {
    document.querySelectorAll('[data-carousel]').forEach(function (track) {
      var navs = document.querySelectorAll('[data-carousel-nav="' + track.id + '"]');
      var sync = function () {
        var max = track.scrollWidth - track.clientWidth - 2;
        navs.forEach(function (nav) {
          nav.hidden = max <= 0;
          var prev = nav.querySelector('[data-carousel-prev]');
          var next = nav.querySelector('[data-carousel-next]');
          if (prev) prev.disabled = track.scrollLeft <= 2;
          if (next) next.disabled = track.scrollLeft >= max;
        });
      };
      navs.forEach(function (nav) {
        nav.addEventListener('click', function (event) {
          var btn = event.target.closest('button');
          if (!btn) return;
          var dir = btn.hasAttribute('data-carousel-prev') ? -1 : 1;
          track.scrollBy({ left: dir * step(track), behavior: 'smooth' });
        });
      });
      track.addEventListener('scroll', sync, { passive: true });
      window.addEventListener('resize', sync);
      sync();
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initHeader();
    initCarousels();
  });
})();
