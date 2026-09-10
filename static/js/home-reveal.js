(function () {
    'use strict';

    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function markVisible(el) {
        el.classList.add('is-visible');
    }

    function isAlreadyPast(el) {
        return el.getBoundingClientRect().bottom < 0;
    }

    function revealWhyGrid(grid) {
        if (!grid) {
            return;
        }

        grid.querySelectorAll('.v2-why-shell.home-reveal').forEach(markVisible);
    }

    function initWhyGridReveal() {
        var grid = document.querySelector('#home-redesign-why .v2-why-grid');
        if (!grid) {
            return;
        }

        if (reduced || !('IntersectionObserver' in window) || isAlreadyPast(grid)) {
            revealWhyGrid(grid);
            return;
        }

        var whyObserver = new IntersectionObserver(function (entries, obs) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    revealWhyGrid(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -12% 0px'
        });

        whyObserver.observe(grid);
    }

    function initHomeReveal() {
        var items = document.querySelectorAll('.home-reveal:not([data-reveal-hold]):not(.v2-why-shell)');
        var holdItems = document.querySelectorAll('.home-reveal[data-reveal-hold]');

        if (reduced || !('IntersectionObserver' in window)) {
            items.forEach(markVisible);
            holdItems.forEach(markVisible);
            initWhyGridReveal();
            return;
        }

        initWhyGridReveal();

        var observer = new IntersectionObserver(function (entries, obs) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    markVisible(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0,
            rootMargin: '100% 0px -4% 0px'
        });

        items.forEach(function (el) {
            if (isAlreadyPast(el)) {
                markVisible(el);
                return;
            }
            observer.observe(el);
        });

        var holdObserver = new IntersectionObserver(function (entries, obs) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    markVisible(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0,
            rootMargin: '100% 0px -14% 0px'
        });

        holdItems.forEach(function (el) {
            if (isAlreadyPast(el)) {
                markVisible(el);
                return;
            }
            holdObserver.observe(el);
        });

        window.addEventListener('scroll', function () {
            document.querySelectorAll('.home-reveal:not(.is-visible)').forEach(function (el) {
                if (isAlreadyPast(el)) {
                    markVisible(el);
                }
            });
        }, { passive: true });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHomeReveal);
    } else {
        initHomeReveal();
    }
}());
