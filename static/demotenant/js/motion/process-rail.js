/* SECT-10: is-rail-on після .process-rail__item.is-visible; stamp каскадом. */
(function () {
  'use strict';

  function initOneRail(wrap) {
    if (wrap.getAttribute('data-rail-ready') === '1') return;
    var fill = wrap.querySelector('.process-rail__fill');
    var items = Array.prototype.slice.call(wrap.querySelectorAll('.process-rail__item'));
    if (!fill || !items.length) return;
    wrap.setAttribute('data-rail-ready', '1');

    var bar = fill.closest('.process-rail__bar');
    if (bar) {
      bar.classList.remove('reveal', 'is-visible');
      bar.removeAttribute('data-reveal');
    }

    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
      wrap.classList.add('is-rail-on');
      items.forEach(function (item) {
        item.classList.add('is-visible', 'is-stamped');
      });
      return;
    }

    function armRail() {
      if (wrap.classList.contains('is-rail-on')) return;
      var anyVisible = items.some(function (item) {
        return item.classList.contains('is-visible');
      });
      if (!anyVisible) return;
      wrap.classList.add('is-rail-on');
    }

    function queueStamp(item, index) {
      if (item.getAttribute('data-stamp-queued') === '1') return;
      if (!item.classList.contains('is-visible')) return;
      item.setAttribute('data-stamp-queued', '1');
      window.setTimeout(function () {
        item.classList.add('is-stamped');
      }, 90 + index * 120);
    }

    function maybeDisconnect() {
      var allQueued = items.every(function (item) {
        return item.getAttribute('data-stamp-queued') === '1';
      });
      if (allQueued && wrap.classList.contains('is-rail-on')) {
        classObserver.disconnect();
      }
    }

    function onClassChange() {
      armRail();
      items.forEach(function (item, i) {
        queueStamp(item, i);
      });
      maybeDisconnect();
    }

    var classObserver = new MutationObserver(onClassChange);
    items.forEach(function (item, i) {
      classObserver.observe(item, { attributes: true, attributeFilter: ['class'] });
      queueStamp(item, i);
    });
    armRail();
    maybeDisconnect();
  }

  function initProcessRail(root) {
    root = root || document;
    var rails = root.querySelectorAll ? root.querySelectorAll('.process-rail') : [];
    if (!rails.length && root.classList && root.classList.contains('process-rail')) {
      initOneRail(root);
      return;
    }
    rails.forEach(initOneRail);
  }

  document.addEventListener('DOMContentLoaded', function () {
    initProcessRail(document);
  });
  document.body.addEventListener('htmx:afterSwap', function (event) {
    initProcessRail(event.target);
  });
})();
