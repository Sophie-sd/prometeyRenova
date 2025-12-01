(function() {
    'use strict';

    class PortfolioHeroSlots {
        constructor() {
            this.slots = new Map();
            this.slotTimeouts = new Map();
            this.observer = null;
            this.timeoutCounter = 0;
            this.initialized = false;
        }

        init() {
            try {
                const slotElements = document.querySelectorAll('.portfolio-card');
                if (slotElements.length === 0) return;

                slotElements.forEach((slot, index) => {
                    this.initSlot(slot, index);
                });

                // Перевірка чи є валідні слоти
                if (this.slots.size === 0) {
                    console.warn('PortfolioHero: No valid slots found');
                    return;
                }

                this.initialized = true;

                // Налаштування observer з fallback
                if ('IntersectionObserver' in window) {
                    this.setupIntersectionObserver();
                    // Fallback: перевірка видимості через requestAnimationFrame
                    requestAnimationFrame(() => {
                        requestAnimationFrame(() => {
                            this.checkInitialVisibility();
                        });
                    });
                } else {
                    // Fallback для старих браузерів без IntersectionObserver
                    this.startAllAnimations();
                }

                this.setupResizeHandler();
            } catch (error) {
                console.error('PortfolioHero init error:', error);
            }
        }

        initSlot(slotElement, index) {
            try {
                const slotNum = slotElement.dataset.slot || index + 1;
                
                // Перевірка data-атрибутів
                if (!slotElement.dataset.image1 || !slotElement.dataset.image2 || !slotElement.dataset.image3) {
                    console.warn(`PortfolioHero: Slot ${slotNum} missing image data`, {
                        image1: slotElement.dataset.image1,
                        image2: slotElement.dataset.image2,
                        image3: slotElement.dataset.image3
                    });
                    return;
                }

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
            } catch (error) {
                console.error('PortfolioHero initSlot error:', error);
            }
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
            try {
                const slot = this.slots.get(slotNum);
                if (!slot || slot.animationStarted) return;

                slot.animationStarted = true;

                const initialDelay = (parseInt(slotNum) - 1) * 1000;
                const timeout = setTimeout(() => {
                    this.scheduleNextSwitch(slotNum);
                }, initialDelay);

                // Зберігаємо таймаут для можливості очистки
                this.slotTimeouts.set(`start-${slotNum}`, timeout);
            } catch (error) {
                console.error('PortfolioHero startSlotAnimation error:', error);
            }
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
            try {
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
                    try {
                        if (!next || !current) return;

                        next.style.opacity = '1';
                        next.style.zIndex = '1';
                        current.style.opacity = '0';
                        current.style.zIndex = '0';

                        setTimeout(() => {
                            try {
                                if (!current || !next) return;

                                current.src = next.src;
                                current.style.opacity = '1';
                                current.style.zIndex = '1';
                                next.style.opacity = '0';
                                next.style.zIndex = '0';
                            } catch (error) {
                                console.error('PortfolioHero: Error in image swap timeout:', error);
                            }
                        }, 500);
                    } catch (error) {
                        console.error('PortfolioHero: Error in handleImageLoad:', error);
                    }
                };

                next.onload = handleImageLoad;

                if (next.complete) {
                    handleImageLoad();
                }
            } catch (error) {
                console.error('PortfolioHero switchImage error:', error);
            }
        }

        checkInitialVisibility() {
            try {
                this.slots.forEach((slot, slotNum) => {
                    if (slot.animationStarted) return;

                    const rect = slot.element.getBoundingClientRect();
                    const isVisible = (
                        rect.top < window.innerHeight &&
                        rect.bottom > 0 &&
                        rect.left < window.innerWidth &&
                        rect.right > 0
                    );

                    if (isVisible) {
                        this.startSlotAnimation(slotNum);
                    }
                });
            } catch (error) {
                console.error('PortfolioHero checkInitialVisibility error:', error);
            }
        }

        startAllAnimations() {
            try {
                this.slots.forEach((slot, slotNum) => {
                    this.startSlotAnimation(slotNum);
                });
            } catch (error) {
                console.error('PortfolioHero startAllAnimations error:', error);
            }
        }

        setupResizeHandler() {
            try {
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
            } catch (error) {
                console.error('PortfolioHero setupResizeHandler error:', error);
            }
        }

        destroy() {
            try {
                if (this.observer) {
                    this.observer.disconnect();
                }

                this.slots.forEach((slot) => {
                    if (slot.currentTimeout) {
                        clearTimeout(slot.currentTimeout);
                        slot.currentTimeout = null;
                    }
                });

                // Очистити всі таймаути
                this.slotTimeouts.forEach(timeout => {
                    clearTimeout(timeout);
                });
                this.slotTimeouts.clear();

                this.slots.clear();
                this.initialized = false;
            } catch (error) {
                console.error('PortfolioHero destroy error:', error);
            }
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        try {
            const portfolioHero = new PortfolioHeroSlots();
            portfolioHero.init();

            window.addEventListener('beforeunload', () => {
                portfolioHero.destroy();
            });
        } catch (error) {
            console.error('PortfolioHero initialization error:', error);
        }
    });
})();
