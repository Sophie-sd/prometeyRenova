/**
 * Language Suggest Modal
 * На RU-сторінках показує overlay з пропозицією перейти на українську.
 *
 * data-always="true"  — показувати при кожному візиті (без localStorage-перевірки)
 * data-uk-url="/..."  — пряме посилання на UA-версію (замість /i18n/set_language/)
 */
(function () {
    'use strict';

    const STORAGE_KEY = 'lang_suggest_seen';
    const SHOW_DELAY_MS = 1500;

    function getCSRFToken() {
        if (window.PrometeyUtils?.getCSRFToken) {
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

    function dismiss(modal) {
        const isAlways = modal.dataset.always === 'true';
        if (!isAlways) {
            try {
                localStorage.setItem(STORAGE_KEY, '1');
            } catch (_) { /* private browsing may block */ }
        }
        modal.hidden = true;
    }

    function init() {
        const modal = document.getElementById('lang-suggest');
        if (!modal) return;

        const isAlways = modal.dataset.always === 'true';
        const directUrl = modal.dataset.ukUrl || null;

        if (!isAlways) {
            try {
                if (localStorage.getItem(STORAGE_KEY)) return;
            } catch (_) { /* ignore */ }
        }

        setTimeout(() => {
            modal.hidden = false;
        }, SHOW_DELAY_MS);

        document.getElementById('lang-suggest-yes')?.addEventListener('click', () => {
            switchToUkrainian(directUrl);
        });

        document.getElementById('lang-suggest-close')?.addEventListener('click', () => {
            dismiss(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) dismiss(modal);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
