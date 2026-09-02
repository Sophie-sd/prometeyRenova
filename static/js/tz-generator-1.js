/* tz-generator-1.js — reveal, hero doc mockup, clients marquee */
(function () {
    'use strict';

    var root = document.getElementById('tzRoot');
    if (!root) return;

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function initReveal() {
        var els = root.querySelectorAll('[data-reveal], .reveal');
        if (!els.length) return;

        if (reduceMotion) {
            els.forEach(function (el) {
                el.classList.add('is-visible');
                el.classList.remove('is-pending-reveal');
            });
            return;
        }

        els.forEach(function (el) {
            if (el.__rev) return;
            el.__rev = 1;
            el.classList.add('is-pending-reveal');
        });

        function reveal(el) {
            el.classList.remove('is-pending-reveal');
            el.classList.add('is-visible');
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (ents) {
                ents.forEach(function (en) {
                    if (en.isIntersecting) {
                        reveal(en.target);
                        io.unobserve(en.target);
                    }
                });
            }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });

            els.forEach(function (el) { io.observe(el); });

            requestAnimationFrame(function () {
                var vh = window.innerHeight || 800;
                els.forEach(function (el) {
                    var r = el.getBoundingClientRect();
                    if (r.top < vh * 0.95) {
                        reveal(el);
                        io.unobserve(el);
                    }
                });
            });
        } else {
            els.forEach(reveal);
        }
    }

    function initHeroDoc() {
        var doc = root.querySelector('[data-doc]');
        if (!doc) return;

        var panels = doc.querySelectorAll('[data-doc-panel]');
        var tabs = doc.querySelectorAll('[data-doc-tab]');
        var lines = doc.querySelectorAll('[data-doc-line]');
        var tabIds = ['brief', 'structure', 'budget'];
        var cycleTimer = null;
        var cyclePaused = false;
        var cycleIndex = 0;
        var CYCLE_MS = 4200;

        function showPanel(id) {
            panels.forEach(function (p) {
                var active = p.getAttribute('data-doc-panel') === id;
                p.classList.toggle('is-active', active);
                p.setAttribute('aria-hidden', active ? 'false' : 'true');
            });
            tabs.forEach(function (t) {
                var active = t.getAttribute('data-doc-tab') === id;
                t.classList.toggle('is-active', active);
                t.setAttribute('aria-selected', active ? 'true' : 'false');
            });
            cycleIndex = tabIds.indexOf(id);
            if (cycleIndex < 0) cycleIndex = 0;
        }

        tabs.forEach(function (t) {
            t.addEventListener('click', function () {
                cyclePaused = true;
                showPanel(t.getAttribute('data-doc-tab'));
            });
        });

        function tick() {
            if (cyclePaused) return;
            cycleIndex = (cycleIndex + 1) % tabIds.length;
            showPanel(tabIds[cycleIndex]);
        }

        function startCycle() {
            if (reduceMotion) return;
            if (cycleTimer) clearInterval(cycleTimer);
            cycleTimer = setInterval(tick, CYCLE_MS);
        }

        doc.addEventListener('pointerenter', function () { cyclePaused = true; });
        doc.addEventListener('pointerleave', function () { cyclePaused = false; });

        function staggerLines() {
            lines.forEach(function (line, i) {
                setTimeout(function () {
                    line.classList.add('is-visible');
                }, 260 + i * 110);
            });
        }

        function finish() {
            doc.classList.add('is-live');
            lines.forEach(function (l) { l.classList.add('is-visible'); });
        }

        if (reduceMotion) {
            finish();
            return;
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (ents) {
                ents.forEach(function (en) {
                    if (en.isIntersecting) {
                        doc.classList.add('is-live');
                        staggerLines();
                        startCycle();
                        io.unobserve(doc);
                    }
                });
            }, { threshold: 0.25 });
            io.observe(doc);
        } else {
            finish();
            startCycle();
        }
    }

    function init() {
        initReveal();
        initHeroDoc();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.__tzInitReveal = initReveal;
})();
