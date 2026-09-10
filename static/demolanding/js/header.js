/* Kontur+ header chrome: is-scrolled, drawer aria, in-page close */
(function () {
  'use strict';

  var header = document.querySelector('.dl-header');
  var burger = document.querySelector('[data-qa="menu-open"]');
  var drawer = document.querySelector('.drawer');

  if (header) {
    var ticking = false;

    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        header.classList.toggle('is-scrolled', window.scrollY > 8);
        ticking = false;
      });
    }

    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  function syncBurger() {
    if (!burger || !drawer) return;
    var open = drawer.classList.contains('is-open');
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    var label = burger.getAttribute(open ? 'data-label-close' : 'data-label-open');
    if (label) burger.setAttribute('aria-label', label);
  }

  if (drawer && window.MutationObserver) {
    new MutationObserver(syncBurger).observe(drawer, {
      attributes: true,
      attributeFilter: ['class'],
    });
    syncBurger();
  }

  document.querySelectorAll('.drawer a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function () {
      if (!drawer) return;
      drawer.classList.remove('is-open');
      document.body.classList.remove('has-drawer-open');
    });
  });
})();
