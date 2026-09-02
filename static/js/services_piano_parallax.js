/**
 * Services piano — IO visibility gate + play/pause.
 * Adds .is-piano-visible to #svc-piano when in viewport → reveals video.
 * Hero and piano use different videos; opacity controls which is visible.
 */
(function () {
    'use strict';

    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function getSection() {
        return document.getElementById('svc-piano');
    }

    function getActiveVideo(section) {
        var isMobile = window.matchMedia('(max-width: 767px)').matches;
        return section.querySelector(isMobile ? '.mobile-video' : '.desktop-video');
    }

    function getVideos(section) {
        return section.querySelectorAll('.video-background');
    }

    function pauseAll(section) {
        getVideos(section).forEach(function (v) {
            if (!v.paused) { v.pause(); }
        });
    }

    function resumeActive(section) {
        if (reducedMotion || document.hidden) { return; }
        var active = getActiveVideo(section);
        if (!active) { return; }

        getVideos(section).forEach(function (v) {
            if (v !== active && !v.paused) { v.pause(); }
        });

        if (active.readyState < 2) {
            active.preload = 'auto';
            active.load();
        }

        var p = active.play();
        if (p && typeof p.catch === 'function') { p.catch(function () {}); }
    }

    function show(section) {
        section.classList.add('is-piano-visible');
        resumeActive(section);
    }

    function hide(section) {
        section.classList.remove('is-piano-visible');
        pauseAll(section);
    }

    function init() {
        var section = getSection();
        if (!section) { return; }

        if (!('IntersectionObserver' in window)) {
            show(section);
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    show(section);
                } else {
                    hide(section);
                }
            });
        }, { threshold: 0, rootMargin: '0px' });

        observer.observe(section);

        document.addEventListener('visibilitychange', function () {
            if (document.hidden) { hide(section); }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
