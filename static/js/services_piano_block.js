(function () {
    'use strict';

    var TOUCH_MQ = '(hover: none), (pointer: coarse)';
    var STAGGER_MS = 100;

    function prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    function isTouchMode() {
        return window.matchMedia(TOUCH_MQ).matches;
    }

    function getSection(root) {
        if (!root) {
            return null;
        }
        if (root.id === 'svc-piano') {
            return root;
        }
        return root.querySelector('#svc-piano');
    }

    function setUnitFlipped(unit, flipped) {
        var key = unit.querySelector('.svc-piano__key:not(.svc-piano__key--back)');
        var backFace = unit.querySelector('.svc-piano__mob-face--back');
        var backKey = unit.querySelector('.svc-piano__key--back');

        unit.classList.toggle('is-flipped', flipped);

        if (key) {
            key.setAttribute('aria-expanded', flipped ? 'true' : 'false');
        }
        if (backFace) {
            backFace.setAttribute('aria-hidden', flipped ? 'false' : 'true');
        }
        if (backKey) {
            backKey.setAttribute('tabindex', flipped ? '0' : '-1');
        }
    }

    function resetAllFlipped(units) {
        units.forEach(function (unit) {
            setUnitFlipped(unit, false);
        });
    }

    function createFlipApi(section) {
        return {
            setUnitFlipped: setUnitFlipped,
            isMobilePianoLayout: isMobilePianoLayout,
            prefersReducedMotion: prefersReducedMotion,
            getUnits: function () {
                return section.querySelectorAll('.svc-piano__unit');
            }
        };
    }

    function initMobileFlip(section, scrollCtrl) {
        var units = section.querySelectorAll('.svc-piano__unit');
        if (!units.length) {
            return null;
        }

        function bindFlipHandlers() {
            units.forEach(function (unit) {
                var frontFace = unit.querySelector('.svc-piano__mob-face--front');
                var backKey = unit.querySelector('.svc-piano__key--back');

                if (!frontFace || frontFace.dataset.mobFlipBound === '1') {
                    return;
                }

                frontFace.dataset.mobFlipBound = '1';

                function toggleFlip(event) {
                    if (!isMobilePianoLayout()) {
                        return;
                    }

                    event.preventDefault();
                    event.stopPropagation();

                    var willFlip = !unit.classList.contains('is-flipped');
                    setUnitFlipped(unit, willFlip);

                    if (scrollCtrl && scrollCtrl.lockManualFlip) {
                        scrollCtrl.lockManualFlip(unit);
                    }
                }

                frontFace.addEventListener('click', toggleFlip);

                if (backKey) {
                    backKey.addEventListener('click', toggleFlip);
                }
            });
        }

        function onResize() {
            if (!isMobilePianoLayout() && scrollCtrl && scrollCtrl.resetAllFlips) {
                scrollCtrl.resetAllFlips();
            }
        }

        bindFlipHandlers();
        window.addEventListener('resize', onResize);

        return function destroy() {
            window.removeEventListener('resize', onResize);
            resetAllFlipped(units);
        };
    }

    function setUnitOpen(unit, open) {
        var key = unit.querySelector('.svc-piano__key');
        var rise = unit.querySelector('.svc-piano__rise');
        var desc = unit.querySelector('.svc-piano__key-desc');
        var foot = unit.querySelector('.svc-piano__key-foot');

        if (!key || !rise) {
            return;
        }

        unit.classList.toggle('is-active', open);
        key.setAttribute('aria-expanded', open ? 'true' : 'false');
        rise.setAttribute('aria-hidden', open ? 'false' : 'true');

        if (desc) {
            desc.setAttribute('aria-hidden', open ? 'false' : 'true');
        }
        if (foot) {
            foot.setAttribute('aria-hidden', open ? 'false' : 'true');
        }
    }

    function initHoverA11y(section) {
        if (isTouchMode()) {
            return null;
        }

        var units = section.querySelectorAll('.svc-piano__unit');

        units.forEach(function (unit) {
            unit.addEventListener('mouseenter', function () {
                setUnitOpen(unit, true);
            });
            unit.addEventListener('mouseleave', function () {
                setUnitOpen(unit, false);
            });
        });

        return null;
    }

    function closeAllUnits(units, except) {
        units.forEach(function (unit) {
            if (unit !== except) {
                setUnitOpen(unit, false);
            }
        });
    }

    function isMobilePianoLayout() {
        return window.matchMedia('(max-width: 767px)').matches;
    }

    function initScrollReveal(section) {
        var units = section.querySelectorAll('.svc-piano__unit');
        if (!units.length) {
            return;
        }

        if (isMobilePianoLayout() || prefersReducedMotion() || !('IntersectionObserver' in window)) {
            units.forEach(function (unit) {
                unit.classList.add('is-visible');
            });
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) {
                    return;
                }

                var index = Array.prototype.indexOf.call(units, entry.target);
                window.setTimeout(function () {
                    entry.target.classList.add('is-visible');
                }, Math.max(0, index) * STAGGER_MS);

                observer.unobserve(entry.target);
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -8% 0px'
        });

        units.forEach(function (unit) {
            var rect = unit.getBoundingClientRect();
            var vh = window.innerHeight || document.documentElement.clientHeight;

            if (rect.top < vh * 0.92 && rect.bottom > 0) {
                var idx = Array.prototype.indexOf.call(units, unit);
                window.setTimeout(function () {
                    unit.classList.add('is-visible');
                }, idx * STAGGER_MS);
            } else {
                observer.observe(unit);
            }
        });
    }

    function initTouchToggle(section) {
        if (isMobilePianoLayout()) {
            return null;
        }

        var units = section.querySelectorAll('.svc-piano__unit');
        if (!units.length) {
            return null;
        }

        function onDocumentPointerDown(event) {
            if (event.target.closest('.svc-piano__detail')) {
                return;
            }
            if (!section.contains(event.target)) {
                closeAllUnits(units, null);
            }
        }

        units.forEach(function (unit) {
            var key = unit.querySelector('.svc-piano__key');
            if (!key) {
                return;
            }

            key.addEventListener('click', function (event) {
                if (!isTouchMode()) {
                    return;
                }

                event.preventDefault();
                var willOpen = !unit.classList.contains('is-active');
                closeAllUnits(units, willOpen ? unit : null);
                setUnitOpen(unit, willOpen);
            });
        });

        document.addEventListener('pointerdown', onDocumentPointerDown);

        return function destroy() {
            document.removeEventListener('pointerdown', onDocumentPointerDown);
        };
    }

    function initServiceModals(section) {
        var savedScrollPosition = 0;

        function lockScroll() {
            savedScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
            document.body.style.top = '-' + savedScrollPosition + 'px';
            document.body.classList.add('modal-open', 'service-modal-open');
            document.documentElement.style.backgroundColor = '#000';
        }

        function unlockScroll() {
            document.body.style.top = '';
            document.body.classList.remove('modal-open', 'service-modal-open');
            document.documentElement.style.backgroundColor = '';
            window.scrollTo({
                top: savedScrollPosition,
                behavior: 'auto'
            });
        }

        function openModal(serviceType) {
            var modal = document.getElementById('service-' + serviceType + '-modal');
            if (!modal) {
                return;
            }

            lockScroll();
            modal.classList.add('active');
            modal.setAttribute('aria-hidden', 'false');

            function closeModal() {
                modal.classList.remove('active');
                modal.setAttribute('aria-hidden', 'true');
                unlockScroll();
            }

            var closeBtn = modal.querySelector('.modal-close');
            var backdrop = modal.querySelector('.modal-backdrop');

            if (closeBtn) {
                closeBtn.onclick = closeModal;
            }
            if (backdrop) {
                backdrop.onclick = closeModal;
            }

            function escHandler(event) {
                if (event.key === 'Escape') {
                    closeModal();
                    document.removeEventListener('keydown', escHandler);
                }
            }

            document.addEventListener('keydown', escHandler);
        }

        section.querySelectorAll('.service-detail-btn').forEach(function (btn) {
            btn.addEventListener('click', function (event) {
                event.stopPropagation();
                event.preventDefault();
                var serviceType = btn.getAttribute('data-service');
                if (!serviceType) {
                    var host = btn.closest('[data-service]');
                    serviceType = host ? host.getAttribute('data-service') : '';
                }
                if (serviceType) {
                    openModal(serviceType);
                }
            });

            btn.addEventListener('pointerdown', function (event) {
                event.stopPropagation();
            });
        });
    }

    function initServicesPianoBlock(root) {
        var section = getSection(root);
        if (!section || section.dataset.svcPianoInit === '1') {
            return null;
        }

        section.dataset.svcPianoInit = '1';

        var flipApi = createFlipApi(section);
        var scrollCtrl = typeof window.initServicesPianoMobScroll === 'function'
            ? window.initServicesPianoMobScroll(section, flipApi)
            : null;

        initScrollReveal(section);
        initHoverA11y(section);
        var destroyTouch = initTouchToggle(section);
        var destroyMobileFlip = initMobileFlip(section, scrollCtrl);
        initServiceModals(section);

        section._svcPianoDestroy = function () {
            if (destroyTouch) {
                destroyTouch();
            }
            if (destroyMobileFlip) {
                destroyMobileFlip();
            }
            if (scrollCtrl && scrollCtrl.destroy) {
                scrollCtrl.destroy();
            }
            section.dataset.svcPianoInit = '';
        };

        return section;
    }

    function boot() {
        initServicesPianoBlock(document);
    }

    if (document.readyState === 'complete') {
        boot();
    } else {
        document.addEventListener('DOMContentLoaded', boot);
    }

    window.initServicesPianoBlock = initServicesPianoBlock;
}());
