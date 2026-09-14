(function () {
    'use strict';

    var root = document.getElementById('plShopRoot');
    if (!root) return;

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function scriptNonce() {
        var tagged = document.querySelector('script[nonce]');
        if (!tagged) return '';
        return tagged.nonce || tagged.getAttribute('nonce') || '';
    }

    function loadPageScript(src, onload) {
        if (!src) return;
        var loaded = window.__plShopScripts || (window.__plShopScripts = {});
        if (loaded[src] === 'done') {
            if (onload) onload();
            return;
        }
        if (loaded[src] === 'pending') {
            if (onload) {
                document.querySelectorAll('script[src="' + src + '"]').forEach(function (el) {
                    el.addEventListener('load', onload, { once: true });
                });
            }
            return;
        }
        loaded[src] = 'pending';
        var s = document.createElement('script');
        s.src = src;
        s.defer = true;
        var nonce = scriptNonce();
        if (nonce) {
            s.setAttribute('nonce', nonce);
            s.nonce = nonce;
        }
        s.addEventListener('load', function () {
            loaded[src] = 'done';
            if (onload) onload();
        }, { once: true });
        s.addEventListener('error', function () {
            loaded[src] = 'done';
        }, { once: true });
        document.body.appendChild(s);
    }

    function loadWhenNear(selector, src, onload) {
        var el = root.querySelector(selector) || document.querySelector(selector);
        if (!el || !src) return;

        function go() {
            loadPageScript(src, onload);
        }

        if (!('IntersectionObserver' in window)) {
            go();
            return;
        }

        var io = new IntersectionObserver(function (entries) {
            if (entries.some(function (entry) { return entry.isIntersecting; })) {
                io.disconnect();
                go();
            }
        }, { rootMargin: '480px 0px' });
        io.observe(el);
    }

    function initReveal() {
        var els = root.querySelectorAll('[data-reveal]');
        if (!els.length) return;

        if (reduceMotion) {
            els.forEach(function (el) { el.classList.add('is-in'); });
            return;
        }

        root.classList.add('is-reveal-ready');

        function reveal(el) {
            el.classList.add('is-in');
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

            els.forEach(function (el) {
                io.observe(el);
            });

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

    function prepareHeroChartDraw(chartWrap, line) {
        if (!line) return;

        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                var len = line.getTotalLength();
                if (!len || len < 50) len = 2800;
                line.style.strokeDasharray = len + ' ' + len;
                line.style.strokeDashoffset = String(len);
                if (chartWrap) chartWrap.classList.remove('is-drawn');
            });
        });
    }

    function playHeroChartDraw(chartWrap, line) {
        if (!line) return;

        requestAnimationFrame(function () {
            line.style.strokeDashoffset = '0';
            if (chartWrap) chartWrap.classList.add('is-drawn');

            line.addEventListener('transitionend', function onDrawEnd(e) {
                if (e.propertyName !== 'stroke-dashoffset') return;
                line.removeEventListener('transitionend', onDrawEnd);
                line.style.strokeDasharray = 'none';
                line.style.strokeDashoffset = '0';
            });
        });
    }

    function initHeroSequence() {
        var img = root.querySelector('[data-hero-img]');
        if (!img) return;

        var chartWrap = root.querySelector('[data-hero-chart-wrap]');
        var line = root.querySelector('[data-hero-line]');
        var chips = root.querySelectorAll('[data-hero-chip]');

        prepareHeroChartDraw(chartWrap, line);

        function finish() {
            if (chartWrap) chartWrap.classList.add('is-in');
            playHeroChartDraw(chartWrap, line);
            chips.forEach(function (c) { c.classList.add('is-in'); });
        }

        if (reduceMotion) {
            finish();
            return;
        }

        requestAnimationFrame(function () {
            setTimeout(function () {
                if (chartWrap) chartWrap.classList.add('is-in');
                playHeroChartDraw(chartWrap, line);
            }, 420);
            setTimeout(function () {
                if (chips[0]) chips[0].classList.add('is-in');
            }, 1200);
            setTimeout(function () {
                if (chips[1]) chips[1].classList.add('is-in');
            }, 1520);
        });
    }

    function initCalcPkgLinks() {
        root.querySelectorAll('[data-calc-pkg]').forEach(function (link) {
            link.addEventListener('click', function () {
                var pkg = link.getAttribute('data-calc-pkg');
                if (!pkg) return;
                try {
                    sessionStorage.setItem('pl_shop_pkg_hint', pkg);
                } catch (e) { /* ignore */ }
            });
        });
    }

    function initClientsMarquee() {
        var container = root.querySelector('.pl-shop__clients-stories-container');
        if (!container) return;

        container.setAttribute('aria-label', container.dataset.marqueeLabel || container.getAttribute('aria-label') || '');
        container.setAttribute('role', 'marquee');

        function start() {
            container.classList.add('marquee-active');
        }

        if (reduceMotion) return;

        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        requestAnimationFrame(start);
                        observer.unobserve(container);
                    }
                });
            }, { threshold: 0.1, rootMargin: '50px' });
            observer.observe(container);
        } else {
            requestAnimationFrame(start);
        }
    }

    function observeReveal(el, onReveal) {
        if (!el) return;

        if (reduceMotion) {
            onReveal();
            return;
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        onReveal();
                        io.disconnect();
                    }
                });
            }, { threshold: 0.14, rootMargin: '0px 0px -8% 0px' });

            io.observe(el);

            requestAnimationFrame(function () {
                var rect = el.getBoundingClientRect();
                if (rect.top < (window.innerHeight || 800) * 0.92) {
                    onReveal();
                    io.disconnect();
                }
            });
        } else {
            onReveal();
        }
    }

    function initPkgReadMore() {
        root.querySelectorAll('.pl-shop__pkg-read-more').forEach(function (btn) {
            var extraId = btn.getAttribute('aria-controls');
            var extra = extraId ? document.getElementById(extraId) : null;
            if (!extra) return;

            btn.addEventListener('click', function () {
                var isOpen = btn.getAttribute('aria-expanded') === 'true';
                btn.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
                extra.hidden = isOpen;
                btn.textContent = isOpen
                    ? (btn.dataset.labelMore || btn.textContent)
                    : (btn.dataset.labelLess || btn.textContent);
            });
        });
    }

    function initPkgStagger() {
        var grid = root.querySelector('[data-pkg-stagger]');
        if (!grid) return;

        var cards = grid.querySelectorAll('.pl-shop__pkg-card');
        cards.forEach(function (card, cardIndex) {
            card.style.setProperty('--pkg-i', String(cardIndex));
            var mainList = card.querySelector('.pl-shop__pkg-features > .pl-shop__pkg-list');
            if (!mainList) return;
            mainList.querySelectorAll('li').forEach(function (item, itemIndex) {
                item.style.setProperty('--pkg-li', String(itemIndex));
            });
        });

        observeReveal(grid, function () {
            grid.classList.add('is-revealed');
        });
    }

    function formatCountValue(value) {
        return String(value).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function setSvobodaStatFinalValues(block) {
        block.querySelectorAll('.pl-shop__stat-num[data-count-to]').forEach(function (el) {
            var target = parseInt(el.getAttribute('data-count-to'), 10);
            if (!target || isNaN(target)) return;

            var suffix = el.getAttribute('data-count-suffix') || '';
            var unitSpan = el.querySelector('span');
            var unitText = el.getAttribute('data-count-unit') || '';

            el.textContent = formatCountValue(target) + suffix;
            if (unitSpan || unitText) {
                var span = document.createElement('span');
                span.textContent = unitText || unitSpan.textContent;
                el.appendChild(span);
            }
        });
    }

    function runSvobodaStatCounters(block) {
        block.querySelectorAll('.pl-shop__stat-num[data-count-to]').forEach(function (el, index) {
            var target = parseInt(el.getAttribute('data-count-to'), 10);
            if (!target || isNaN(target)) return;

            var suffix = el.getAttribute('data-count-suffix') || '';
            var unitSpan = el.querySelector('span');
            var duration = target >= 1000 ? 1600 : 1100;
            var delay = 720 + index * 140;
            var startTime = null;

            function updateDisplay(value) {
                var mainText = formatCountValue(value) + suffix;
                if (unitSpan) {
                    if (el.firstChild && el.firstChild.nodeType === 3) {
                        el.firstChild.textContent = mainText;
                    } else {
                        el.insertBefore(document.createTextNode(mainText), unitSpan);
                    }
                    return;
                }
                el.textContent = mainText;
            }

            function tick(now) {
                if (!startTime) startTime = now;
                var progress = Math.min((now - startTime) / duration, 1);
                var eased = 1 - Math.pow(1 - progress, 3);
                updateDisplay(Math.round(target * eased));

                if (progress < 1) {
                    requestAnimationFrame(tick);
                }
            }

            setTimeout(function () {
                requestAnimationFrame(tick);
            }, delay);
        });
    }

    function initSvobodaReveal() {
        var block = root.querySelector('[data-svoboda-reveal]');
        if (!block) return;

        block.querySelectorAll('.pl-shop__card').forEach(function (card, cardIndex) {
            card.style.setProperty('--sv-i', String(cardIndex));
            card.querySelectorAll('.pl-shop__list-item').forEach(function (item, itemIndex) {
                item.style.setProperty('--sv-li', String(itemIndex));
            });
        });

        block.querySelectorAll('.pl-shop__stat').forEach(function (stat, statIndex) {
            stat.style.setProperty('--sv-stat', String(statIndex));
            stat.querySelectorAll('.pl-shop__stat-num').forEach(function (numEl) {
                numEl.style.setProperty('--sv-stat', String(statIndex));
            });
        });

        observeReveal(block, function () {
            block.classList.add('is-revealed');
            if (reduceMotion) {
                setSvobodaStatFinalValues(block);
            } else {
                runSvobodaStatCounters(block);
            }
        });
    }

    function initPkgCompareTabs() {
        var modal = document.getElementById('pl-shop-pkg-compare-modal');
        if (!modal) return;

        var wrap = modal.querySelector('.pl-shop__pkg-matrix-wrap');
        var tabBtns = modal.querySelectorAll('[data-pkg-tab-btn]');
        if (!wrap || !tabBtns.length) return;

        var defaultTab = 'premium';

        function setTab(tabKey) {
            if (!tabKey) return;
            wrap.setAttribute('data-pkg-tab', tabKey);
            tabBtns.forEach(function (btn) {
                var isActive = btn.getAttribute('data-pkg-tab-btn') === tabKey;
                btn.classList.toggle('pl-shop__pkg-matrix-tab--active', isActive);
                btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
            });
        }

        tabBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                setTab(btn.getAttribute('data-pkg-tab-btn'));
            });
        });

        document.querySelectorAll('[data-modal="pl-shop-pkg-compare-modal"]').forEach(function (trigger) {
            trigger.addEventListener('click', function () {
                setTab(defaultTab);
            });
        });
    }

    function initDeferredSections() {
        loadWhenNear('[data-admin-mock]', root.getAttribute('data-admin-js'), function () {
            if (typeof window.initAdminMock === 'function') {
                window.initAdminMock();
            }
        });
        loadWhenNear('#calculator', root.getAttribute('data-quiz-js'));
    }

    function init() {
        initReveal();
        initPkgStagger();
        initPkgReadMore();
        initSvobodaReveal();
        initHeroSequence();
        initCalcPkgLinks();
        initClientsMarquee();
        initPkgCompareTabs();
        initDeferredSections();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
