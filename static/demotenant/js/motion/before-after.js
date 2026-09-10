/* GAL-05 before/after — pointer capture, --ba 2…98, touch-action none */
(function () {
  'use strict';

  var MIN = 2;
  var MAX = 98;

  function clamp(n) {
    return Math.min(MAX, Math.max(MIN, n));
  }

  function initBaCompare(root) {
    if (!root || root.getAttribute('data-ba-ready') === '1') {
      return function () {};
    }
    root.setAttribute('data-ba-ready', '1');

    var dragging = false;

    function readBa() {
      var v = parseFloat(getComputedStyle(root).getPropertyValue('--ba'));
      return isFinite(v) ? v : 52;
    }

    function setBa(pct) {
      var v = clamp(pct);
      root.style.setProperty('--ba', v.toFixed(2) + '%');
      root.setAttribute('aria-valuenow', String(Math.round(v)));
    }

    function pctFromEvent(event) {
      var rect = root.getBoundingClientRect();
      if (rect.width <= 0) return readBa();
      return ((event.clientX - rect.left) / rect.width) * 100;
    }

    function onDown(event) {
      if (event.pointerType === 'mouse' && event.button !== 0) return;
      dragging = true;
      root.classList.add('is-dragging');
      try {
        root.setPointerCapture(event.pointerId);
      } catch (err) { /* ignore */ }
      setBa(pctFromEvent(event));
    }

    function onMove(event) {
      if (!dragging) return;
      setBa(pctFromEvent(event));
    }

    function onUp(event) {
      if (!dragging) return;
      dragging = false;
      root.classList.remove('is-dragging');
      if (event && event.pointerId != null) {
        try {
          if (root.hasPointerCapture && root.hasPointerCapture(event.pointerId)) {
            root.releasePointerCapture(event.pointerId);
          }
        } catch (err) { /* ignore */ }
      }
    }

    function onKey(event) {
      var step = event.shiftKey ? 10 : 2;
      var cur = readBa();
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        setBa(cur - step);
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        setBa(cur + step);
      } else if (event.key === 'Home') {
        event.preventDefault();
        setBa(MIN);
      } else if (event.key === 'End') {
        event.preventDefault();
        setBa(MAX);
      }
    }

    function onDragStart(event) {
      event.preventDefault();
    }

    root.addEventListener('pointerdown', onDown);
    root.addEventListener('pointermove', onMove);
    root.addEventListener('pointerup', onUp);
    root.addEventListener('pointercancel', onUp);
    root.addEventListener('lostpointercapture', onUp);
    root.addEventListener('keydown', onKey);
    root.addEventListener('dragstart', onDragStart);

    return function destroy() {
      onUp();
      root.removeEventListener('pointerdown', onDown);
      root.removeEventListener('pointermove', onMove);
      root.removeEventListener('pointerup', onUp);
      root.removeEventListener('pointercancel', onUp);
      root.removeEventListener('lostpointercapture', onUp);
      root.removeEventListener('keydown', onKey);
      root.removeEventListener('dragstart', onDragStart);
      root.removeAttribute('data-ba-ready');
    };
  }

  function initAll(scope) {
    scope = scope || document;
    var nodes = scope.querySelectorAll('[data-ba-compare]');
    for (var i = 0; i < nodes.length; i += 1) {
      initBaCompare(nodes[i]);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initAll(document);
  });
  document.body.addEventListener('htmx:afterSwap', function (event) {
    initAll(event.target);
  });
})();
