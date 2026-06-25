(function (global) {
    'use strict';

    var VIEWPORT_PAD = 12;
    var MOBILE_MQ = '(max-width: 767px)';

    function isMobilePopoverDisabled() {
        return window.matchMedia(MOBILE_MQ).matches;
    }

    function initProcessBlockPopovers(host) {
        var section = host;
        if (!section) {
            return null;
        }

        if (section.id !== 'pb-process') {
            section = host.querySelector('#pb-process');
        }

        if (!section) {
            return null;
        }

        var details = section.querySelectorAll('.pb-step__detail');
        if (!details.length) {
            return null;
        }

        var openDetail = null;

        function getPopover(detail) {
            return detail ? detail.querySelector('.pb-step__popover') : null;
        }

        function resetPopoverStyles(popover) {
            if (!popover) {
                return;
            }

            popover.style.removeProperty('--pb-popover-shift');
        }

        function closeDetail(detail, restoreFocus) {
            if (!detail) {
                return;
            }

            var btn = detail.querySelector('.pb-step__detail-btn');
            var popover = getPopover(detail);

            if (!btn || !popover) {
                return;
            }

            popover.classList.remove('is-open', 'pb-step__popover--below');
            popover.setAttribute('aria-hidden', 'true');
            popover.setAttribute('hidden', '');
            btn.setAttribute('aria-expanded', 'false');
            resetPopoverStyles(popover);

            if (openDetail === detail) {
                openDetail = null;
            }

            if (restoreFocus) {
                btn.focus();
            }
        }

        function closeAll(restoreFocus) {
            details.forEach(function (detail) {
                closeDetail(detail, restoreFocus && openDetail === detail);
            });
        }

        function clampHorizontalShift(popover) {
            var rect = popover.getBoundingClientRect();
            var vw = window.innerWidth || document.documentElement.clientWidth;
            var shift = 0;

            if (rect.left < VIEWPORT_PAD) {
                shift = VIEWPORT_PAD - rect.left;
            } else if (rect.right > vw - VIEWPORT_PAD) {
                shift = (vw - VIEWPORT_PAD) - rect.right;
            }

            if (shift !== 0) {
                popover.style.setProperty('--pb-popover-shift', shift + 'px');
            } else {
                popover.style.removeProperty('--pb-popover-shift');
            }
        }

        function updatePopoverPlacement(detail, popover) {
            popover.classList.remove('pb-step__popover--below');
            resetPopoverStyles(popover);

            var rect = popover.getBoundingClientRect();

            if (rect.top < VIEWPORT_PAD) {
                popover.classList.add('pb-step__popover--below');
            }

            clampHorizontalShift(popover);
        }

        function openPopover(detail) {
            if (isMobilePopoverDisabled()) {
                return;
            }

            var btn = detail.querySelector('.pb-step__detail-btn');
            var popover = getPopover(detail);

            if (!btn || !popover) {
                return;
            }

            if (openDetail && openDetail !== detail) {
                closeDetail(openDetail, false);
            }

            popover.removeAttribute('hidden');
            popover.setAttribute('aria-hidden', 'false');
            popover.classList.add('is-open');
            btn.setAttribute('aria-expanded', 'true');
            openDetail = detail;

            requestAnimationFrame(function () {
                updatePopoverPlacement(detail, popover);
                requestAnimationFrame(function () {
                    updatePopoverPlacement(detail, popover);
                });
            });
        }

        function togglePopover(detail) {
            if (isMobilePopoverDisabled()) {
                return;
            }

            var popover = getPopover(detail);

            if (!popover) {
                return;
            }

            if (popover.classList.contains('is-open')) {
                closeDetail(detail, true);
                return;
            }

            openPopover(detail);
        }

        function onDocumentClick(event) {
            if (!openDetail) {
                return;
            }

            var popover = getPopover(openDetail);
            if (openDetail.contains(event.target) || (popover && popover.contains(event.target))) {
                return;
            }

            closeDetail(openDetail, false);
        }

        function onDocumentKeydown(event) {
            if (event.key !== 'Escape' || !openDetail) {
                return;
            }

            closeDetail(openDetail, true);
        }

        function onResize() {
            if (isMobilePopoverDisabled()) {
                closeAll(false);
                return;
            }

            if (!openDetail) {
                return;
            }

            var popover = getPopover(openDetail);
            if (popover) {
                updatePopoverPlacement(openDetail, popover);
            }
        }

        function onMobileChange(event) {
            if (event.matches) {
                closeAll(false);
            }
        }

        var mobileMedia = window.matchMedia(MOBILE_MQ);
        if (mobileMedia.addEventListener) {
            mobileMedia.addEventListener('change', onMobileChange);
        } else if (mobileMedia.addListener) {
            mobileMedia.addListener(onMobileChange);
        }

        details.forEach(function (detail) {
            var btn = detail.querySelector('.pb-step__detail-btn');
            if (!btn) {
                return;
            }

            btn.addEventListener('click', function (event) {
                event.stopPropagation();
                togglePopover(detail);
            });
        });

        document.addEventListener('click', onDocumentClick);
        document.addEventListener('keydown', onDocumentKeydown);
        window.addEventListener('resize', onResize);

        return function destroy() {
            closeAll(false);
            if (mobileMedia.removeEventListener) {
                mobileMedia.removeEventListener('change', onMobileChange);
            } else if (mobileMedia.removeListener) {
                mobileMedia.removeListener(onMobileChange);
            }
            document.removeEventListener('click', onDocumentClick);
            document.removeEventListener('keydown', onDocumentKeydown);
            window.removeEventListener('resize', onResize);
        };
    }

    global.initProcessBlockPopovers = initProcessBlockPopovers;
})(typeof window !== 'undefined' ? window : this);
