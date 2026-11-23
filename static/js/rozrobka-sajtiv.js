/* Soft /rozrobka-sajtiv/: portfolio carousel + demo CMS tabs.
   Currency is HTMX + pl_currency. Screen scroll-on-hover lives in js/portfolio-screen-scroll.js. */
(function () {
    'use strict';

    var root = document.getElementById('plRsRoot');
    if (!root) return;

    function initCarousel() {
        var section = root.querySelector('[data-pl-rs-portfolio]');
        if (!section) return;
        var track = section.querySelector('[data-pl-rs-track]');
        var prev = section.querySelector('[data-pl-rs-prev]');
        var next = section.querySelector('[data-pl-rs-next]');
        if (!track || !prev || !next) return;

        function cardStep() {
            var card = track.querySelector('.pl-rs__work-card');
            if (!card) return 378;
            var styles = window.getComputedStyle(track);
            var gap = parseFloat(styles.columnGap || styles.gap || '20') || 20;
            return card.getBoundingClientRect().width + gap;
        }

        function scrollByDir(dir) {
            track.scrollBy({ left: dir * cardStep(), behavior: 'smooth' });
        }

        prev.addEventListener('click', function () { scrollByDir(-1); });
        next.addEventListener('click', function () { scrollByDir(1); });
    }

    /* Demo CMS window: WAI-ARIA tabs (roving tabindex, arrows/Home/End).
       No JS → first pane visible via [hidden] on the rest. */
    function initCms(screen) {
        var tabs = Array.prototype.slice.call(screen.querySelectorAll('[data-pl-rs-cms-tab]'));
        var panes = Array.prototype.slice.call(screen.querySelectorAll('[data-pl-rs-cms-pane]'));
        var ind = screen.querySelector('[data-pl-rs-cms-ind]');
        if (!tabs.length || tabs.length !== panes.length) return;

        var current = 0;
        tabs.forEach(function (tab, i) {
            if (tab.getAttribute('aria-selected') === 'true') current = i;
        });

        function placeIndicator() {
            if (!ind) return;
            var tab = tabs[current];
            ind.style.height = tab.offsetHeight + 'px';
            ind.style.transform = 'translate3d(0,' + tab.offsetTop + 'px,0)';
        }

        function select(index, focus) {
            if (index < 0) index = tabs.length - 1;
            if (index >= tabs.length) index = 0;
            current = index;
            tabs.forEach(function (tab, i) {
                var on = i === index;
                tab.classList.toggle('is-on', on);
                tab.setAttribute('aria-selected', on ? 'true' : 'false');
                tab.tabIndex = on ? 0 : -1;
                panes[i].classList.toggle('is-on', on);
                panes[i].setAttribute('aria-hidden', on ? 'false' : 'true');
            });
            if (focus) tabs[index].focus();
            placeIndicator();
        }

        // Enhance: keep all panes in layout (height lock), visibility handled by CSS.
        panes.forEach(function (pane) { pane.hidden = false; });
        screen.classList.add('is-js');

        tabs.forEach(function (tab, i) {
            tab.addEventListener('click', function () { select(i, false); });
            tab.addEventListener('keydown', function (e) {
                var key = e.key;
                if (key === 'ArrowDown' || key === 'ArrowRight') {
                    e.preventDefault();
                    select(current + 1, true);
                } else if (key === 'ArrowUp' || key === 'ArrowLeft') {
                    e.preventDefault();
                    select(current - 1, true);
                } else if (key === 'Home') {
                    e.preventDefault();
                    select(0, true);
                } else if (key === 'End') {
                    e.preventDefault();
                    select(tabs.length - 1, true);
                }
            });
        });

        // First placement without animation (no slide-in on load).
        if (ind) ind.style.transition = 'none';
        select(current, false);
        if (ind) {
            void ind.offsetHeight;
            ind.style.transition = '';
        }

        // Re-measure on resize / late webfont swap (tab height changes with font metrics).
        var t = 0;
        window.addEventListener('resize', function () {
            window.clearTimeout(t);
            t = window.setTimeout(placeIndicator, 150);
        }, { passive: true });
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(placeIndicator);
        }
    }

    /* Reviews: full text is in the HTML. JS opts into the clamp and shows
       the toggle only when the clamped box actually overflows. */
    function initReviews() {
        var buttons = root.querySelectorAll('[data-pl-rs-review-more]');
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
    }

    initCarousel();
    Array.prototype.forEach.call(root.querySelectorAll('[data-pl-rs-cms]'), initCms);
    initReviews();
})();
