(function() {
    'use strict';

    class PortfolioHeroSlots {
        constructor() {
            this.slots = new Map();
            this.animationTimeouts = new Map();
            this.observer = null;
        }

        init() {
            const slotElements = document.querySelectorAll('.portfolio-hero__slot');
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
            ];

            this.slots.set(slotNum, {
                element: slotElement,
                imagePaths,
                currentIndex: 0,
                isAnimating: false
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
            this.scheduleNextSwitch(slotNum);
        }

        scheduleNextSwitch(slotNum) {
            const slot = this.slots.get(slotNum);
            if (!slot) return;

            const delay = Math.random() * 3000 + 4000;
            const timeout = setTimeout(() => {
                this.switchImage(slotNum);
                this.scheduleNextSwitch(slotNum);
            }, delay);

            this.animationTimeouts.set(`${slotNum}-${Date.now()}`, timeout);
        }

        switchImage(slotNum) {
            const slot = this.slots.get(slotNum);
            if (!slot) return;

            slot.currentIndex = (slot.currentIndex + 1) % slot.imagePaths.length;

            const wrapper = slot.element.querySelector('.portfolio-hero__image-wrapper');
            const current = wrapper.querySelector('.portfolio-hero__image');
            const next = wrapper.querySelector('.portfolio-hero__image--next');

            next.src = slot.imagePaths[slot.currentIndex];

            next.onload = () => {
                next.style.opacity = '1';
                next.style.zIndex = '1';
                current.style.opacity = '0';
                current.style.zIndex = '0';

                setTimeout(() => {
                    current.src = next.src;
                    current.style.opacity = '1';
                    current.style.zIndex = '1';
                    next.style.opacity = '0';
                    next.style.zIndex = '0';
                }, 500);
            };

            if (next.complete) {
                next.onload();
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
            this.animationTimeouts.forEach(timeout => clearTimeout(timeout));
            this.animationTimeouts.clear();
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
