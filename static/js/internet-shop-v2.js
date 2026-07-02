(function () {
    'use strict';

    var root = document.getElementById('plShopRoot');
    if (!root) return;

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function initReveal() {
        var els = root.querySelectorAll('[data-reveal]');
        if (!els.length) return;

        if (reduceMotion) return;

        els.forEach(function (el) {
            if (el.__rev) return;
            el.__rev = 1;
            el.style.opacity = '0';
            el.style.transform = 'translateY(28px)';
            el.style.transition = 'opacity .75s cubic-bezier(.2,.7,.2,1), transform .75s cubic-bezier(.2,.7,.2,1)';
        });

        function reveal(el) {
            el.style.opacity = '1';
            el.style.transform = 'none';
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
                if (!el.__obs) {
                    el.__obs = 1;
                    io.observe(el);
                }
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
            img.style.opacity = '1';
            if (chartWrap) chartWrap.style.opacity = '1';
            playHeroChartDraw(chartWrap, line);
            chips.forEach(function (c) {
                c.style.opacity = '1';
                c.style.transform = 'none';
            });
        }

        if (reduceMotion) {
            finish();
            return;
        }

        img.style.opacity = '0';
        img.style.transition = 'opacity .7s cubic-bezier(.2,.7,.2,1)';
        if (chartWrap) {
            chartWrap.style.opacity = '0';
            chartWrap.style.transition = 'opacity .6s ease';
        }
        chips.forEach(function (c) {
            c.style.opacity = '0';
            c.style.transform = 'translateY(12px) scale(.96)';
            c.style.transition = 'opacity .5s ease, transform .5s cubic-bezier(.2,.7,.2,1)';
        });

        requestAnimationFrame(function () {
            setTimeout(function () { img.style.opacity = '1'; }, 140);
            setTimeout(function () {
                if (chartWrap) chartWrap.style.opacity = '1';
                playHeroChartDraw(chartWrap, line);
            }, 420);
            setTimeout(function () {
                if (chips[0]) {
                    chips[0].style.opacity = '1';
                    chips[0].style.transform = 'none';
                }
            }, 1200);
            setTimeout(function () {
                if (chips[1]) {
                    chips[1].style.opacity = '1';
                    chips[1].style.transform = 'none';
                }
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

    function waitForImages(container) {
        return new Promise(function (resolve, reject) {
            var images = container.querySelectorAll('img');
            if (!images.length) {
                resolve();
                return;
            }

            var loadedCount = 0;
            var totalImages = images.length;
            var timeout = setTimeout(function () { reject(new Error('timeout')); }, 3000);

            function done() {
                loadedCount += 1;
                if (loadedCount === totalImages) {
                    clearTimeout(timeout);
                    resolve();
                }
            }

            images.forEach(function (img) {
                if (img.complete) {
                    done();
                } else {
                    img.addEventListener('load', done, { once: true });
                    img.addEventListener('error', done, { once: true });
                }
            });
        });
    }

    function initClientsMarquee() {
        var container = root.querySelector('.pl-shop__clients-stories-container');
        if (!container) return;

        function initMarqueeAnimation() {
            var stories = container.querySelectorAll('.project-story:not(.story-clone)');
            if (!stories.length) return;

            var containerStyles = window.getComputedStyle(container);
            var gap = parseFloat(containerStyles.gap) || 24;
            var firstStory = stories[0];
            var lastStory = stories[stories.length - 1];
            var setWidth = (lastStory.offsetLeft + lastStory.offsetWidth + gap) - firstStory.offsetLeft;

            container.style.setProperty('--marquee-distance', setWidth + 'px');
            container.setAttribute('aria-label', 'Наші клієнти — автоматична демонстрація');
            container.setAttribute('role', 'marquee');

            if ('IntersectionObserver' in window) {
                var observer = new IntersectionObserver(function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) {
                            requestAnimationFrame(function () {
                                container.classList.add('marquee-active');
                            });
                            observer.unobserve(container);
                        }
                    });
                }, { threshold: 0.1, rootMargin: '50px' });
                observer.observe(container);
            } else {
                requestAnimationFrame(function () {
                    container.classList.add('marquee-active');
                });
            }
        }

        waitForImages(container).then(initMarqueeAnimation).catch(function () {
            setTimeout(initMarqueeAnimation, 500);
        });
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
                btn.textContent = isOpen ? 'Читати далі' : 'Згорнути';
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

    function init() {
        initReveal();
        initPkgStagger();
        initPkgReadMore();
        initSvobodaReveal();
        initHeroSequence();
        initCalcPkgLinks();
        initClientsMarquee();
        initPkgCompareTabs();
        if (typeof window.initAdminMock === 'function') {
            window.initAdminMock();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
