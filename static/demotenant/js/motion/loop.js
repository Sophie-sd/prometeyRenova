/* SECT-08 marquee — два+ сети, track −50%, пауза поза в'юпортом (MERR-06). */
(function () {
  'use strict';

  var io = null;

  function cloneSet(first) {
    var copy = first.cloneNode(true);
    copy.setAttribute('aria-hidden', 'true');
    return copy;
  }

  function fillLoopTrack(el) {
    var track = el.querySelector('.loop__track');
    if (!track) return;
    var first = track.querySelector('.loop__set');
    if (!first) return;

    if (track.children.length === 1) {
      track.appendChild(cloneSet(first));
    }

    var guard = 0;
    while (
      el.clientWidth > 0 &&
      track.scrollWidth < el.clientWidth * 2 &&
      guard < 16
    ) {
      track.appendChild(cloneSet(first));
      guard += 1;
    }

    if (track.children.length % 2 === 1) {
      track.appendChild(cloneSet(first));
    }
  }

  function observeLoop(el) {
    if (!io) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          entry.target.classList.toggle('is-motion', entry.isIntersecting);
        });
      }, { threshold: 0.05 });
    }
    io.observe(el);
  }

  function initLoop(root) {
    root = root || document;
    var loops = root.querySelectorAll('[data-loop]');
    if (!loops.length) return;

    loops.forEach(function (el) {
      fillLoopTrack(el);
      if (el.dataset.loopReady === '1') return;
      el.dataset.loopReady = '1';
      observeLoop(el);
      if (typeof ResizeObserver === 'function') {
        var ro = new ResizeObserver(function () {
          fillLoopTrack(el);
        });
        ro.observe(el);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initLoop(document);
  });
  document.body.addEventListener('htmx:afterSwap', function (event) {
    initLoop(event.target);
  });
})();
