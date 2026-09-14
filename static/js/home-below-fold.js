/**
 * Lazy-load below-fold homepage scripts (process + piano) in fixed order.
 * Script URLs come from #home-below-fold[data-scripts] (JSON array).
 * Does not touch home-bundle / video / CookieYes / GTM.
 */
(function () {
    'use strict';

    var LOADED = false;

    function readScripts() {
        var el = document.getElementById('home-below-fold-urls');
        if (!el) {
            return [];
        }
        try {
            var list = JSON.parse(el.textContent);
            return Array.isArray(list) ? list.filter(Boolean) : [];
        } catch (err) {
            return [];
        }
    }

    function loadScript(src) {
        return new Promise(function (resolve, reject) {
            if (document.querySelector('script[data-home-below="' + src + '"]')) {
                resolve();
                return;
            }
            var s = document.createElement('script');
            s.src = src;
            s.defer = true;
            s.setAttribute('data-home-below', src);
            var host = document.getElementById('home-below-fold');
            var nonce = (host && host.getAttribute('data-nonce')) || '';
            if (nonce) {
                s.setAttribute('nonce', nonce);
            }
            s.onload = function () { resolve(); };
            s.onerror = function () { reject(new Error('Failed to load ' + src)); };
            document.body.appendChild(s);
        });
    }

    function loadAll(scripts) {
        if (LOADED) {
            return;
        }
        LOADED = true;
        var chain = Promise.resolve();
        scripts.forEach(function (src) {
            chain = chain.then(function () { return loadScript(src); });
        });
        chain.catch(function () { /* keep page usable if a file 404s */ });
    }

    function armIdle(scripts) {
        if (typeof requestIdleCallback === 'function') {
            requestIdleCallback(function () { loadAll(scripts); }, { timeout: 4000 });
        } else {
            setTimeout(function () { loadAll(scripts); }, 2500);
        }
    }

    function armObserver(scripts) {
        if (!scripts.length) {
            return;
        }

        var targets = [
            document.getElementById('home-redesign'),
            document.getElementById('svc-piano')
        ].filter(Boolean);

        if (!targets.length || !('IntersectionObserver' in window)) {
            armIdle(scripts);
            return;
        }

        var obs = new IntersectionObserver(function (entries) {
            for (var i = 0; i < entries.length; i++) {
                if (entries[i].isIntersecting) {
                    obs.disconnect();
                    loadAll(scripts);
                    return;
                }
            }
        }, { rootMargin: '400px 0px', threshold: 0 });

        targets.forEach(function (el) { obs.observe(el); });

        window.addEventListener('load', function () {
            armIdle(scripts);
        }, { once: true });
    }

    function start() {
        armObserver(readScripts());
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start, { once: true });
    } else {
        start();
    }
}());
