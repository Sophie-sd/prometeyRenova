(function () {
    'use strict';

    var STEP_DELAY = 720;
    var CONNECTOR_DELAY = 980;
    var RESIZE_DEBOUNCE = 150;

    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function debounce(fn, ms) {
        var timer;
        return function () {
            var args = arguments;
            var ctx = this;
            clearTimeout(timer);
            timer = setTimeout(function () {
                fn.apply(ctx, args);
            }, ms);
        };
    }

    function wait(ms) {
        return new Promise(function (resolve) {
            setTimeout(resolve, ms);
        });
    }

    function getInnerRect(stepEl, stageRect) {
        var inner = stepEl.querySelector('.pf-flow__step-inner') || stepEl;
        var rect = inner.getBoundingClientRect();
        return {
            left: rect.left - stageRect.left,
            right: rect.right - stageRect.left,
            top: rect.top - stageRect.top,
            bottom: rect.bottom - stageRect.top,
            centerX: rect.left + rect.width / 2 - stageRect.left,
            centerY: rect.top + rect.height / 2 - stageRect.top
        };
    }

    function getLinkBox(fromStep, toStep, allSteps) {
        var stage = fromStep.closest('.pf-flow__stage');
        var stageRect = stage.getBoundingClientRect();
        var from = getInnerRect(fromStep, stageRect);
        var to = getInnerRect(toStep, stageRect);
        var inset = 8;
        var minSize = 6;
        var channelV = 4;
        var channelH = 8;
        var box = null;
        var rowOverlap = Math.min(from.bottom, to.bottom) - Math.max(from.top, to.top);
        var isSameRow = rowOverlap >= minSize;

        if (isSameRow && to.left >= from.right + minSize) {
            var width = to.left - from.right - inset * 2;
            if (width >= minSize) {
                var overlapTop = Math.max(from.top, to.top) + inset;
                var overlapBottom = Math.min(from.bottom, to.bottom) - inset;
                var y = (overlapTop + overlapBottom) / 2;

                box = {
                    type: 'h',
                    left: from.right + inset,
                    top: y - channelH / 2,
                    width: width,
                    height: channelH,
                    rtl: false
                };
            }
        } else if (isSameRow && from.left >= to.right + minSize) {
            var rtlWidth = from.left - to.right - inset * 2;
            if (rtlWidth >= minSize) {
                var rtlOverlapTop = Math.max(from.top, to.top) + inset;
                var rtlOverlapBottom = Math.min(from.bottom, to.bottom) - inset;
                var rtlY = (rtlOverlapTop + rtlOverlapBottom) / 2;

                box = {
                    type: 'h',
                    left: to.right + inset,
                    top: rtlY - channelH / 2,
                    width: rtlWidth,
                    height: channelH,
                    rtl: true
                };
            }
        } else if (to.top >= from.bottom + minSize) {
            var height = to.top - from.bottom - inset * 2;
            if (height >= minSize) {
                var x = from.centerX;
                var overlapLeft = Math.max(from.left, to.left) + inset;
                var overlapRight = Math.min(from.right, to.right) - inset;

                if (overlapRight - overlapLeft >= minSize) {
                    x = (overlapLeft + overlapRight) / 2;
                }

                box = {
                    type: 'v',
                    left: x - channelV / 2,
                    top: from.bottom + inset,
                    width: channelV,
                    height: height,
                    rtl: false
                };
            }
        }

        if (!box) return null;

        if (allSteps && linkIntersectsCards(box, allSteps, stageRect, [fromStep, toStep])) {
            return null;
        }

        return box;
    }

    function linkIntersectsCards(box, steps, stageRect, skipSteps) {
        var linkRect = {
            left: box.left,
            top: box.top,
            right: box.left + box.width,
            bottom: box.top + box.height
        };

        for (var i = 0; i < steps.length; i++) {
            if (skipSteps.indexOf(steps[i]) >= 0) continue;

            var card = getInnerRect(steps[i], stageRect);
            if (
                linkRect.left < card.right &&
                linkRect.right > card.left &&
                linkRect.top < card.bottom &&
                linkRect.bottom > card.top
            ) {
                return true;
            }
        }

        return false;
    }

    function buildLinkPath(box) {
        var w = Math.max(box.width, 1);
        var h = Math.max(box.height, 1);

        if (box.type === 'h') {
            var cy = h / 2;

            if (box.rtl) {
                return 'M' + w + ',' + cy + ' L0,' + cy;
            }

            return 'M0,' + cy + ' L' + w + ',' + cy;
        }

        var cx = w / 2;
        return 'M' + cx + ',0 L' + cx + ',' + h;
    }

    function preparePathStroke(path) {
        if (!path || typeof path.getTotalLength !== 'function') return;

        var len = path.getTotalLength();
        path.style.strokeDasharray = String(len);
        path.style.strokeDashoffset = String(len);
        path.classList.remove('is-drawn');
    }

    function syncLinkSvg(link, box) {
        var svg = link.querySelector('.pf-flow__link-svg');
        var path = link.querySelector('.pf-flow__link-path');
        var glow = link.querySelector('.pf-flow__link-glow');

        if (!svg || !path || !box) return;

        svg.setAttribute('viewBox', '0 0 ' + box.width + ' ' + box.height);
        svg.setAttribute('preserveAspectRatio', 'none');
        var d = buildLinkPath(box);
        path.setAttribute('d', d);

        if (glow) {
            glow.setAttribute('d', d);
        }

        preparePathStroke(path);
        preparePathStroke(glow);
    }

    function prepareLink(link) {
        link.classList.remove('is-drawn', 'is-complete', 'is-active', 'is-ready');
        preparePathStroke(link.querySelector('.pf-flow__link-path'));
        preparePathStroke(link.querySelector('.pf-flow__link-glow'));
    }

    function applyLinkBox(link, box) {
        if (!box) {
            link.style.display = 'none';
            link.classList.remove('is-ready');
            return;
        }

        link.style.display = 'block';
        link.style.left = box.left + 'px';
        link.style.top = box.top + 'px';
        link.style.width = box.width + 'px';
        link.style.height = box.height + 'px';
        link.classList.remove('pf-flow__link--h', 'pf-flow__link--v', 'pf-flow__link--rtl');
        link.classList.add('pf-flow__link--' + box.type);
        if (box.rtl) {
            link.classList.add('pf-flow__link--rtl');
        }
        link.classList.add('is-ready');
        syncLinkSvg(link, box);
    }

    function updateConnectors(root) {
        var stage = root.querySelector('.pf-flow__stage');
        if (!stage) return;

        var steps = root.querySelectorAll('.pf-flow__step');
        var stepsArray = Array.from(steps);
        var links = root.querySelectorAll('.pf-flow__link');

        root.classList.add('pf-flow--layout-measure');
        void root.offsetHeight;

        links.forEach(function (link, i) {
            var fromStep = steps[i];
            var toStep = steps[i + 1];
            prepareLink(link);

            if (!fromStep || !toStep) {
                link.style.display = 'none';
                link.classList.remove('is-ready');
                return;
            }

            applyLinkBox(link, getLinkBox(fromStep, toStep, stepsArray));
        });

        root.classList.remove('pf-flow--layout-measure');
    }

    function resetHeroAccordion(step) {
        var accordion = step.querySelector('.pf-flow__hero-accordion');
        if (!accordion) return;

        accordion.classList.remove('is-open');
        step.querySelectorAll('.pf-flow__hero-item').forEach(function (item) {
            item.style.animation = 'none';
            item.style.opacity = '0';
            item.style.transform = '';
        });
    }

    function openHeroAccordion(step, instant) {
        var accordion = step.querySelector('.pf-flow__hero-accordion');
        if (!accordion) return;

        step.querySelectorAll('.pf-flow__hero-item').forEach(function (item) {
            item.style.animation = '';
            item.style.opacity = '';
            item.style.transform = '';
        });

        function applyOpen() {
            accordion.classList.add('is-open');
        }

        if (instant) {
            applyOpen();
            return;
        }

        setTimeout(applyOpen, 480);
    }

    function revealStep(step) {
        step.classList.remove('is-revealing', 'is-visible');
        resetHeroAccordion(step);
        void step.offsetWidth;
        step.classList.add('is-revealing');

        requestAnimationFrame(function () {
            step.classList.add('is-visible');
            if (step.classList.contains('pf-flow__step--hero')) {
                openHeroAccordion(step, false);
            }
        });

        var stepDelay = step.classList.contains('pf-flow__step--hero')
            ? STEP_DELAY + 520
            : STEP_DELAY;

        return new Promise(function (resolve) {
            var done = false;
            function finish() {
                if (done) return;
                done = true;
                step.classList.remove('is-revealing');
                resolve();
            }

            step.addEventListener('animationend', finish, { once: true });
            setTimeout(finish, stepDelay);
        });
    }

    function drawConnectorGroup(link) {
        return new Promise(function (resolve) {
            if (!link || !link.classList.contains('is-ready')) {
                resolve();
                return;
            }

            var path = link.querySelector('.pf-flow__link-path');
            var glow = link.querySelector('.pf-flow__link-glow');

            link.classList.add('is-active');
            requestAnimationFrame(function () {
                if (path) {
                    path.classList.add('is-drawn');
                    path.style.strokeDashoffset = '0';
                }
                if (glow) {
                    glow.classList.add('is-drawn');
                    glow.style.strokeDashoffset = '0';
                }
            });

            var done = false;
            function finish() {
                if (done) return;
                done = true;
                link.classList.remove('is-active');
                link.classList.add('is-complete');
                resolve();
            }

            if (path) {
                path.addEventListener('transitionend', finish, { once: true });
            }
            setTimeout(finish, CONNECTOR_DELAY + 80);
        });
    }

    function showAllInstant(root) {
        root.classList.add('is-complete');
        root.querySelectorAll('.pf-flow__step').forEach(function (step) {
            step.classList.add('is-visible');
            step.classList.remove('is-revealing');
            openHeroAccordion(step, true);
        });
        root.querySelectorAll('.pf-flow__link.is-ready').forEach(function (link) {
            link.classList.add('is-drawn', 'is-complete');
            var path = link.querySelector('.pf-flow__link-path');
            var glow = link.querySelector('.pf-flow__link-glow');

            if (path) {
                path.classList.add('is-drawn');
                path.style.strokeDashoffset = '0';
            }
            if (glow) {
                glow.classList.add('is-drawn');
                glow.style.strokeDashoffset = '0';
            }
        });
    }

    function playSequence(root) {
        if (root.dataset.playing === 'true') return;
        root.dataset.playing = 'true';

        var steps = Array.from(root.querySelectorAll('.pf-flow__step'));
        var links = Array.from(root.querySelectorAll('.pf-flow__link'));

        root.classList.remove('is-complete');
        steps.forEach(function (s) {
            s.classList.remove('is-visible', 'is-revealing');
            resetHeroAccordion(s);
        });
        links.forEach(prepareLink);
        updateConnectors(root);

        return (async function () {
            for (var i = 0; i < steps.length; i++) {
                await revealStep(steps[i]);
                if (links[i]) {
                    await drawConnectorGroup(links[i]);
                }
            }
            root.classList.add('is-complete');
            root.dataset.played = 'true';
            root.dataset.playing = 'false';
        })();
    }

    function isInViewport(el) {
        var rect = el.getBoundingClientRect();
        var vh = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < vh * 0.85 && rect.bottom > vh * 0.1;
    }

    function startAnimation(root) {
        if (root.dataset.played === 'true' || root.dataset.playing === 'true') {
            return;
        }
        playSequence(root);
    }

    function initProcessFlow(container) {
        var root = container.querySelector('.pf-flow');
        if (!root || root.classList.contains('pf-flow--skeleton')) return null;

        root.dataset.played = '';
        root.dataset.playing = 'false';
        updateConnectors(root);

        var resizeHandler = debounce(function () {
            var wasComplete = root.classList.contains('is-complete');
            updateConnectors(root);
            if (wasComplete) {
                showAllInstant(root);
            }
        }, RESIZE_DEBOUNCE);

        if (root._pfResizeHandler) {
            window.removeEventListener('resize', root._pfResizeHandler);
        }
        root._pfResizeHandler = resizeHandler;
        window.addEventListener('resize', resizeHandler);

        if (prefersReducedMotion) {
            showAllInstant(root);
            root.dataset.played = 'true';
            return root;
        }

        if (root._pfObserver) {
            root._pfObserver.disconnect();
        }

        if (isInViewport(root)) {
            requestAnimationFrame(function () {
                updateConnectors(root);
                startAnimation(root);
            });
            return root;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting && entry.intersectionRatio >= 0.2) {
                    updateConnectors(root);
                    startAnimation(root);
                    observer.disconnect();
                }
            });
        }, { threshold: [0, 0.2, 0.4] });

        root._pfObserver = observer;
        observer.observe(root);

        return root;
    }

    function handleSwap(event) {
        var target = event.detail && event.detail.target;
        if (!target || target.id !== 'pf-flow-root') return;
        initProcessFlow(target);
    }

    function boot() {
        var root = document.getElementById('pf-flow-root');
        if (root && root.querySelector('.pf-flow:not(.pf-flow--skeleton)')) {
            initProcessFlow(root);
        }

        document.body.addEventListener('htmx:afterSwap', handleSwap);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
