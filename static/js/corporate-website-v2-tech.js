(function () {
    'use strict';

    var root = document.getElementById('plCorpRoot');
    if (!root) return;

    var explorer = root.querySelector('[data-tech-explorer]');
    if (!explorer) return;

    var tabs = explorer.querySelectorAll('[data-tech-tab]');
    var panels = explorer.querySelectorAll('[data-tech-panel]');
    if (!tabs.length || !panels.length) return;

    var AUTO_MS = 2500;
    var autoTimer = null;
    var currentIndex = 0;
    var hoverPaused = false;
    var focusPaused = false;
    var offscreen = false;

    var finePointer = window.matchMedia &&
        window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function prepareTechChartReveal(chartWrap, plot) {
        if (chartWrap) chartWrap.classList.remove('is-drawn');
        if (!plot) return;

        plot.style.transition = 'none';
        plot.style.clipPath = 'inset(100% 0 0 0)';
        plot.style.webkitClipPath = 'inset(100% 0 0 0)';
    }

    function playTechChartReveal(chartWrap, plot) {
        if (!plot) return;

        requestAnimationFrame(function () {
            plot.style.transition = 'clip-path 1.1s cubic-bezier(0.4, 0.8, 0.3, 1), -webkit-clip-path 1.1s cubic-bezier(0.4, 0.8, 0.3, 1)';
            plot.style.clipPath = 'inset(0 0 0 0)';
            plot.style.webkitClipPath = 'inset(0 0 0 0)';
            if (chartWrap) chartWrap.classList.add('is-drawn');
        });
    }

    function prepareTechRingFill(ringArc, ringNum) {
        if (!ringArc) return;

        requestAnimationFrame(function () {
            var len = ringArc.getTotalLength();
            if (!len || len < 20) len = 289;

            ringArc.style.transition = 'none';
            ringArc.style.strokeDasharray = len + ' ' + len;
            ringArc.style.strokeDashoffset = String(len);
            if (ringNum) ringNum.textContent = '0';
        });
    }

    function playTechRingFill(ringArc, ringNum) {
        if (!ringArc) return;

        var len = ringArc.getTotalLength();
        if (!len || len < 20) len = 289;
        var duration = 1350;

        requestAnimationFrame(function () {
            ringArc.style.transition = 'stroke-dashoffset ' + (duration / 1000) + 's cubic-bezier(0.4, 0.8, 0.3, 1)';
            ringArc.style.strokeDashoffset = '0';
        });

        if (!ringNum) return;

        if (reduceMotion) {
            ringNum.textContent = '100';
            return;
        }

        var start = null;

        function tick(ts) {
            if (!start) start = ts;
            var progress = Math.min((ts - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            ringNum.textContent = String(Math.round(eased * 100));
            if (progress < 1) requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);
    }

    function restartPanelAnimations(panel) {
        if (!panel) return;

        var chartWrap = panel.querySelector('[data-tech-chart-wrap]');
        var chartPlot = panel.querySelector('[data-tech-chart-plot]');
        var ringArc = panel.querySelector('[data-tech-ring-arc]');
        var ringNum = panel.querySelector('[data-tech-ring-num]');

        if (chartPlot) {
            if (reduceMotion) {
                if (chartWrap) chartWrap.classList.add('is-drawn');
                chartPlot.style.transition = 'none';
                chartPlot.style.clipPath = 'inset(0 0 0 0)';
                chartPlot.style.webkitClipPath = 'inset(0 0 0 0)';
            } else {
                prepareTechChartReveal(chartWrap, chartPlot);
                playTechChartReveal(chartWrap, chartPlot);
            }
        }

        if (ringArc) {
            if (reduceMotion) {
                var ringLen = ringArc.getTotalLength();
                if (!ringLen || ringLen < 20) ringLen = 289;
                ringArc.style.transition = 'none';
                ringArc.style.strokeDasharray = ringLen + ' ' + ringLen;
                ringArc.style.strokeDashoffset = '0';
                if (ringNum) ringNum.textContent = '100';
            } else {
                prepareTechRingFill(ringArc, ringNum);
                playTechRingFill(ringArc, ringNum);
            }
        }

        if (reduceMotion) return;

        var animated = panel.querySelectorAll('.pl-corp__tech-bar, .pl-corp__tech-device');

        animated.forEach(function (el) {
            el.style.animation = 'none';
            void el.offsetWidth;
            el.style.animation = '';
        });
    }

    function setActive(idx) {
        currentIndex = parseInt(idx, 10);
        if (isNaN(currentIndex)) currentIndex = 0;

        var id = String(currentIndex);
        var activePanel = null;

        tabs.forEach(function (tab) {
            var on = tab.getAttribute('data-tech-tab') === id;
            tab.classList.toggle('is-active', on);
            tab.setAttribute('aria-selected', on ? 'true' : 'false');
            tab.setAttribute('tabindex', on ? '0' : '-1');
        });

        panels.forEach(function (panel) {
            var on = panel.getAttribute('data-tech-panel') === id;
            panel.classList.toggle('is-active', on);
            panel.setAttribute('aria-hidden', on ? 'false' : 'true');
            if (on) activePanel = panel;
        });

        restartPanelAnimations(activePanel);
    }

    function shouldAutoRun() {
        return !reduceMotion && !hoverPaused && !focusPaused && !offscreen;
    }

    function stopAuto() {
        if (!autoTimer) return;
        clearInterval(autoTimer);
        autoTimer = null;
    }

    function startAuto() {
        if (!shouldAutoRun() || autoTimer) return;
        autoTimer = setInterval(function () {
            setActive((currentIndex + 1) % tabs.length);
        }, AUTO_MS);
    }

    function syncAuto() {
        stopAuto();
        startAuto();
    }

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            setActive(tab.getAttribute('data-tech-tab'));
            syncAuto();
        });

        if (finePointer) {
            tab.addEventListener('mouseenter', function () {
                setActive(tab.getAttribute('data-tech-tab'));
            });
        }

        tab.addEventListener('keydown', function (e) {
            var current = parseInt(tab.getAttribute('data-tech-tab'), 10);
            var next = -1;

            if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                next = (current + 1) % tabs.length;
            } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                next = (current - 1 + tabs.length) % tabs.length;
            } else if (e.key === 'Home') {
                next = 0;
            } else if (e.key === 'End') {
                next = tabs.length - 1;
            }

            if (next < 0) return;

            e.preventDefault();
            setActive(next);
            tabs[next].focus();
            syncAuto();
        });
    });

    explorer.addEventListener('mouseenter', function () {
        hoverPaused = true;
        syncAuto();
    });

    explorer.addEventListener('mouseleave', function () {
        hoverPaused = false;
        syncAuto();
    });

    explorer.addEventListener('focusin', function () {
        focusPaused = true;
        syncAuto();
    });

    explorer.addEventListener('focusout', function (e) {
        if (!explorer.contains(e.relatedTarget)) {
            focusPaused = false;
            syncAuto();
        }
    });

    if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                offscreen = !entry.isIntersecting;
                syncAuto();
            });
        }, { threshold: 0.2 });

        io.observe(explorer);
    }

    setActive(0);
    syncAuto();
})();
