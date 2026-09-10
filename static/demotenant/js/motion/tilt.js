/* object_tilt_glare_skill: rect cache + rAF, will-change лише під .is-tilt (MERR-14). */
(function () {
  'use strict';

  var MAX_DEG = 14;

  function initObjectTilt(selector, root) {
    root = root || document;
    var nodes = root.querySelectorAll(selector || '[data-tilt]');
    nodes.forEach(function (el) {
      var rect = null;
      var raf = null;

      el.addEventListener('pointerenter', function () {
        rect = el.getBoundingClientRect();
        el.classList.add('is-tilt');
      });

      el.addEventListener('pointermove', function (event) {
        if (!rect) return;
        if (raf) window.cancelAnimationFrame(raf);
        raf = window.requestAnimationFrame(function () {
          var px = (event.clientX - rect.left) / rect.width;
          var py = (event.clientY - rect.top) / rect.height;
          el.style.setProperty('--tilt-y', (px - 0.5) * MAX_DEG + 'deg');
          el.style.setProperty('--tilt-x', (0.5 - py) * MAX_DEG + 'deg');
          el.style.setProperty('--tilt-glare-x', px * 100 + '%');
          el.style.setProperty('--tilt-glare-y', py * 100 + '%');
        });
      });

      el.addEventListener('pointerleave', function () {
        el.classList.remove('is-tilt');
        el.style.setProperty('--tilt-x', '0deg');
        el.style.setProperty('--tilt-y', '0deg');
        rect = null;
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initObjectTilt('[data-tilt]');
  });

  window.demotenant = window.demotenant || {};
  window.demotenant.initObjectTilt = initObjectTilt;
})();
