/* tz-generator-2.js — stat counters, process rail (SECT-10), holo tilt (CARD-05) */
(function () {
    'use strict';

    var root = document.getElementById('tzRoot');
    if (!root) return;

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function formatCountValue(value) {
        return String(value).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function initStatCounters() {
        var els = root.querySelectorAll('.pl-tz__stat-num[data-count-to]');
        if (!els.length) return;

        function setFinal(el) {
            var target = parseInt(el.getAttribute('data-count-to'), 10);
            if (!target || isNaN(target)) return;
            var suffix = el.getAttribute('data-count-suffix') || '';
            var unitText = el.getAttribute('data-count-unit') || '';
            el.textContent = formatCountValue(target) + suffix;
            if (unitText) {
                var span = document.createElement('span');
                span.textContent = unitText;
                el.appendChild(span);
            }
        }

        function runCounter(el, delay) {
            var target = parseInt(el.getAttribute('data-count-to'), 10);
            if (!target || isNaN(target)) return;
            var suffix = el.getAttribute('data-count-suffix') || '';
            var unitText = el.getAttribute('data-count-unit') || '';
            var duration = target >= 1000 ? 1500 : 1000;
            var startTime = null;

            function frame(now) {
                if (!startTime) startTime = now;
                var progress = Math.min(1, (now - startTime) / duration);
                var eased = 1 - Math.pow(1 - progress, 3);
                var value = Math.round(target * eased);
                el.textContent = formatCountValue(value) + suffix;
                if (progress < 1) {
                    requestAnimationFrame(frame);
                } else {
                    el.textContent = formatCountValue(target) + suffix;
                    if (unitText) {
                        var span = document.createElement('span');
                        span.textContent = unitText;
                        el.appendChild(span);
                    }
                }
            }

            setTimeout(function () { requestAnimationFrame(frame); }, delay);
        }

        if (reduceMotion) {
            els.forEach(setFinal);
            return;
        }

        var done = false;
        function trigger() {
            if (done) return;
            done = true;
            els.forEach(function (el, i) { runCounter(el, i * 120); });
        }

        var host = els[0].closest('[data-compare-reveal]') || els[0].parentElement;

        if ('IntersectionObserver' in window && host) {
            var io = new IntersectionObserver(function (ents) {
                ents.forEach(function (en) {
                    if (en.isIntersecting) {
                        trigger();
                        io.unobserve(host);
                    }
                });
            }, { threshold: 0.2 });
            io.observe(host);
        } else {
            trigger();
        }
    }

    /* ===== PROCESS RAIL (SECT-10) ===== */
    function initProcessRail(selector) {
        var wrap = root.querySelector(selector || '.process-rail');
        if (!wrap) return;
        var fill = wrap.querySelector('.process-rail__fill');
        var items = Array.prototype.slice.call(wrap.querySelectorAll('.process-rail__item'));
        if (!fill || !items.length) return;

        var bar = fill.closest('.process-rail__bar');
        if (bar) bar.classList.remove('reveal', 'is-visible');

        if (reduceMotion) {
            wrap.classList.add('is-rail-on');
            items.forEach(function (item) { item.classList.add('is-stamped'); });
            return;
        }

        function armRail() {
            if (wrap.classList.contains('is-rail-on')) return;
            var anyVisible = items.some(function (item) { return item.classList.contains('is-visible'); });
            if (!anyVisible) return;
            wrap.classList.add('is-rail-on');
        }

        function queueStamp(item, index) {
            if (item.dataset.stampQueued === '1') return;
            if (!item.classList.contains('is-visible')) return;
            item.dataset.stampQueued = '1';
            setTimeout(function () { item.classList.add('is-stamped'); }, 90 + index * 120);
        }

        function maybeDisconnect() {
            var allQueued = items.every(function (item) { return item.dataset.stampQueued === '1'; });
            if (allQueued && wrap.classList.contains('is-rail-on')) {
                classObserver.disconnect();
            }
        }

        function onClassChange() {
            armRail();
            items.forEach(function (item, i) { queueStamp(item, i); });
            maybeDisconnect();
        }

        var classObserver = new MutationObserver(onClassChange);
        items.forEach(function (item, i) {
            classObserver.observe(item, { attributes: true, attributeFilter: ['class'] });
            queueStamp(item, i);
        });
        armRail();
        maybeDisconnect();
    }

    /* ===== HOLO TILT (CARD-05) ===== */
    function initHoloTilt(selector) {
        if (reduceMotion) return;
        if (!window.matchMedia || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

        root.querySelectorAll(selector || '[data-tilt]').forEach(function (card) {
            var rect = null;
            var raf = 0;
            var pending = null;

            function apply() {
                raf = 0;
                if (!pending || !rect) return;
                var clientX = pending.clientX;
                var clientY = pending.clientY;
                pending = null;
                var px = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
                var py = Math.min(1, Math.max(0, (clientY - rect.top) / rect.height));
                var x = px - 0.5;
                var y = py - 0.5;
                card.style.setProperty('--tilt-x', (-y * 18).toFixed(2) + 'deg');
                card.style.setProperty('--tilt-y', (x * 24).toFixed(2) + 'deg');
                card.style.setProperty('--px', px.toFixed(4));
                card.style.setProperty('--py', py.toFixed(4));
                card.classList.add('is-tilt');
            }

            card.addEventListener('pointerenter', function () {
                rect = card.getBoundingClientRect();
            });
            card.addEventListener('pointermove', function (event) {
                if (!card.classList.contains('is-visible')) return;
                if (!rect) rect = card.getBoundingClientRect();
                pending = { clientX: event.clientX, clientY: event.clientY };
                if (!raf) raf = requestAnimationFrame(apply);
            }, { passive: true });
            card.addEventListener('pointerleave', function () {
                if (raf) cancelAnimationFrame(raf);
                raf = 0;
                pending = null;
                rect = null;
                card.classList.remove('is-tilt');
                card.style.removeProperty('--tilt-x');
                card.style.removeProperty('--tilt-y');
                card.style.removeProperty('--px');
                card.style.removeProperty('--py');
            });
        });
    }

    function init() {
        initStatCounters();
        initProcessRail();
        initHoloTilt();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
