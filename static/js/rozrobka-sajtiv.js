/* Soft currency + portfolio carousel for /rozrobka-sajtiv/.
   Fixed Soft lock, not a live FX feed. Andriy can replace the USD figures.
   Rate used to round them: 1 € ≈ 1.08 USD.
   Landings 250 € → 270 $, corporate 500 € → 540 $, shops 800 € → 865 $
   (800 × 1.08 = 864, rounded to 865). */
(function () {
    var root = document.getElementById('plRsRoot');
    if (!root) return;

    var storageKey = 'pl-rs-currency';
    var buttons = root.querySelectorAll('[data-currency]');

    function apply(code) {
        var usd = code === 'usd';
        root.querySelectorAll('[data-pl-rs-amount]').forEach(function (el) {
            el.textContent = usd ? el.getAttribute('data-usd') : el.getAttribute('data-eur');
        });
        root.querySelectorAll('[data-pl-rs-float]').forEach(function (el) {
            el.textContent = usd ? el.getAttribute('data-usd') : el.getAttribute('data-eur');
        });
        root.querySelectorAll('[data-pl-rs-sign]').forEach(function (el) {
            el.textContent = usd ? '$' : '€';
        });
        buttons.forEach(function (btn) {
            var on = btn.getAttribute('data-currency') === (usd ? 'usd' : 'eur');
            btn.setAttribute('aria-pressed', on ? 'true' : 'false');
            btn.classList.toggle('is-on', on);
        });
        try {
            sessionStorage.setItem(storageKey, usd ? 'usd' : 'eur');
        } catch (err) {
            /* private mode */
        }
    }

    buttons.forEach(function (btn, index) {
        btn.addEventListener('click', function () {
            apply(btn.getAttribute('data-currency'));
        });
        btn.addEventListener('keydown', function (event) {
            var next = null;
            if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
                next = (index + 1) % buttons.length;
            } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
                next = (index - 1 + buttons.length) % buttons.length;
            } else if (event.key === 'Home') {
                next = 0;
            } else if (event.key === 'End') {
                next = buttons.length - 1;
            }
            if (next === null) return;
            event.preventDefault();
            buttons[next].focus();
            apply(buttons[next].getAttribute('data-currency'));
        });
    });

    var saved = 'eur';
    try {
        saved = sessionStorage.getItem(storageKey) || 'eur';
    } catch (err) {
        saved = 'eur';
    }
    if (saved === 'usd') apply('usd');

    /* Portfolio UPPER carousel (Figma 34:4051) */
    var section = root.querySelector('[data-pl-rs-portfolio]');
    if (!section) return;
    var track = section.querySelector('[data-pl-rs-track]');
    var prev = section.querySelector('[data-pl-rs-prev]');
    var next = section.querySelector('[data-pl-rs-next]');
    if (!track || !prev || !next) return;

    function cardStep() {
        var card = track.querySelector('.pl-rs__work-card');
        if (!card) return 378;
        var styles = window.getComputedStyle(track);
        var gap = parseFloat(styles.columnGap || styles.gap || '20') || 20;
        return card.getBoundingClientRect().width + gap;
    }

    function scrollByDir(dir) {
        track.scrollBy({ left: dir * cardStep(), behavior: 'smooth' });
    }

    prev.addEventListener('click', function () { scrollByDir(-1); });
    next.addEventListener('click', function () { scrollByDir(1); });
})();
