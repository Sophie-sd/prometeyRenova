(function () {
    'use strict';

    var SVGNS = 'http://www.w3.org/2000/svg';
    var GAP = 12;
    var AH = 6;
    var GLOW_PAD = 4;
    var STEP_IMG_DELAY = 130;
    var STEP_STAGGER = 270;
    var ARROW_DRAW_MS = 140;
    var NUM_TO_TITLE_GAP = 9;
    var TITLE_PHASE_DURATION = 120;
    var LETTER_GAP = 10;

    var anim = window.PbProcessAnim;

    function wait(ms) {
        return new Promise(function (resolve) {
            setTimeout(resolve, ms);
        });
    }

    function getSection(host) {
        if (!host) return null;
        if (host.id === 'pb-process') return host;
        return host.querySelector('#pb-process');
    }

    function isSkeleton(section) {
        return section && section.classList.contains('pb-process--skeleton');
    }

    function isGridInViewport(grid) {
        var rect = grid.getBoundingClientRect();
        var vh = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < vh * 0.92 && rect.bottom > vh * 0.08;
    }

    function destroyInstance(section) {
        if (!section || !section._pbDestroy) return;
        section._pbDestroy();
        section._pbDestroy = null;
    }

    function verticalPath(a, b) {
        var x = a.cx;
        var channel = b.t - a.b;
        var startOffset = 8;
        var endOffset = AH + GLOW_PAD + 14;
        var gapStart = a.b + startOffset;
        var tipY = b.t - endOffset;
        var shaftEnd = tipY - AH;

        if (channel < startOffset + endOffset + AH + 8) {
            var mid = (a.b + b.t) * 0.5;
            gapStart = mid - AH;
            shaftEnd = mid - AH * 0.35;
            tipY = mid + AH * 0.65;
        }

        gapStart = Math.max(gapStart, a.b + 6);
        tipY = Math.min(tipY, b.t - 12);
        shaftEnd = Math.min(shaftEnd, tipY - 4);

        if (shaftEnd <= gapStart) {
            shaftEnd = gapStart + Math.max(4, (tipY - gapStart) * 0.65);
        }

        return {
            d: 'M ' + x + ' ' + gapStart
                + ' L ' + x + ' ' + shaftEnd
                + ' M ' + x + ' ' + tipY
                + ' L ' + (x - AH * 0.65) + ' ' + (tipY - AH)
                + ' M ' + x + ' ' + tipY
                + ' L ' + (x + AH * 0.65) + ' ' + (tipY - AH),
            vertical: true
        };
    }

    function horizontalPath(a, b) {
        var y = (a.cy + b.cy) * 0.5;
        var x1;
        var x2;
        var d;

        if (b.cx > a.cx) {
            x1 = a.r + GAP;
            x2 = b.l - GAP;
            d = 'M ' + x1 + ' ' + y + ' L ' + x2 + ' ' + y
                + ' M ' + x2 + ' ' + y
                + ' L ' + (x2 - AH) + ' ' + (y - AH * 0.6)
                + ' M ' + x2 + ' ' + y
                + ' L ' + (x2 - AH) + ' ' + (y + AH * 0.6);
        } else {
            x1 = a.l - GAP;
            x2 = b.r + GAP;
            d = 'M ' + x1 + ' ' + y + ' L ' + x2 + ' ' + y
                + ' M ' + x2 + ' ' + y
                + ' L ' + (x2 + AH) + ' ' + (y - AH * 0.6)
                + ' M ' + x2 + ' ' + y
                + ' L ' + (x2 + AH) + ' ' + (y + AH * 0.6);
        }

        return { d: d, vertical: false };
    }

    function connectorPath(a, b) {
        var sameRow = Math.abs(a.cy - b.cy) < a.h * 0.5;
        return sameRow ? horizontalPath(a, b) : verticalPath(a, b);
    }

    function initProcessBlock(host) {
        var section = getSection(host);
        if (!section || isSkeleton(section)) return null;

        destroyInstance(section);

        var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        var wrap = section.querySelector('#pb-grid-wrap');
        var grid = section.querySelector('#pb-grid');
        var svg = section.querySelector('#pb-arrows');

        if (!wrap || !grid || !svg) return null;

        var cards = Array.prototype.slice.call(grid.querySelectorAll('.pb-step'));
        var paths = [];
        var token = 0;
        var resizeTimer;
        var started = false;
        var completed = false;

        cards.forEach(function (card) {
            if (anim) {
                anim.setupWatermarkNum(card.querySelector('.pb-step__num'));
                anim.setupTypewriterTitle(card.querySelector('.pb-step__title'));
            }
        });

        function syncSvgViewBox() {
            var wr = wrap.getBoundingClientRect();
            if (wr.width < 1 || wr.height < 1) return false;
            svg.setAttribute('viewBox', '0 0 ' + wr.width + ' ' + wr.height);
            return true;
        }

        function getCardBoxes() {
            var gridRect = grid.getBoundingClientRect();
            var wrapRect = wrap.getBoundingClientRect();
            var offsetX = gridRect.left - wrapRect.left;
            var offsetY = gridRect.top - wrapRect.top;

            return cards.map(function (card) {
                var w = card.offsetWidth;
                var h = card.offsetHeight;
                var left = offsetX + card.offsetLeft;
                var top = offsetY + card.offsetTop;

                return {
                    l: left,
                    t: top,
                    r: left + w,
                    b: top + h,
                    h: h,
                    cx: left + w * 0.5,
                    cy: top + h * 0.5
                };
            });
        }

        function applyPathGeometry(pathEl, result) {
            pathEl.setAttribute('d', result.d);
            pathEl.setAttribute('class', result.vertical ? 'pb-arrow pb-arrow--v' : 'pb-arrow pb-arrow--h');
            var len = pathEl.getTotalLength();
            pathEl._len = len;
            pathEl.style.strokeDasharray = len;
            return len;
        }

        function rebuildPath(index, keepOffset) {
            if (!syncSvgViewBox()) return null;

            var boxes = getCardBoxes();
            var a = boxes[index];
            var b = boxes[index + 1];
            if (!a || !b) return null;

            var result = connectorPath(a, b);
            var pathEl = paths[index];

            if (!pathEl) {
                pathEl = document.createElementNS(SVGNS, 'path');
                svg.appendChild(pathEl);
                paths[index] = pathEl;
            }

            applyPathGeometry(pathEl, result);

            if (!keepOffset) {
                pathEl.style.transition = 'none';
                pathEl.style.strokeDashoffset = pathEl._len;
            }

            return pathEl;
        }

        function buildArrows(resetOffset) {
            paths.forEach(function (p) {
                p.remove();
            });
            paths = [];

            if (!syncSvgViewBox()) return;

            var boxes = getCardBoxes();

            for (var i = 0; i < boxes.length - 1; i++) {
                var result = connectorPath(boxes[i], boxes[i + 1]);
                var pathEl = document.createElementNS(SVGNS, 'path');
                applyPathGeometry(pathEl, result);
                pathEl.style.strokeDashoffset = resetOffset === false ? 0 : pathEl._len;
                svg.appendChild(pathEl);
                paths.push(pathEl);
            }
        }

        function resetCardPopover(card) {
            var popover = card.querySelector('.pb-step__popover');
            var btn = card.querySelector('.pb-step__detail-btn');
            if (!popover) {
                return;
            }
            popover.classList.remove('is-open', 'pb-step__popover--below');
            popover.setAttribute('aria-hidden', 'true');
            popover.setAttribute('hidden', '');
            popover.style.removeProperty('--pb-popover-shift');
            if (btn) {
                btn.setAttribute('aria-expanded', 'false');
            }
        }

        function resetCardState(card) {
            resetCardPopover(card);
            card.classList.remove('is-visible', 'is-img-visible', 'is-title-visible');
            if (anim) {
                anim.resetWatermarkNum(card.querySelector('.pb-step__num'));
                anim.resetTypewriterIn(card);
            }
        }

        function revealCardInstant(card) {
            card.classList.add('is-visible', 'is-img-visible', 'is-title-visible');
            if (anim) {
                anim.showNumInstant(card.querySelector('.pb-step__num'));
                anim.showTypewriterInstant(card);
            }
        }

        function hideAll() {
            started = false;
            cards.forEach(resetCardState);
            paths.forEach(function (p) {
                p.style.transition = 'none';
                p.style.strokeDashoffset = p._len;
            });
            void grid.offsetWidth;
        }

        function showAllInstant() {
            started = true;
            cards.forEach(revealCardInstant);
            buildArrows(false);
            paths.forEach(function (p) {
                p.style.transition = 'none';
                p.style.strokeDashoffset = 0;
            });
        }

        function waitForLayout() {
            return new Promise(function (resolve) {
                requestAnimationFrame(function () {
                    requestAnimationFrame(resolve);
                });
            });
        }

        async function animateCard(card, my) {
            card.classList.add('is-img-visible');
            await wait(STEP_IMG_DELAY);
            if (my !== token) return;

            card.classList.add('is-visible');

            var numEl = card.querySelector('.pb-step__num');
            var titleEl = card.querySelector('.pb-step__title');

            if (anim) {
                if (!(await anim.playNumSequence(numEl, my, token, wait))) {
                    return;
                }
            }

            if (my !== token) return;

            await wait(NUM_TO_TITLE_GAP);
            if (my !== token) return;

            card.classList.add('is-title-visible');

            if (anim && titleEl) {
                anim.revealTypewriterEl(titleEl, LETTER_GAP, my, token, wait);
            }
        }

        async function play() {
            if (started || completed) return;

            var my = ++token;

            if (reduce) {
                showAllInstant();
                completed = true;
                observer.disconnect();
                return;
            }

            hideAll();
            started = true;
            observer.disconnect();

            buildArrows(true);

            for (var i = 0; i < cards.length; i++) {
                if (my !== token) return;

                animateCard(cards[i], my);

                if (i < cards.length - 1) {
                    await wait(STEP_STAGGER);
                    if (my !== token) return;

                    await waitForLayout();
                    var pathEl = rebuildPath(i, false);
                    if (pathEl) {
                        pathEl.style.transition = 'stroke-dashoffset ' + (ARROW_DRAW_MS / 1000) + 's cubic-bezier(0.16, 1, 0.3, 1)';
                        pathEl.style.strokeDashoffset = 0;
                    }
                }
            }

            buildArrows(false);
            paths.forEach(function (p) {
                p.style.transition = 'none';
                p.style.strokeDashoffset = 0;
            });
            completed = true;
        }

        function tryStart() {
            if (started || completed) return;
            if (!isGridInViewport(grid)) return;
            requestAnimationFrame(function () {
                requestAnimationFrame(function () {
                    play();
                });
            });
        }

        function onResize() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function () {
                var wasComplete = started;
                buildArrows(!wasComplete);
                if (wasComplete) {
                    paths.forEach(function (p) {
                        p.style.transition = 'none';
                        p.style.strokeDashoffset = 0;
                    });
                }
            }, 200);
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (e.isIntersecting && e.intersectionRatio >= 0.08) {
                    tryStart();
                }
            });
        }, {
            threshold: [0, 0.08, 0.2, 0.35],
            rootMargin: '0px 0px -5% 0px'
        });

        observer.observe(grid);
        window.addEventListener('resize', onResize);

        var popoverDestroy = typeof window.initProcessBlockPopovers === 'function'
            ? window.initProcessBlockPopovers(section)
            : null;

        section._pbDestroy = function () {
            token++;
            observer.disconnect();
            window.removeEventListener('resize', onResize);
            clearTimeout(resizeTimer);
            if (popoverDestroy) {
                popoverDestroy();
                popoverDestroy = null;
            }
        };

        tryStart();

        return section;
    }

    function handleHtmxUpdate(event) {
        var target = event.detail && event.detail.target;
        if (!target || target.id !== 'pf-flow-root') return;
        initProcessBlock(target);
    }

    document.body.addEventListener('htmx:afterSwap', handleHtmxUpdate);
    document.body.addEventListener('htmx:afterSettle', handleHtmxUpdate);

    function boot() {
        var root = document.getElementById('pf-flow-root');
        if (root) {
            initProcessBlock(root);
            return;
        }

        var section = document.getElementById('pb-process');
        if (section) {
            initProcessBlock(section);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
