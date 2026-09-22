/* Демо-магазин: reveal, about split-reveal, qty, wishlist, drawer, NP checkout, flyout, page-strip */

function setVh() {
    document.documentElement.style.setProperty('--ds-vh', `${window.innerHeight}px`);
}

function initSafariFix() {
    setVh();
    window.addEventListener('resize', setVh, { passive: true });
}

function initReveal(root) {
    const targets = root.querySelectorAll('[data-ds-reveal]:not(.is-in)');
    if (!targets.length) return;
    const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-in');
                io.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    targets.forEach((el) => io.observe(el));
}

function initAboutReveal() {
    const sections = document.querySelectorAll('[data-ds-about]:not([data-done])');
    if (!sections.length) return;
    if (!('IntersectionObserver' in window)) {
        sections.forEach((el) => el.setAttribute('data-done', '1'));
        return;
    }
    const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const media = entry.target;
            const el = media.closest('[data-ds-about]');
            if (!el || el.getAttribute('data-done') === '1') {
                io.unobserve(media);
                return;
            }
            el.classList.add('is-animating');
            el.setAttribute('data-done', '1');
            const clearAnimating = () => {
                el.classList.remove('is-animating');
                media.removeEventListener('transitionend', clearAnimating);
            };
            media.addEventListener('transitionend', clearAnimating);
            io.unobserve(media);
        });
    }, { threshold: 0.5 });
    sections.forEach((el) => {
        const media = el.querySelector('.ds-about__media');
        if (!media) {
            el.setAttribute('data-done', '1');
            return;
        }
        io.observe(media);
    });
}

function initPdpGallery(root) {
    root.querySelectorAll('[data-ds-gallery]').forEach((gallery) => {
        if (gallery.dataset.dsGalleryBound) return;
        gallery.dataset.dsGalleryBound = '1';
        const main = gallery.querySelector('[data-ds-gallery-main]');
        const thumbs = gallery.querySelectorAll('[data-ds-gallery-thumb]');
        if (!main || !thumbs.length) return;
        thumbs.forEach((btn) => {
            btn.addEventListener('click', () => {
                const src = btn.getAttribute('data-full');
                if (src) main.src = src;
                thumbs.forEach((thumb) => {
                    const on = thumb === btn;
                    thumb.classList.toggle('is-active', on);
                    if (on) thumb.setAttribute('aria-current', 'true');
                    else thumb.removeAttribute('aria-current');
                });
            });
        });
    });
}

function initPdpTabs(root) {
    root.querySelectorAll('[data-ds-tabs]').forEach((tabs) => {
        if (tabs.dataset.dsTabsBound) return;
        tabs.dataset.dsTabsBound = '1';
        const buttons = tabs.querySelectorAll('[role="tab"]');
        buttons.forEach((btn) => {
            btn.addEventListener('click', () => {
                const panelId = btn.getAttribute('aria-controls');
                buttons.forEach((item) => {
                    item.setAttribute('aria-selected', item === btn ? 'true' : 'false');
                });
                tabs.querySelectorAll('[role="tabpanel"]').forEach((panel) => {
                    panel.hidden = panel.id !== panelId;
                });
            });
        });
    });
}

function initQtyStepper(root) {
    root.querySelectorAll('[data-ds-qty]').forEach((wrapper) => {
        if (wrapper.dataset.dsQtyBound) return;
        wrapper.dataset.dsQtyBound = '1';
        const input = wrapper.querySelector('input[type="number"]');
        if (!input) return;
        wrapper.querySelectorAll('[data-ds-qty-step]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const step = parseInt(btn.getAttribute('data-ds-qty-step'), 10) || 1;
                const next = Math.max(1, (parseInt(input.value, 10) || 1) + step);
                input.value = String(next);
            });
        });
    });
}

/* ——— Wishlist (guest localStorage) ——— */

function wishlistKey() {
    const shopId = document.body.getAttribute('data-shop-id') || '0';
    return `demoshop_wishlist:${shopId}`;
}

function readWishlistIds() {
    try {
        const raw = localStorage.getItem(wishlistKey());
        const parsed = raw ? JSON.parse(raw) : [];
        return Array.isArray(parsed)
            ? parsed.map((id) => parseInt(id, 10)).filter((id) => id > 0)
            : [];
    } catch (err) {
        return [];
    }
}

function writeWishlistIds(ids) {
    localStorage.setItem(wishlistKey(), JSON.stringify([...new Set(ids)]));
}

