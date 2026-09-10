/* Мобільне drawer-меню: Escape/backdrop/scroll-lock (cooperative_design §9). */
(function () {
  'use strict';

  function initDrawer(root) {
    root = root || document;
    var drawer = root.querySelector('.drawer');
    if (!drawer) return;
    var openers = root.querySelectorAll('[data-qa="menu-open"]');
    var backdrop = drawer.querySelector('.drawer__backdrop');

    function setExpanded(open) {
      openers.forEach(function (btn) {
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    }

    function open() {
      drawer.classList.add('is-open');
      document.body.classList.add('has-drawer-open');
      setExpanded(true);
    }

    function close() {
      drawer.classList.remove('is-open');
      document.body.classList.remove('has-drawer-open');
      setExpanded(false);
    }

    openers.forEach(function (btn) {
      if (!btn.getAttribute('aria-expanded')) {
        btn.setAttribute('aria-expanded', 'false');
      }
      btn.addEventListener('click', function () {
        drawer.classList.contains('is-open') ? close() : open();
      });
    });
    document.addEventListener('click', function (event) {
      if (event.target.closest('[data-qa="menu-close"]')) close();
    });
    if (backdrop) backdrop.addEventListener('click', close);
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') close();
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initDrawer(document);
  });
})();
