(function (global) {
    'use strict';

    var FLIP_TRIGGER_RATIO = 0.55;

    function computeShouldFlip(unit, vh) {
        var rect = unit.getBoundingClientRect();
        var center = rect.top + rect.height * 0.5;
        var trigger = vh * FLIP_TRIGGER_RATIO;

        return center < trigger && rect.bottom > 0 && rect.top < vh;
    }

    function createRafScheduler(fn) {
        var rafId = 0;

        return {
            schedule: function schedule() {
                if (rafId) {
                    return;
                }

                rafId = global.requestAnimationFrame(function () {
                    rafId = 0;
                    fn();
                });
            },
            cancel: function cancel() {
                if (rafId) {
                    global.cancelAnimationFrame(rafId);
                    rafId = 0;
                }
            }
        };
    }

    function initServicesPianoMobScroll(section, api) {
        if (!section || !api) {
            return null;
        }

        var units = section.querySelectorAll('.svc-piano__unit');
        if (!units.length) {
            return null;
        }

        function resetAllFlips() {
            units.forEach(function (unit) {
                delete unit.dataset.manualFlipLock;
                api.setUnitFlipped(unit, false);
            });
        }

        function syncScrollFlips() {
            if (!api.isMobilePianoLayout()) {
                return;
            }

            var vh = global.innerHeight || document.documentElement.clientHeight;

            units.forEach(function (unit) {
                if (unit.dataset.manualFlipLock === '1') {
                    return;
                }

                var next = computeShouldFlip(unit, vh);
                var isFlipped = unit.classList.contains('is-flipped');

                if (next !== isFlipped) {
                    api.setUnitFlipped(unit, next);
                }
            });
        }

        function onResize() {
            if (!api.isMobilePianoLayout()) {
                resetAllFlips();
                return;
            }

            syncScrollFlips();
        }

        var scheduler = createRafScheduler(syncScrollFlips);

        function onScroll() {
            scheduler.schedule();
        }

        function releaseManualLock(unit) {
            delete unit.dataset.manualFlipLock;
            syncScrollFlips();
        }

        function lockManualFlip(unit) {
            unit.dataset.manualFlipLock = '1';
            global.requestAnimationFrame(function () {
                global.requestAnimationFrame(function () {
                    releaseManualLock(unit);
                });
            });
        }

        global.addEventListener('scroll', onScroll, { passive: true });
        document.addEventListener('scroll', onScroll, { passive: true });
        global.addEventListener('resize', onResize);

        if (api.prefersReducedMotion()) {
            syncScrollFlips();
        } else {
            scheduler.schedule();
        }

        return {
            syncScrollFlips: syncScrollFlips,
            lockManualFlip: lockManualFlip,
            resetAllFlips: resetAllFlips,
            destroy: function destroy() {
                global.removeEventListener('scroll', onScroll);
                document.removeEventListener('scroll', onScroll);
                global.removeEventListener('resize', onResize);
                scheduler.cancel();
                resetAllFlips();
            }
        };
    }

    global.initServicesPianoMobScroll = initServicesPianoMobScroll;
}(typeof window !== 'undefined' ? window : this));
