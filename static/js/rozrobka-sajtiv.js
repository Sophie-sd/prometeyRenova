/* Soft portfolio carousel for /rozrobka-sajtiv/. Currency is HTMX + pl_currency. */
(function () {
    var root = document.getElementById('plRsRoot');
    if (!root) return;

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
