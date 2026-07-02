(function () {
    'use strict';

    var root = document.getElementById('plCorpRoot');
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
            el.style.transform = 'translateY(26px)';
            el.style.transition = 'opacity .7s cubic-bezier(.2,.7,.2,1), transform .7s cubic-bezier(.2,.7,.2,1)';
        });

        function reveal(el) {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
            window.setTimeout(function () {
                el.style.removeProperty('transform');
                el.style.removeProperty('opacity');
                el.style.removeProperty('transition');
            }, 720);
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

    function initHeroMockup() {
        var mockup = root.querySelector('[data-hero-mockup]');
        if (!mockup) return;

        var panels = mockup.querySelectorAll('[data-hero-panel]');
        var tabBtns = mockup.querySelectorAll('[data-hero-tab]');
        var backBtns = mockup.querySelectorAll('[data-hero-back]');
        var chipTriggers = root.querySelectorAll('[data-hero-tab-trigger]');
        var speedBar = mockup.querySelector('[data-hero-speed-bar]');
        var currentPanel = 'main';

        function showPanel(id) {
            currentPanel = id;
            panels.forEach(function (panel) {
                var active = panel.getAttribute('data-hero-panel') === id;
                panel.classList.toggle('is-active', active);
                panel.setAttribute('aria-hidden', active ? 'false' : 'true');
            });

            tabBtns.forEach(function (btn) {
                var tab = btn.getAttribute('data-hero-tab');
                var selected = tab === id;
                btn.classList.toggle('is-active', selected);
                btn.setAttribute('aria-selected', selected ? 'true' : 'false');
            });

            if (id === 'speed' && speedBar) {
                speedBar.classList.remove('is-filled');
                requestAnimationFrame(function () {
                    speedBar.classList.add('is-filled');
                });
            }
        }

        tabBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                showPanel(btn.getAttribute('data-hero-tab'));
            });
        });

        backBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                showPanel('main');
            });
        });

        chipTriggers.forEach(function (chip) {
            function activate() {
                showPanel(chip.getAttribute('data-hero-tab-trigger'));
            }
            chip.addEventListener('click', activate);
            chip.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    activate();
                }
            });
        });

        return {
            showPanel: showPanel,
            getCurrentPanel: function () { return currentPanel; },
            isTabPanel: function (id) {
                return id === 'economy' || id === 'tech' || id === 'scale';
            }
        };
    }

    function initHeroSequence() {
        var stage = root.querySelector('[data-hero-stage]');
        if (!stage) return;

        var mockupApi = initHeroMockup();
        var mockup = root.querySelector('[data-hero-mockup]');
        var win = root.querySelector('[data-hero-win]');
        var rings = root.querySelectorAll('[data-hero-ring]');
        var chips = root.querySelectorAll('[data-hero-chip]');
        var winLines = root.querySelectorAll('[data-hero-win-line]');
        var cardsWrap = root.querySelector('[data-hero-win-cards]');
        var cards = cardsWrap ? cardsWrap.querySelectorAll('[data-hero-tab]') : [];
        var cardCycleTimer = null;
        var cardCycleIndex = 0;
        var cardCyclePaused = false;
        var CARD_CYCLE_MS = 2500;
        var tabIds = ['economy', 'tech', 'scale'];

        function showWinLines() {
            winLines.forEach(function (line) {
                line.classList.add('is-visible');
            });
        }

        function staggerWinLines() {
            if (!winLines.length) return;
            winLines.forEach(function (line, i) {
                setTimeout(function () {
                    line.classList.add('is-visible');
                }, 300 + i * 120);
            });
        }

        function setActiveCard(index) {
            if (!cards.length || !mockupApi) return;
            var tabId = tabIds[index];
            if (!tabId) return;
            cardCycleIndex = index;
            mockupApi.showPanel(tabId);
            cards.forEach(function (card, i) {
                var active = i === index;
                card.classList.toggle('is-active', active);
                card.setAttribute('aria-selected', active ? 'true' : 'false');
            });
        }

        function stopCardCycle() {
            if (!cardCycleTimer) return;
            clearInterval(cardCycleTimer);
            cardCycleTimer = null;
        }

        function tickCardCycle() {
            if (cardCyclePaused || !cards.length) return;
            cardCycleIndex = (cardCycleIndex + 1) % cards.length;
            setActiveCard(cardCycleIndex);
        }

        function startCardCycle() {
            if (!cards.length || reduceMotion || !mockupApi) return;
            stopCardCycle();
            setActiveCard(0);
            cardCycleTimer = setInterval(tickCardCycle, CARD_CYCLE_MS);
        }

        function restartCardCycle() {
            if (!cards.length || reduceMotion || !mockupApi) return;
            stopCardCycle();
            cardCycleTimer = setInterval(tickCardCycle, CARD_CYCLE_MS);
        }

        if (cardsWrap) {
            cardsWrap.addEventListener('mouseenter', function () {
                cardCyclePaused = true;
            });
            cardsWrap.addEventListener('mouseleave', function () {
                cardCyclePaused = false;
            });
            cardsWrap.addEventListener('focusin', function () {
                cardCyclePaused = true;
            });
            cardsWrap.addEventListener('focusout', function () {
                cardCyclePaused = false;
            });
        }

        cards.forEach(function (card, index) {
            card.addEventListener('click', function () {
                cardCycleIndex = index;
                setActiveCard(index);
                restartCardCycle();
            });
        });

        if (mockup) {
            mockup.addEventListener('click', function (e) {
                if (e.target.closest('[data-hero-back]')) {
                    cardCyclePaused = false;
                }
            });
        }

        root.querySelectorAll('[data-hero-tab-trigger]').forEach(function (chip) {
            chip.addEventListener('click', function () {
                var target = chip.getAttribute('data-hero-tab-trigger');
                cardCyclePaused = target === 'speed';
            });
        });

        function finish() {
            if (win) {
                win.style.opacity = '1';
                win.style.transform = 'none';
            }
            rings.forEach(function (r) {
                r.style.strokeDashoffset = '0';
            });
            chips.forEach(function (c) {
                c.style.opacity = '1';
                c.style.removeProperty('transform');
            });
            showWinLines();
            if (cards.length && mockupApi) {
                mockupApi.showPanel('main');
            }
        }

        if (reduceMotion) {
            finish();
            startCardCycle();
            return;
        }

        if (win) {
            win.style.opacity = '0';
            win.style.transform = 'translateY(20px) scale(.98)';
            win.style.transition = 'opacity .7s cubic-bezier(.2,.7,.2,1), transform .7s cubic-bezier(.2,.7,.2,1)';
        }

        chips.forEach(function (c) {
            c.style.opacity = '0';
            c.style.transform = 'translateY(12px) scale(.96)';
            c.style.transition = 'opacity .5s ease, transform .5s cubic-bezier(.2,.7,.2,1)';
        });

        requestAnimationFrame(function () {
            setTimeout(function () {
                if (win) {
                    win.style.opacity = '1';
                    win.style.transform = 'none';
                }
                staggerWinLines();
            }, 140);
            setTimeout(function () {
                rings.forEach(function (r) {
                    r.style.strokeDashoffset = '0';
                });
            }, 700);
            setTimeout(function () {
                if (chips[0]) {
                    chips[0].style.opacity = '1';
                    chips[0].style.removeProperty('transform');
                }
            }, 1300);
            setTimeout(function () {
                if (chips[1]) {
                    chips[1].style.opacity = '1';
                    chips[1].style.removeProperty('transform');
                }
                startCardCycle();
            }, 1650);
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
        var container = root.querySelector('.pl-corp__clients-stories-container');
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

    function initScaleDiagram() {
        var diagram = root.querySelector('.pl-corp__scale-diagram');
        if (!diagram) return;

        function activate() {
            if (diagram.classList.contains('is-live')) return;
            diagram.classList.add('is-live');
        }

        if (reduceMotion) {
            activate();
            return;
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (ents) {
                ents.forEach(function (en) {
                    if (en.isIntersecting) {
                        activate();
                        io.unobserve(diagram);
                    }
                });
            }, { threshold: 0.2, rootMargin: '0px 0px -8% 0px' });

            io.observe(diagram);

            requestAnimationFrame(function () {
                var vh = window.innerHeight || 800;
                var rect = diagram.getBoundingClientRect();
                if (rect.top < vh * 0.92) {
                    activate();
                    io.unobserve(diagram);
                }
            });
        } else {
            activate();
        }
    }

    function init() {
        initReveal();
        initHeroSequence();
        initClientsMarquee();
        initScaleDiagram();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
