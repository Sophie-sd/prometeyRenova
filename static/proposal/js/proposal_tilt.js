/**
 * 3D tilt for proposal sheets — fine pointer + desktop only.
 */
(function () {
  'use strict';

  const DEFAULT_MAX = 5;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  const wideScreen = window.matchMedia('(min-width: 48rem)');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function canTilt() {
    return finePointer.matches && wideScreen.matches && !reduceMotion.matches;
  }

  function bindTilt(el) {
    let frame = 0;
    const maxAttr = el.getAttribute('data-tilt-max');
    const max = maxAttr ? Number(maxAttr) : DEFAULT_MAX;

    function onMove(event) {
      if (!canTilt()) return;
      const rect = el.getBoundingClientRect();
      if (!rect.width || !rect.height) return;

      const px = (event.clientX - rect.left) / rect.width;
      const py = (event.clientY - rect.top) / rect.height;
      const rotateY = (px - 0.5) * 2 * max;
      const rotateX = (0.5 - py) * 2 * max;
      const shadow = (0.08 + Math.abs(px - 0.5) * 0.1 + Math.abs(py - 0.5) * 0.06).toFixed(3);

      if (frame) cancelAnimationFrame(frame);
      frame = requestAnimationFrame(function () {
        el.classList.add('is-tilting');
        el.style.setProperty('--tilt-x', rotateX.toFixed(2) + 'deg');
        el.style.setProperty('--tilt-y', rotateY.toFixed(2) + 'deg');
        el.style.setProperty('--glare-x', (px * 100).toFixed(1) + '%');
        el.style.setProperty('--glare-y', (py * 100).toFixed(1) + '%');
        el.style.setProperty('--tilt-shadow', shadow);
      });
    }

    function onLeave() {
      if (frame) cancelAnimationFrame(frame);
      el.classList.remove('is-tilting');
      el.style.setProperty('--tilt-x', '0deg');
      el.style.setProperty('--tilt-y', '0deg');
      el.style.setProperty('--glare-x', '50%');
      el.style.setProperty('--glare-y', '40%');
      el.style.setProperty('--tilt-shadow', '0.08');
    }

    el.addEventListener('pointermove', onMove);
    el.addEventListener('pointerleave', onLeave);
    el.addEventListener('pointercancel', onLeave);
  }

  function init() {
    if (!canTilt()) return;
    document.querySelectorAll('[data-prop-tilt]').forEach(bindTilt);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
