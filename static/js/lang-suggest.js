/**
 * Language Suggest Toast
 * Non-blocking notification at the top of the page on RU pages.
 *
 * Behaviour:
 * - Appears gently ~1.5s after page load (slide + fade in).
 * - Does NOT block scroll — page is fully usable.
 * - Auto-dismisses on first user scroll (>40px) or after 12s of inactivity.
 * - "Так" → switch to Ukrainian (or navigate to data-uk-url).
 * - "Ні"  → dismiss and remember choice (unless data-always="true").
 *
 * Data attributes:
 *   data-always="true"  — show on every visit (skip localStorage gate).
 *   data-uk-url="/..."  — direct URL to the UA version (preferred over set_language).
 */
(function () {
    'use strict';

    const STORAGE_KEY = 'lang_suggest_seen';
    const SHOW_DELAY_MS = 1500;
    const AUTO_HIDE_MS = 12000;
    const SCROLL_THRESHOLD_PX = 40;

    function getCSRFToken() {
        if (window.PrometeyUtils && typeof window.PrometeyUtils.getCSRFToken === 'function') {
            return window.PrometeyUtils.getCSRFToken();
        }
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.getAttribute('content') || '';
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1].trim() : '';
    }

    function switchToUkrainian(directUrl) {
        if (directUrl) {
            window.location.href = directUrl;
            return;
        }

        let nextUrl = window.location.pathname + window.location.search;
        nextUrl = nextUrl.replace(/^\/ru\//, '/');

        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/i18n/set_language/';

        const fields = {
            csrfmiddlewaretoken: getCSRFToken(),
            language: 'uk',
            next: nextUrl,
        };

        Object.entries(fields).forEach(([name, value]) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            input.value = value;
            form.appendChild(input);
        });

        document.body.appendChild(form);
        form.submit();
    }

    function init() {
        const toast = document.getElementById('lang-suggest');
        if (!toast) return;

        const isAlways = toast.dataset.always === 'true';
        const directUrl = toast.dataset.ukUrl || null;

        if (!isAlways) {
            try {
                if (localStorage.getItem(STORAGE_KEY)) return;
            } catch (_) { /* private browsing may block */ }
        }

        let dismissed = false;
        let initialScrollY = 0;
        let autoHideTimer = null;

        function persistDismiss() {
            if (isAlways) return;
            try {
                localStorage.setItem(STORAGE_KEY, '1');
            } catch (_) { /* ignore */ }
        }

        function hide(persist) {
            if (dismissed) return;
            dismissed = true;
            toast.classList.remove('is-visible');
            window.removeEventListener('scroll', onScroll, { passive: true });
            if (autoHideTimer) {
                clearTimeout(autoHideTimer);
                autoHideTimer = null;
            }
            // After the CSS transition completes, fully detach from layout.
            setTimeout(() => { toast.hidden = true; }, 320);
            if (persist) persistDismiss();
        }

        function onScroll() {
            const delta = Math.abs(window.scrollY - initialScrollY);
            if (delta > SCROLL_THRESHOLD_PX) {
                // User started scrolling — gently dismiss without persisting,
                // so we can still show it next time if they didn't decide.
                hide(false);
            }
        }

        function show() {
            initialScrollY = window.scrollY || 0;
            toast.hidden = false;
            // Force a reflow so the transition kicks in from the initial state.
            void toast.offsetWidth;
            toast.classList.add('is-visible');

            window.addEventListener('scroll', onScroll, { passive: true });
            autoHideTimer = setTimeout(() => hide(false), AUTO_HIDE_MS);
        }

        const yesBtn = document.getElementById('lang-suggest-yes');
        const noBtn = document.getElementById('lang-suggest-close');

        if (yesBtn) {
            yesBtn.addEventListener('click', () => {
                persistDismiss();
                switchToUkrainian(directUrl);
            });
        }

        if (noBtn) {
            noBtn.addEventListener('click', () => hide(true));
        }

        setTimeout(show, SHOW_DELAY_MS);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
