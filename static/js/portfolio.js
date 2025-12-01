(function() {
    'use strict';

    class PortfolioHeroSlots {
        constructor() {
            this.slots = new Map();
            this.slotTimeouts = new Map();
            this.observer = null;
            this.initialized = false;
            this.imageCache = new Map();
        }

        init() {
            try {
                const slotElements = document.querySelectorAll('.portfolio-card');
                if (slotElements.length === 0) return;

                this.preloadAllImages(slotElements);

                slotElements.forEach((slot, index) => {
                    this.initSlot(slot, index);
                });

                if (this.slots.size === 0) {
                    console.warn('PortfolioHero: No valid slots found');
                    return;
                }

                this.initialized = true;

                if (this.isIOSSafari()) {
                    setTimeout(() => {
                        this.startAllAnimationsWithDelay();
                    }, 100);
                } else if ('IntersectionObserver' in window) {
                    this.setupIntersectionObserver();
                    setTimeout(() => this.checkInitialVisibility(), 300);
                } else {
                    this.startAllAnimationsWithDelay();
                }

                this.setupResizeHandler();
            } catch (error) {
                console.error('PortfolioHero init error:', error);
            }
        }

        preloadAllImages(slotElements) {
            slotElements.forEach(slot => {
                const images = [slot.dataset.image1, slot.dataset.image2, slot.dataset.image3];
                images.forEach(src => {
                    if (src && !this.imageCache.has(src)) {
                        const img = new Image();
                        img.src = src;
                        this.imageCache.set(src, img);
                    }
                });
            });
        }

        isIOSSafari() {
            const ua = navigator.userAgent;
            const iOS = /iPad|iPhone|iPod/.test(ua);
            const webkit = /WebKit/.test(ua);
            return iOS && webkit && !/CriOS|FxiOS|OPiOS|mercury/.test(ua);
        }

        initSlot(slotElement, index) {
            try {
                const slotNum = slotElement.dataset.slot || String(index + 1);
                
                if (!slotElement.dataset.image1 || !slotElement.dataset.image2 || !slotElement.dataset.image3) {
                    console.warn(`PortfolioHero: Slot ${slotNum} missing image data`);
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
                    currentTimeout: null,
                    animationStarted: false,
                    isAnimating: false
                });
            } catch (error) {
                console.error('PortfolioHero initSlot error:', error);
            }
        }

        setupIntersectionObserver() {
            const options = {
                threshold: 0.1,
                rootMargin: '50px'
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

        startAllAnimationsWithDelay() {
            this.slots.forEach((slot, slotNum) => {
                const delay = (parseInt(slotNum) - 1) * 200;
                setTimeout(() => {
                    this.startSlotAnimation(slotNum);
                }, delay);
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

                this.slotTimeouts.set(`start-${slotNum}`, timeout);
            } catch (error) {
                console.error('PortfolioHero startSlotAnimation error:', error);
            }
        }

        scheduleNextSwitch(slotNum) {
            try {
                const slot = this.slots.get(slotNum);
                if (!slot) return;

                const delay = Math.random() * 2000 + 2500;
                const timeout = setTimeout(() => {
                    this.switchImage(slotNum);
                    this.scheduleNextSwitch(slotNum);
                }, delay);

                slot.currentTimeout = timeout;
            } catch (error) {
                console.error('PortfolioHero scheduleNextSwitch error:', error);
            }
        }

        switchImage(slotNum) {
            try {
                const slot = this.slots.get(slotNum);
                if (!slot || slot.isAnimating) return;
                
                slot.isAnimating = true;

                slot.currentIndex = (slot.currentIndex + 1) % slot.imagePaths.length;
                const imagePath = slot.imagePaths[slot.currentIndex];

                if (!imagePath) {
                    slot.isAnimating = false;
                    return;
                }

                const wrapper = slot.element?.querySelector('.portfolio-hero__image-wrapper');
                if (!wrapper) {
                    slot.isAnimating = false;
                    return;
                }

                const current = wrapper.querySelector('.portfolio-hero__image:not(.portfolio-hero__image--next)');
                const next = wrapper.querySelector('.portfolio-hero__image--next');

                if (!current || !next) {
                    slot.isAnimating = false;
                    return;
                }

                next.src = imagePath;

                const handleImageLoad = () => {
                    try {
                        if (!next || !current) {
                            slot.isAnimating = false;
                            return;
                        }

                        next.style.opacity = '1';
                        next.style.zIndex = '2';
                        current.style.opacity = '0';
                        current.style.zIndex = '1';

                        setTimeout(() => {
                            try {
                                if (!current || !next) {
                                    slot.isAnimating = false;
                                    return;
                                }

                                current.src = next.src;
                                current.style.opacity = '1';
                                current.style.zIndex = '1';
                                next.style.opacity = '0';
                                next.style.zIndex = '0';

                                next.onload = null;
                                next.onerror = null;
                                slot.isAnimating = false;
                            } catch (error) {
                                console.error('PortfolioHero: Error in swap cleanup:', error);
                                slot.isAnimating = false;
                            }
                        }, 300);

                    } catch (error) {
                        console.error('PortfolioHero: Error in handleImageLoad:', error);
                        slot.isAnimating = false;
                    }
                };

                const handleImageError = () => {
                    console.error(`PortfolioHero: Failed to load image: ${imagePath}`);
                    next.onload = null;
                    next.onerror = null;
                    slot.isAnimating = false;
                };

                next.onload = handleImageLoad;
                next.onerror = handleImageError;

                if (next.complete && next.naturalWidth > 0) {
                    handleImageLoad();
                }
            } catch (error) {
                console.error('PortfolioHero switchImage error:', error);
                const slot = this.slots.get(slotNum);
                if (slot) slot.isAnimating = false;
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

                this.slotTimeouts.forEach(timeout => {
                    clearTimeout(timeout);
                });
                this.slotTimeouts.clear();

                this.slots.clear();
                this.imageCache.clear();
                this.initialized = false;
            } catch (error) {
                console.error('PortfolioHero destroy error:', error);
            }
        }
    }

    const initPortfolio = () => {
        try {
            const portfolioHero = new PortfolioHeroSlots();
            portfolioHero.init();

            window.addEventListener('beforeunload', () => {
                portfolioHero.destroy();
            });
        } catch (error) {
            console.error('PortfolioHero initialization error:', error);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPortfolio);
    } else {
        initPortfolio();
    }
})();