function syncWishlistUI(root) {
    const ids = readWishlistIds();
    const countEls = document.querySelectorAll('[data-wishlist-count]');
    countEls.forEach((el) => {
        el.textContent = String(ids.length);
    });
    (root || document).querySelectorAll('[data-wishlist-toggle]').forEach((btn) => {
        const id = parseInt(btn.getAttribute('data-product-id'), 10);
        const active = ids.includes(id);
        btn.setAttribute('aria-pressed', active ? 'true' : 'false');
        if (btn.classList.contains('ds-wish-toggle--lg')) {
            const labelActive = btn.getAttribute('data-label-active') || '♥ В обраному';
            const labelIdle = btn.getAttribute('data-label-idle') || '♡ В обране';
            btn.textContent = active ? labelActive : labelIdle;
        } else {
            btn.textContent = active ? '♥' : '♡';
        }
    });
}

function initWishlist(root) {
    syncWishlistUI(root);
    (root || document).querySelectorAll('[data-wishlist-toggle]').forEach((btn) => {
        if (btn.dataset.wishBound) return;
        btn.dataset.wishBound = '1';
        btn.addEventListener('click', () => {
            const id = parseInt(btn.getAttribute('data-product-id'), 10);
            if (!id) return;
            let ids = readWishlistIds();
            if (ids.includes(id)) {
                ids = ids.filter((x) => x !== id);
            } else {
                ids.push(id);
            }
            writeWishlistIds(ids);
            syncWishlistUI(document);

            const page = document.querySelector('[data-ds-wishlist-page]');
            const base = document.body.getAttribute('data-wishlist-url');
            if (page && base) {
                const url = ids.length ? `${base}?ids=${ids.join(',')}` : base;
                window.location.replace(url);
            }
        });
    });

    const page = document.querySelector('[data-ds-wishlist-page]');
    if (page && !page.dataset.wishLoaded) {
        page.dataset.wishLoaded = '1';
        const ids = readWishlistIds();
        const base = document.body.getAttribute('data-wishlist-url');
        if (base && ids.length && !window.location.search.includes('ids=')) {
            const url = `${base}?ids=${ids.join(',')}`;
            window.location.replace(url);
        }
    }
}

/* ——— Cart toast ——— */

let toastTimer = null;
let toastCloseTimer = null;

function closeCartToast() {
    if (toastTimer) {
        clearTimeout(toastTimer);
        toastTimer = null;
    }
    if (toastCloseTimer) {
        clearTimeout(toastCloseTimer);
        toastCloseTimer = null;
    }
    const root = document.getElementById('ds-drawer-root');
    const toast = root && root.querySelector('[data-ds-cart-toast]');
    if (!toast) {
        if (root) root.innerHTML = '';
        return;
    }
    if (toast.dataset.closing === '1') return;
    toast.dataset.closing = '1';
    toast.classList.remove('is-in');
    const finish = () => {
        if (root) root.innerHTML = '';
    };
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
        finish();
        return;
    }
    toastCloseTimer = setTimeout(finish, 320);
}

function initCartToast(root) {
    const toast = (root || document).querySelector('[data-ds-cart-toast]');
    if (!toast || toast.dataset.bound === '1') return;
    toast.dataset.bound = '1';
    if (toastTimer) clearTimeout(toastTimer);
    requestAnimationFrame(() => {
        toast.classList.add('is-in');
    });
    toast.querySelectorAll('[data-ds-toast-close]').forEach((btn) => {
        btn.addEventListener('click', closeCartToast);
    });
    toastTimer = setTimeout(closeCartToast, 3200);
}

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeCartToast();
});

/* ——— Catalog flyout delay ——— */

function initFlyout() {
    document.querySelectorAll('[data-ds-flyout]').forEach((item) => {
        if (item.dataset.flyBound) return;
        item.dataset.flyBound = '1';
        let timer = null;
        item.addEventListener('mouseenter', () => {
            clearTimeout(timer);
            item.classList.add('is-open');
        });
        item.addEventListener('mouseleave', () => {
            timer = window.setTimeout(() => item.classList.remove('is-open'), 200);
        });
    });
}

/* ——— NP checkout ——— */

function debounce(fn, ms) {
    let t;
    return (...args) => {
        clearTimeout(t);
        t = window.setTimeout(() => fn(...args), ms);
    };
}

