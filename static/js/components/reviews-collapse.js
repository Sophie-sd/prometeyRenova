/* Review text clamp for any container. Full text stays in the HTML.
   JS opts into the clamp and shows the toggle only when the box overflows. */
(function () {
    'use strict';

    var buttons = document.querySelectorAll('[data-pl-rs-review-more]');
    if (!buttons.length) return;

    function overflows(text) {
        if (text.scrollHeight > text.clientHeight) return true;
        /* Safari reports the clamped scrollHeight. Compare the unclamped
           scrollHeight with the clamped clientHeight in the same turn. */
        text.classList.remove('is-collapsed');
        var full = text.scrollHeight;
        text.classList.add('is-collapsed');
        return full > text.clientHeight;
    }

    function sync(text, btn) {
        if (text.classList.contains('is-expanded')) {
            btn.hidden = false;
            return;
        }
        text.classList.add('is-collapsed');
        btn.hidden = !overflows(text);
    }

    Array.prototype.forEach.call(buttons, function (btn) {
        var textId = btn.getAttribute('aria-controls');
        var text = textId ? document.getElementById(textId) : null;
        if (!text) return;

        text.classList.add('is-collapsed');
        text.classList.remove('is-expanded');
        btn.setAttribute('aria-expanded', 'false');

        btn.addEventListener('click', function () {
            var expand = text.classList.contains('is-collapsed');
            text.classList.toggle('is-collapsed', !expand);
            text.classList.toggle('is-expanded', expand);
            btn.setAttribute('aria-expanded', expand ? 'true' : 'false');
            if (!expand) sync(text, btn);
        });

        sync(text, btn);
    });

    var timer = 0;
    window.addEventListener('resize', function () {
        window.clearTimeout(timer);
        timer = window.setTimeout(function () {
            Array.prototype.forEach.call(buttons, function (btn) {
                var text = document.getElementById(btn.getAttribute('aria-controls'));
                if (!text) return;
                sync(text, btn);
            });
        }, 150);
    }, { passive: true });
})();
