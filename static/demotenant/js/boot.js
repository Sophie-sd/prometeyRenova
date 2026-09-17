/* Порядок ініціалізації motion-модулів. reveal.js вантажиться першим —
   решта не залежить від нього, лише спільна конвенція htmx:afterSwap. */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    if (window.demotenant && window.demotenant.initObjectTilt) {
      window.demotenant.initObjectTilt('[data-tilt]');
    }
  });
})();
