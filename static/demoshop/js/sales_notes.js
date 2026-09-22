/* Sales-шар: модалка, auto-open 5s, hide в localStorage. Без onclick. */

function salesOffKey(shopId) {
    return `ds-sales-off:${shopId}`;
}

function salesSeenKey(shopId, page) {
    return `ds-sales-seen:${shopId}:${page || 'page'}`;
}

function isFormField(el) {
    if (!el || el === document.body || el === document.documentElement) return false;
    const tag = (el.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select') return true;
    return Boolean(el.isContentEditable);
}

function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function initSalesChrome() {
    const root = document.querySelector('[data-ds-sales-chrome]');
    if (!root || root.dataset.bound === '1') return;
    root.dataset.bound = '1';

    const shopId = root.getAttribute('data-shop-id') || document.body.getAttribute('data-shop-id') || '0';
    const page = root.getAttribute('data-ds-sales-page') || '';
    const panel = root.querySelector('.ds-sales-panel');
    const backdrop = root.querySelector('.ds-sales-backdrop');
    const openBtn = root.querySelector('[data-ds-sales-open]');
    const hideBtn = root.querySelector('[data-ds-sales-hide]');
    const showBtn = root.querySelector('[data-ds-sales-show]');
    const closeBtns = root.querySelectorAll('[data-ds-sales-close]');
    let autoTimer = 0;

    function isOff() {
        try {
            return localStorage.getItem(salesOffKey(shopId)) === '1';
        } catch (err) {
            return false;
        }
    }

    function isSeen() {
        try {
            return sessionStorage.getItem(salesSeenKey(shopId, page)) === '1';
        } catch (err) {
            return false;
        }
    }

    function markSeen() {
        try {
            sessionStorage.setItem(salesSeenKey(shopId, page), '1');
        } catch (err) { /* private mode */ }
    }

    function clearAutoTimer() {
        if (autoTimer) {
            window.clearTimeout(autoTimer);
            autoTimer = 0;
        }
    }

    function applyHiddenState() {
        const off = isOff();
        document.body.classList.toggle('ds-sales-off', off);
        if (hideBtn) hideBtn.hidden = off;
        if (showBtn) showBtn.hidden = !off;
    }

    function setOpen(open) {
        if (!panel) return;
        panel.hidden = !open;
        if (backdrop) backdrop.hidden = !open;
        if (openBtn) openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
        document.body.classList.toggle('ds-sales-panel-open', open);
        if (open) {
            markSeen();
            clearAutoTimer();
        }
    }

    function delayMs() {
        return prefersReducedMotion() ? 0 : 5000;
    }

    function attemptAutoOpen() {
        if (isOff() || isSeen() || !panel) return;
        const active = document.activeElement;
        if (isFormField(active)) {
            active.addEventListener('blur', () => {
                autoTimer = window.setTimeout(attemptAutoOpen, delayMs());
            }, { once: true });
            return;
        }
        setOpen(true);
    }

    function scheduleAutoOpen() {
        if (isOff() || isSeen() || !panel) return;
        autoTimer = window.setTimeout(attemptAutoOpen, delayMs());
    }

    applyHiddenState();
    scheduleAutoOpen();

    openBtn?.addEventListener('click', () => {
        setOpen(panel.hidden);
    });
    closeBtns.forEach((btn) => {
        btn.addEventListener('click', () => setOpen(false));
    });
    hideBtn?.addEventListener('click', () => {
        try {
            localStorage.setItem(salesOffKey(shopId), '1');
        } catch (err) { /* private mode */ }
        applyHiddenState();
        setOpen(false);
        markSeen();
        clearAutoTimer();
    });
    showBtn?.addEventListener('click', () => {
        try {
            localStorage.removeItem(salesOffKey(shopId));
        } catch (err) { /* private mode */ }
        applyHiddenState();
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') setOpen(false);
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSalesChrome);
} else {
    initSalesChrome();
}
