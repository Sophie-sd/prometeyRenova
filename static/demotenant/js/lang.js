/* Shared demo language switcher. Bind all [data-dt-lang] instances (header + drawer). */
(function () {
  'use strict';

  function unprefixedPath() {
    var path = window.location.pathname.replace(/^\/(en|ru|cs)(?=\/|$)/, '') || '/';
    if (path.charAt(0) !== '/') {
      path = '/' + path;
    }
    return path + window.location.search;
  }

  function bind(root) {
    var form = root.querySelector('form');
    var select = root.querySelector('[data-dt-lang-select]');
    var next = root.querySelector('[data-dt-lang-next]');
    var submitting = false;
    if (!form || !select || !next) {
      return;
    }
    function onChange() {
      if (submitting) {
        return;
      }
      submitting = true;
      next.value = unprefixedPath();
      form.submit();
    }
    select.addEventListener('change', onChange);
    select.addEventListener('input', onChange);
  }

  function init() {
    document.querySelectorAll('[data-dt-lang]').forEach(bind);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
