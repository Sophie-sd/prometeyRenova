(function() {
    'use strict';

    class PortfolioHeroSlots {
        constructor() {
            this.slots = new Map();
            this.slotTimeouts = new Map();
            this.observer = null;
            this.timeoutCounter = 0;
        }

        init() {
            const slotElements = document.querySelectorAll('.portfolio-card');
            if (slotElements.length === 0) return;

            slotElements.forEach((slot, index) => {
                this.initSlot(slot, index);
            });

            this.setupIntersectionObserver();
            this.setupResizeHandler();
        }

        initSlot(slotElement, index) {
            const slotNum = slotElement.dataset.slot || index + 1;
            const imagePaths = [
                slotElement.dataset.image1,
                slotElement.dataset.image2,
                slotElement.dataset.image3
            ].filter(path => path && path.trim());

            if (imagePaths.length === 0) return;

            this.slots.set(slotNum, {
                element: slotElement,
                imagePaths,
                currentIndex: 0,
                isAnimating: false,
                currentTimeout: null
            });
        }

        setupIntersectionObserver() {
            const options = {
                threshold: 0.1
            };

            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const slotNum = entry.target.dataset.slot;
                        this.startSlotAnimation(slotNum);
                    }
                });
            }, options);

            this.slots.forEach(slot => {
                this.observer.observe(slot.element);
            });
        }

        startSlotAnimation(slotNum) {
            const slot = this.slots.get(slotNum);
            if (!slot || slot.animationStarted) return;

            slot.animationStarted = true;

            const initialDelay = (parseInt(slotNum) - 1) * 1000;
            setTimeout(() => {
                this.scheduleNextSwitch(slotNum);
            }, initialDelay);
        }

        scheduleNextSwitch(slotNum) {
            const slot = this.slots.get(slotNum);
            if (!slot) return;

            const delay = Math.random() * 3000 + 4000;
            const timeout = setTimeout(() => {
                this.switchImage(slotNum);
                this.scheduleNextSwitch(slotNum);
            }, delay);

            slot.currentTimeout = timeout;
        }

        switchImage(slotNum) {
            const slot = this.slots.get(slotNum);
            if (!slot) return;

            slot.currentIndex = (slot.currentIndex + 1) % slot.imagePaths.length;
            const imagePath = slot.imagePaths[slot.currentIndex];

            if (!imagePath) return;

            const wrapper = slot.element?.querySelector('.portfolio-hero__image-wrapper');
            if (!wrapper) return;

            const current = wrapper.querySelector('.portfolio-hero__image');
            const next = wrapper.querySelector('.portfolio-hero__image--next');

            if (!current || !next) return;

            next.src = imagePath;

            const handleImageLoad = () => {
                if (!next || !current) return;

                next.style.opacity = '1';
                next.style.zIndex = '1';
                current.style.opacity = '0';
                current.style.zIndex = '0';

                setTimeout(() => {
                    if (!current || !next) return;

                    current.src = next.src;
                    current.style.opacity = '1';
                    current.style.zIndex = '1';
                    next.style.opacity = '0';
                    next.style.zIndex = '0';
                }, 500);
            };

            next.onload = handleImageLoad;

            if (next.complete) {
                handleImageLoad();
            }
        }

        setupResizeHandler() {
            let resizeTimeout;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {
                    this.slots.forEach((slot, slotNum) => {
                        if (!slot.animationStarted) {
                            this.startSlotAnimation(slotNum);
                        }
                    });
                }, 300);
            });
        }

        destroy() {
            if (this.observer) {
                this.observer.disconnect();
            }

            this.slots.forEach((slot) => {
                if (slot.currentTimeout) {
                    clearTimeout(slot.currentTimeout);
                    slot.currentTimeout = null;
                }
            });

            this.slots.clear();
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const portfolioHero = new PortfolioHeroSlots();
        portfolioHero.init();

        window.addEventListener('beforeunload', () => {
            portfolioHero.destroy();
        });
    });
})();
