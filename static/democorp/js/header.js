/* Sticky header: is-scrolled (тінь). Не ховаємо при скролі — luxury sticky. */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var header = document.querySelector('.dc-header');
    if (!header) return;

    window.addEventListener('scroll', function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    }, { passive: true });
  });
})();
