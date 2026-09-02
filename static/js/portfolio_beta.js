(function () {
    'use strict';

    var track = document.getElementById('beta-carousel-track');
    if (!track) {
        return;
    }

    var slides = Array.prototype.slice.call(
        track.querySelectorAll('.beta-carousel__slide')
    );
    if (!slides.length) {
        return;
    }

    var prevBtn = document.querySelector('.beta-nav-btn[data-dir="prev"]');
    var nextBtn = document.querySelector('.beta-nav-btn[data-dir="next"]');
    var activeIndex = 0;
    var scrollTimer = null;
    var mobileQuery = window.matchMedia('(max-width: 767px)');
    var touchQuery = window.matchMedia('(hover: none)');

    function isMobile() {
        return mobileQuery.matches;
    }

    function closeAllOverlays() {
        track.querySelectorAll('.beta-carousel__overlay.is-visible').forEach(function (overlay) {
            overlay.classList.remove('is-visible');
            overlay.setAttribute('aria-hidden', 'true');
            var learnBtn = overlay.querySelector('.beta-carousel__learn-btn');
            if (learnBtn) {
                learnBtn.setAttribute('tabindex', '-1');
            }
        });
    }

    function openOverlay(overlay) {
        overlay.classList.add('is-visible');
        overlay.setAttribute('aria-hidden', 'false');
        var learnBtn = overlay.querySelector('.beta-carousel__learn-btn');
        if (learnBtn) {
            learnBtn.setAttribute('tabindex', '0');
        }
    }

    track.addEventListener('click', function (e) {
        if (!touchQuery.matches) {
            return;
        }

        if (e.target.closest('.beta-carousel__learn-btn')) {
            return;
        }

        var imageCol = e.target.closest('.beta-carousel__image');
        if (!imageCol) {
            closeAllOverlays();
            return;
        }

        var overlay = imageCol.querySelector('.beta-carousel__overlay');
        if (!overlay) {
            return;
        }

        var isOpen = overlay.classList.contains('is-visible');
        closeAllOverlays();
        if (!isOpen) {
            openOverlay(overlay);
        }
    });

    function getScrollLeftForSlide(index) {
        var slide = slides[index];
        if (!slide) {
            return 0;
        }

        return slide.offsetLeft - parseFloat(getComputedStyle(track).paddingLeft || 0);
    }

    function scrollToSlide(index) {
        var total = slides.length;
        activeIndex = ((index % total) + total) % total;
        track.scrollTo({
            left: getScrollLeftForSlide(activeIndex),
            behavior: 'smooth',
        });
    }

    function getActiveIndexFromScroll() {
        var scrollPos = track.scrollLeft;
        var closest = 0;
        var minDist = Infinity;

        slides.forEach(function (slide, i) {
            var targetLeft = getScrollLeftForSlide(i);
            var dist = Math.abs(scrollPos - targetLeft);
            if (dist < minDist) {
                minDist = dist;
                closest = i;
            }
        });

        return closest;
    }

    function onScrollEnd() {
        activeIndex = getActiveIndexFromScroll();
    }

    track.addEventListener('scroll', function () {
        window.clearTimeout(scrollTimer);
        scrollTimer = window.setTimeout(onScrollEnd, 120);
    }, { passive: true });

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            scrollToSlide(activeIndex - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            scrollToSlide(activeIndex + 1);
        });
    }

    mobileQuery.addEventListener('change', function () {
        window.requestAnimationFrame(function () {
            track.scrollTo({
                left: getScrollLeftForSlide(activeIndex),
                behavior: 'auto',
            });
        });
    });

    window.requestAnimationFrame(function () {
        track.scrollTo({
            left: getScrollLeftForSlide(0),
            behavior: 'auto',
        });
    });
})();
