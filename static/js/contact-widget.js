/**
 * contact-widget.js
 * Floating contact widget: toggle open/close, close on outside click / ESC.
 */
(function () {
    'use strict';

    function init() {
        const widget = document.getElementById('contact-widget');
        const toggle = document.getElementById('contact-widget-toggle');
        const panel  = document.getElementById('contact-widget-panel');

        if (!widget || !toggle || !panel) return;

        function open() {
            widget.classList.add('contact-widget--open');
            toggle.setAttribute('aria-expanded', 'true');
            toggle.setAttribute('aria-label', toggle.getAttribute('data-label-close') ?? 'Закрити контакти');
            panel.setAttribute('aria-hidden', 'false');
        }

        function close() {
            widget.classList.remove('contact-widget--open');
            toggle.setAttribute('aria-expanded', 'false');
            toggle.setAttribute('aria-label', toggle.getAttribute('data-label-open') ?? 'Відкрити контакти');
            panel.setAttribute('aria-hidden', 'true');
        }

        function isOpen() {
            return widget.classList.contains('contact-widget--open');
        }

        toggle.addEventListener('click', () => {
            isOpen() ? close() : open();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isOpen()) close();
        });

        document.addEventListener('click', (e) => {
            if (isOpen() && !widget.contains(e.target)) close();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
