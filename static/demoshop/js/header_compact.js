/* Home: morphing capsule↔ball header (no marquee on home).
   Sentinel after hero + hysteresis. Ball open/close is width/opacity of the
   same capsule — no separate drawer, no body lock. */
(function initHeaderCompact() {
    if (!document.body.classList.contains('ds-body--hero-overlay')) return;

    const header = document.querySelector('.ds-header');
    const sentinel = document.querySelector('[data-ds-compact-sentinel]');
    const burger = document.querySelector('[data-ds-menu-toggle]');
    const capsule = document.querySelector('.ds-header__capsule');
    if (!header || !sentinel || !burger || !capsule) return;

    const COMPACT_ON = 0;
    const COMPACT_OFF = 48;
    const root = document.documentElement;

    let compact = false;
    let menuOpen = false;
    let raf = 0;

    function measureBall() {
        /* Ball diameter must equal the capsule's real rendered height so
           the compact state is a perfect circle, not an oval. */
        const h = Math.round(capsule.getBoundingClientRect().height);
        if (h > 0) {
            root.style.setProperty('--ds-ball', h + 'px');
        }
    }

    function sentinelTop() {
        const top = sentinel.getBoundingClientRect().top;
        const vv = window.visualViewport;
        const offset = vv && typeof vv.offsetTop === 'number' ? vv.offsetTop : 0;
        return top - offset;
    }

    function setMenuOpen(open) {
        if (open === menuOpen) return;
        menuOpen = open;
        header.classList.toggle('is-open', open);
        burger.setAttribute('aria-expanded', open ? 'true' : 'false');
        burger.setAttribute(
            'aria-label',
            burger.getAttribute(open ? 'data-label-close' : 'data-label-open') || ''
        );
    }

    function setCompact(next) {
        if (next === compact) return;
        compact = next;
        header.classList.toggle('is-compact', next);
        if (!next) setMenuOpen(false);
    }

    function syncCompact() {
        const top = sentinelTop();
        if (!compact && top <= COMPACT_ON) setCompact(true);
        else if (compact && top >= COMPACT_OFF) setCompact(false);
        else if (compact && menuOpen) setMenuOpen(false);
    }

    function onScrollTick() {
        raf = 0;
        syncCompact();
    }

    function requestTick() {
        if (raf) return;
        raf = window.requestAnimationFrame(onScrollTick);
    }

    burger.addEventListener('click', (event) => {
        event.preventDefault();
        if (!compact) return;
        setMenuOpen(!menuOpen);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && menuOpen) {
            setMenuOpen(false);
            burger.focus();
        }
    });

    window.addEventListener('scroll', requestTick, { passive: true });
    window.addEventListener('resize', () => {
        measureBall();
        requestTick();
    }, { passive: true });

    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', requestTick);
        window.visualViewport.addEventListener('scroll', requestTick);
    }

    measureBall();
    syncCompact();
})();
