(function () {
    'use strict';

    var root = document.getElementById('plCorpRoot');
    if (!root) return;

    var demoRoot = root.querySelector('[data-demo-root]');
    if (!demoRoot) return;

    var buttons = demoRoot.querySelectorAll('button[data-c]');
    if (!buttons.length) return;

    buttons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var color = btn.getAttribute('data-c');
            if (!color) return;

            buttons.forEach(function (b) {
                b.classList.remove('is-active');
            });
            btn.classList.add('is-active');
            demoRoot.style.setProperty('--pl-corp-demo', color);
        });
    });
})();
