/* SECT-03 stats counter — рахує до data-count-to при вході у в'юпорт, 1600ms. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function formatCount(el) {
    var target = parseFloat(el.getAttribute('data-count-to') || '0');
    var suffix = el.getAttribute('data-count-suffix') || '';
    if (!isFinite(target)) target = 0;
    return Math.round(target) + suffix;
  }

  function settle(el) {
    el.textContent = formatCount(el);
    el.setAttribute('data-count-done', '1');
  }

  function animateCount(el) {
    if (el.getAttribute('data-count-done') === '1') return;
    var target = parseFloat(el.getAttribute('data-count-to') || '0');
    var suffix = el.getAttribute('data-count-suffix') || '';
    if (reduced || !target) {
      settle(el);
      return;
    }
    el.setAttribute('data-count-done', '1');
    el.textContent = '0' + suffix;
    var duration = 1600;
    var start = null;

    function step(timestamp) {
      if (start === null) start = timestamp;
      var progress = Math.min((timestamp - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    }
    window.requestAnimationFrame(step);
  }

  function initCounters(root) {
    root = root || document;
    var items = root.querySelectorAll('[data-count-to]');
    if (!items.length) return;

    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.35, rootMargin: '0px 0px -8% 0px' });

    items.forEach(function (el) {
      if (el.getAttribute('data-count-done') === '1') return;
      if (reduced) {
        settle(el);
        return;
      }
      observer.observe(el);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initCounters(document);
  });
  document.body.addEventListener('htmx:afterSwap', function (event) {
    initCounters(event.target);
  });
})();
