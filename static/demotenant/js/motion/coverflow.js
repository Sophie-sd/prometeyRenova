/* coverflow_carousel_skill: scroll-snap + is-active/is-near за відстанню від центру. */
(function () {
  'use strict';

  function updateActive(cf) {
    var track = cf.querySelector('[data-cf-track]') || cf;
    var cards = track.querySelectorAll('.cf__card');
    var center = cf.scrollLeft + cf.clientWidth / 2;
    var closest = null;
    var closestDist = Infinity;

    cards.forEach(function (card) {
      var cardCenter = card.offsetLeft + card.offsetWidth / 2;
      var dist = Math.abs(cardCenter - center);
      card.classList.remove('is-active', 'is-near');
      if (dist < closestDist) {
        closestDist = dist;
        closest = card;
      } else if (dist < card.offsetWidth * 1.5) {
        card.classList.add('is-near');
      }
    });
    if (closest) closest.classList.add('is-active');
  }

  function initCoverflow(root) {
    root = root || document;
    var items = root.querySelectorAll('[data-cf]');
    items.forEach(function (cf) {
      updateActive(cf);
      var ticking = false;
      cf.addEventListener('scroll', function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () {
          updateActive(cf);
          ticking = false;
        });
      });
      var prev = cf.parentElement && cf.parentElement.querySelector('[data-cf-prev]');
      var next = cf.parentElement && cf.parentElement.querySelector('[data-cf-next]');
      if (prev) prev.addEventListener('click', function () { cf.scrollBy({ left: -320, behavior: 'smooth' }); });
      if (next) next.addEventListener('click', function () { cf.scrollBy({ left: 320, behavior: 'smooth' }); });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initCoverflow(document);
  });
  document.body.addEventListener('htmx:afterSwap', function (event) {
    initCoverflow(event.target);
  });
})();