function initCheckout() {
    const form = document.querySelector('[data-ds-checkout]');
    if (!form || form.dataset.bound) return;
    form.dataset.bound = '1';

    const citiesUrl = document.body.getAttribute('data-np-cities-url');
    const warehousesUrl = document.body.getAttribute('data-np-warehouses-url');
    const cityInput = form.querySelector('[data-ds-np-city]');
    const cityRef = form.querySelector('[data-ds-np-city-ref]');
    const suggest = form.querySelector('[data-ds-np-suggest]');
    const warehouseSelect = form.querySelector('[data-ds-np-warehouse]');
    const warehouseName = form.querySelector('[data-ds-np-warehouse-name]');
    const npBlock = form.querySelector('[data-ds-np-block]');
    const addressBlock = form.querySelector('[data-ds-address-block]');
    const modal = document.querySelector('[data-ds-order-modal]');

    function setDeliveryMode() {
        const method = form.querySelector('[data-ds-delivery]:checked')?.value || 'np_warehouse';
        const isNp = method === 'np_warehouse';
        if (npBlock) npBlock.hidden = !isNp;
        if (addressBlock) addressBlock.hidden = isNp;
        if (cityInput) cityInput.required = isNp;
        if (warehouseSelect) warehouseSelect.required = isNp;
        const address = form.querySelector('#id_address');
        if (address) address.required = !isNp;
    }

    form.querySelectorAll('[data-ds-delivery]').forEach((radio) => {
        radio.addEventListener('change', setDeliveryMode);
    });
    setDeliveryMode();

    const searchCities = debounce(async () => {
        if (!citiesUrl || !cityInput || !suggest) return;
        const q = cityInput.value.trim();
        if (q.length < 1) {
            suggest.hidden = true;
            suggest.innerHTML = '';
            return;
        }
        const res = await fetch(`${citiesUrl}?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        suggest.innerHTML = '';
        (data.results || []).forEach((city) => {
            const li = document.createElement('li');
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = `${city.name}${city.area ? ` (${city.area})` : ''}`;
            btn.addEventListener('click', async () => {
                cityInput.value = city.name;
                cityRef.value = city.ref;
                suggest.hidden = true;
                suggest.innerHTML = '';
                await loadWarehouses(city.ref);
            });
            li.appendChild(btn);
            suggest.appendChild(li);
        });
        suggest.hidden = !(data.results || []).length;
    }, 220);

    async function loadWarehouses(ref) {
        if (!warehousesUrl || !warehouseSelect) return;
        warehouseSelect.disabled = true;
        const labelLoading = warehouseSelect.getAttribute('data-label-loading') || 'Завантаження…';
        warehouseSelect.innerHTML = `<option value="">${labelLoading}</option>`;
        const res = await fetch(`${warehousesUrl}?city_ref=${encodeURIComponent(ref)}`);
        const data = await res.json();
        const labelChoose = warehouseSelect.getAttribute('data-label-choose') || 'Оберіть відділення';
        warehouseSelect.innerHTML = `<option value="">${labelChoose}</option>`;
        (data.results || []).forEach((wh) => {
            const opt = document.createElement('option');
            opt.value = wh.ref;
            opt.textContent = wh.description;
            opt.dataset.name = wh.description;
            warehouseSelect.appendChild(opt);
        });
        warehouseSelect.disabled = false;
    }

    if (cityInput) {
        cityInput.addEventListener('input', () => {
            if (cityRef) cityRef.value = '';
            searchCities();
        });
    }
    if (warehouseSelect) {
        warehouseSelect.addEventListener('change', () => {
            const opt = warehouseSelect.selectedOptions[0];
            if (warehouseName) warehouseName.value = opt?.dataset.name || opt?.textContent || '';
        });
    }

    document.addEventListener('click', (event) => {
        if (suggest && !suggest.contains(event.target) && event.target !== cityInput) {
            suggest.hidden = true;
        }
    });

    const openBtn = form.querySelector('[data-ds-checkout-open]');
    openBtn?.addEventListener('click', () => {
        if (!form.reportValidity()) return;
        const method = form.querySelector('[data-ds-delivery]:checked')?.value || 'np_warehouse';
        const deliveryLabel = method === 'np_warehouse'
            ? (form.querySelector('[data-label-np]')?.textContent || 'Відділення Нової Пошти')
            : (form.querySelector('[data-label-address]')?.textContent || 'Адресна доставка');
        const place = method === 'np_warehouse'
            ? `${cityInput?.value || ''} — ${warehouseSelect?.selectedOptions[0]?.textContent || ''}`.trim()
            : (form.querySelector('#id_address')?.value || '');
        if (modal) {
            modal.querySelector('[data-ds-modal-delivery]').textContent = deliveryLabel;
            modal.querySelector('[data-ds-modal-place]').textContent = place || '—';
            modal.showModal();
        } else {
            form.submit();
        }
    });

    modal?.querySelector('[data-ds-modal-cancel]')?.addEventListener('click', () => modal.close());
    modal?.querySelector('[data-ds-modal-confirm]')?.addEventListener('click', () => {
        modal.close();
        form.submit();
    });
}

const STRIP_SPEED_PX_S = 36;
const STRIP_MIN_DURATION_S = 18;

function tuneLoopDuration(loop) {
    const setEl = loop.querySelector('.page-strip__set');
    if (!setEl) return;
    const width = setEl.getBoundingClientRect().width;
    if (width <= 0) return;
    const duration = Math.max(STRIP_MIN_DURATION_S, width / STRIP_SPEED_PX_S);
    loop.style.setProperty('--loop-duration', `${duration.toFixed(1)}s`);
}

function initPageStrip(root) {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const loops = [];
    if (root.matches && root.matches('[data-loop]')) loops.push(root);
    if (root.querySelectorAll) {
        root.querySelectorAll('[data-loop]').forEach((el) => loops.push(el));
    }
    loops.forEach((loop) => {
        if (loop.dataset.loopBound) return;
        loop.dataset.loopBound = '1';
        tuneLoopDuration(loop);
        const target = loop.closest('section') || loop;
        const setMotion = (on) => loop.classList.toggle('is-motion', !!on);
        if ('IntersectionObserver' in window) {
            const io = new IntersectionObserver((entries) => {
                entries.forEach((entry) => setMotion(entry.isIntersecting));
            }, { rootMargin: '80px 0px', threshold: 0 });
            io.observe(target);
        } else {
            setMotion(true);
        }
    });
}

function initHeroSlider() {
    const root = document.querySelector('[data-ds-hero-slider]');
    if (!root) return;

    const slides = Array.from(root.querySelectorAll('[data-ds-hero-slide]'));
    const dots = Array.from(root.querySelectorAll('[data-ds-hero-dot]'));
    if (slides.length < 2) return;

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const intervalMs = 4000;
    let index = Math.max(0, slides.findIndex((s) => s.classList.contains('is-active')));
    let timer = null;
    let touchX = null;

    const go = (next) => {
        const total = slides.length;
        index = ((next % total) + total) % total;
        slides.forEach((slide, i) => {
            const active = i === index;
            slide.classList.toggle('is-active', active);
            slide.setAttribute('aria-hidden', active ? 'false' : 'true');
        });
        dots.forEach((dot, i) => {
            const active = i === index;
            dot.classList.toggle('is-active', active);
            dot.setAttribute('aria-selected', active ? 'true' : 'false');
        });
    };

    const stop = () => {
        if (timer) {
            window.clearInterval(timer);
            timer = null;
        }
    };

    const start = () => {
        stop();
        if (reduced) return;
        timer = window.setInterval(() => go(index + 1), intervalMs);
    };

    const prevBtn = root.querySelector('[data-ds-hero-prev]');
    const nextBtn = root.querySelector('[data-ds-hero-next]');
    if (prevBtn) prevBtn.addEventListener('click', () => { go(index - 1); start(); });
    if (nextBtn) nextBtn.addEventListener('click', () => { go(index + 1); start(); });
    dots.forEach((dot) => {
        dot.addEventListener('click', () => {
            const i = Number(dot.getAttribute('data-index'));
            if (Number.isFinite(i)) {
                go(i);
                start();
            }
        });
    });

    root.addEventListener('pointerdown', (e) => {
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        touchX = e.clientX;
    });
    root.addEventListener('pointerup', (e) => {
        if (touchX == null) return;
        const dx = e.clientX - touchX;
        touchX = null;
        if (Math.abs(dx) < 48) return;
        go(index + (dx < 0 ? 1 : -1));
        start();
    });
    root.addEventListener('pointercancel', () => { touchX = null; });

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) stop();
        else start();
    });

    go(index);
    start();
}

/* Catalog filters: phone drawer. Desktop sidebar is the same node, unmoved. */
function initFilterDrawer() {
    const drawer = document.querySelector('[data-ds-filter-drawer]');
    const openBtn = document.querySelector('[data-ds-filter-open]');
    if (!drawer || !openBtn || drawer.dataset.filterBound) return;
    drawer.dataset.filterBound = '1';
    const backdrop = document.querySelector('.ds-filter-backdrop');

    function setOpen(open) {
        drawer.classList.toggle('is-open', open);
        if (backdrop) backdrop.hidden = !open;
        openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
        document.body.classList.toggle('ds-filter-open', open);
        if (!open) openBtn.focus();
    }

    openBtn.addEventListener('click', () => {
        setOpen(!drawer.classList.contains('is-open'));
    });
    document.querySelectorAll('[data-ds-filter-close]').forEach((el) => {
        el.addEventListener('click', () => setOpen(false));
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && drawer.classList.contains('is-open')) setOpen(false);
    });
}

function initAll(root) {
    initReveal(root);
    initPageStrip(root);
    initQtyStepper(root);
    initPdpGallery(root);
    initPdpTabs(root);
    initWishlist(root);
    initCartToast(root);
    if (window.dsInitTimers) window.dsInitTimers(root);
}

document.addEventListener('DOMContentLoaded', () => {
    initSafariFix();
    initAll(document);
    initAboutReveal();
    initFlyout();
    initCheckout();
    initFilterDrawer();
    initHeroSlider();
});

document.addEventListener('htmx:afterSwap', (event) => {
    const target = (event.detail && event.detail.target) || document;
    initAll(target);
});
