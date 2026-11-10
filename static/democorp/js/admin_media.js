(function () {
    'use strict';

    function bind(root) {
        root.querySelectorAll('.dc-photo__file').forEach(function (input) {
            input.addEventListener('change', function () {
                var holder = input.closest('.dc-photo');
                var out = holder ? holder.querySelector('[data-dc-photo-chosen]') : null;
                var file = input.files && input.files[0];
                if (out) {
                    out.textContent = file ? file.name : '';
                }
            });
        });

        root.querySelectorAll('.dc-color__input').forEach(function (input) {
            var sync = function () {
                var holder = input.closest('.dc-color');
                var out = holder ? holder.querySelector('[data-dc-color-hex]') : null;
                if (out) {
                    out.textContent = input.value;
                }
            };
            input.addEventListener('input', sync);
            input.addEventListener('change', sync);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            bind(document);
        });
    } else {
        bind(document);
    }
})();
