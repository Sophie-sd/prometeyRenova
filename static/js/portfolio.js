/* =================================
   PORTFOLIO PAGE JAVASCRIPT
   Advanced Sticky Scroll System
   ================================= */

'use strict';

document.addEventListener('DOMContentLoaded', function() {
    console.log('💼 Portfolio page loaded');
    
    initStickyScrollSystem();
    initVideoSystem();
    initNavigationSystem();
    initViewportHeight();
    initMobileOptimizations();
    
    console.log('✅ Portfolio page initialized');
});

/* =================================
   STICKY SCROLL SYSTEM
   ================================= */

function initStickyScrollSystem() {
    const stickySections = document.querySelectorAll('.sticky-section');
    const portfolioProjects = document.querySelector('.portfolio-projects');
    
    if (!stickySections.length || !portfolioProjects) {
        console.log('No sticky sections found');
        return;
    }
    
    console.log(`Found ${stickySections.length} sticky sections`);
    
    let currentSectionIndex = 0;
    let isProgrammaticScrolling = false;
    let isTransitioning = false;
    
    // Initialize first section as active
    updateSectionStates();
    
    // Scroll event handler
    const handleScroll = throttle(() => {
        if (isProgrammaticScrolling || isTransitioning) return;
        
        const scrollTop = window.pageYOffset;
        const windowHeight = window.innerHeight;
        const heroHeight = document.querySelector('.portfolio-hero')?.offsetHeight || 0;
        const scrollAfterHero = Math.max(0, scrollTop - heroHeight);
        
        // Calculate current section based on scroll position
        const newSectionIndex = Math.max(0, Math.min(
            Math.floor(scrollAfterHero / windowHeight),
            stickySections.length - 1
        ));
        
        if (newSectionIndex !== currentSectionIndex) {
            transitionToSection(newSectionIndex);
        }
    }, 16);
    
    // Transition between sections
    function transitionToSection(newIndex) {
        if (isTransitioning) return;
        
        isTransitioning = true;
        const previousIndex = currentSectionIndex;
        currentSectionIndex = newIndex;
        
        // Add transition classes
        if (stickySections[previousIndex]) {
            stickySections[previousIndex].classList.add('transition-out');
        }
        
        if (stickySections[currentSectionIndex]) {
            stickySections[currentSectionIndex].classList.add('transition-in');
        }
        
        // Update states
        updateSectionStates();
        updateNavigationStates();
        updateVideos();
        
        // Remove transition classes after animation
        setTimeout(() => {
            stickySections.forEach(section => {
                section.classList.remove('transition-in', 'transition-out');
            });
            isTransitioning = false;
        }, 800);
        
        console.log(`Section transitioned: ${previousIndex + 1} → ${currentSectionIndex + 1}`);
    }
    
    // Update section states (active, passed, pending)
    function updateSectionStates() {
        stickySections.forEach((section, index) => {
            section.classList.remove('active', 'passed', 'pending');
            
            if (index === currentSectionIndex) {
                section.classList.add('active');
            } else if (index < currentSectionIndex) {
                section.classList.add('passed');
            } else {
                section.classList.add('pending');
            }
        });
    }
    
    // Keyboard navigation
    function handleKeyNavigation(e) {
        if (e.key === 'ArrowDown' && currentSectionIndex < stickySections.length - 1) {
            e.preventDefault();
            smoothScrollToSection(currentSectionIndex + 1);
        } else if (e.key === 'ArrowUp' && currentSectionIndex > 0) {
            e.preventDefault();
            smoothScrollToSection(currentSectionIndex - 1);
        }
    }
    
    // Smooth scroll to specific section
    function smoothScrollToSection(index) {
        if (index < 0 || index >= stickySections.length) return;
        
        const heroHeight = document.querySelector('.portfolio-hero')?.offsetHeight || 0;
        const targetScroll = heroHeight + (index * window.innerHeight);
        
        isProgrammaticScrolling = true;
        
        window.scrollTo({
            top: targetScroll,
            behavior: 'smooth'
        });
        
        // Reset flag after scroll completes
        setTimeout(() => {
            isProgrammaticScrolling = false;
        }, 1000);
    }
    
    // Bind events
    window.addEventListener('scroll', handleScroll, { passive: true });
    document.addEventListener('keydown', handleKeyNavigation);
    
    // Export functions for navigation system
    window.portfolioScrollSystem = {
        goToSection: smoothScrollToSection,
        getCurrentSection: () => currentSectionIndex,
        getTotalSections: () => stickySections.length
    };
    
    console.log('🎯 Sticky scroll system initialized');
}

/* =================================
   VIDEO SYSTEM
   ================================= */

function initVideoSystem() {
    const videos = document.querySelectorAll('.project-video');
    
    if (!videos.length) {
        console.log('No project videos found');
        return;
    }
    
    // Setup intersection observer for video lazy loading
    const videoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const video = entry.target;
            
            if (entry.isIntersecting) {
                loadVideo(video);
            } else {
                pauseVideo(video);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '50px 0px'
    });
    
    // Observe all videos
    videos.forEach(video => {
        videoObserver.observe(video);
    });
    
    // Load video sources based on device
    function loadVideo(video) {
        if (video.src || video.dataset.loaded) return;
        
        const sources = video.querySelectorAll('source');
        const isMobile = window.innerWidth <= 768;
        
        sources.forEach(source => {
            const media = source.getAttribute('media');
            let shouldLoad = false;
            
            if (isMobile && media && media.includes('max-width')) {
                shouldLoad = true;
            } else if (!isMobile && media && media.includes('min-width')) {
                shouldLoad = true;
            }
            
            if (shouldLoad) {
                video.src = source.src;
                video.dataset.loaded = 'true';
                
                video.addEventListener('loadeddata', () => {
                    playVideo(video);
                }, { once: true });
                
                console.log(`📹 Video loaded: ${source.src}`);
                return;
            }
        });
    }
    
    // Play video safely
    async function playVideo(video) {
        try {
            if (video.readyState >= 3) {
                await video.play();
            }
        } catch (error) {
            console.warn('Video play failed:', error);
        }
    }
    
    // Pause video safely
    function pauseVideo(video) {
        try {
            video.pause();
        } catch (error) {
            console.warn('Video pause failed:', error);
        }
    }
    
    // Update videos based on current section
    function updateVideos() {
        const currentSection = document.querySelector('.sticky-section.active');
        
        videos.forEach((video, index) => {
            const videoSection = video.closest('.sticky-section');
            
            if (videoSection === currentSection) {
                playVideo(video);
            } else {
                pauseVideo(video);
            }
        });
    }
    
    // Export for sticky scroll system
    window.updateVideos = updateVideos;
    
    console.log(`📹 Video system initialized for ${videos.length} videos`);
}

/* =================================
   NAVIGATION SYSTEM
   ================================= */

function initNavigationSystem() {
    const navDots = document.querySelectorAll('.nav-dot');
    const navPrev = document.querySelector('.nav-prev');
    const navNext = document.querySelector('.nav-next');
    
    if (!navDots.length) {
        console.log('No navigation elements found');
        return;
    }
    
    // Dot navigation
    navDots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            if (window.portfolioScrollSystem) {
                window.portfolioScrollSystem.goToSection(index);
            }
        });
    });
    
    // Arrow navigation
    if (navPrev) {
        navPrev.addEventListener('click', () => {
            if (window.portfolioScrollSystem) {
                const current = window.portfolioScrollSystem.getCurrentSection();
                if (current > 0) {
                    window.portfolioScrollSystem.goToSection(current - 1);
                }
            }
        });
    }
    
    if (navNext) {
        navNext.addEventListener('click', () => {
            if (window.portfolioScrollSystem) {
                const current = window.portfolioScrollSystem.getCurrentSection();
                const total = window.portfolioScrollSystem.getTotalSections();
                if (current < total - 1) {
                    window.portfolioScrollSystem.goToSection(current + 1);
                }
            }
        });
    }
    
    // Update navigation states
    function updateNavigationStates() {
        if (!window.portfolioScrollSystem) return;
        
        const current = window.portfolioScrollSystem.getCurrentSection();
        const total = window.portfolioScrollSystem.getTotalSections();
        
        // Update dots
        navDots.forEach((dot, index) => {
            dot.classList.toggle('active', index === current);
        });
        
        // Update arrows
        if (navPrev) {
            navPrev.disabled = current === 0;
        }
        
        if (navNext) {
            navNext.disabled = current === total - 1;
        }
    }
    
    // Export for sticky scroll system
    window.updateNavigationStates = updateNavigationStates;
    
    console.log(`🧭 Navigation system initialized with ${navDots.length} dots`);
}

/* =================================
   VIEWPORT HEIGHT FIX
   ================================= */

function initViewportHeight() {
    function updateViewportHeight() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    
    updateViewportHeight();
    window.addEventListener('resize', debounce(updateViewportHeight, 250));
    
    console.log('📱 Viewport height fix applied');
}

/* =================================
   MOBILE OPTIMIZATIONS
   ================================= */

function initMobileOptimizations() {
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Disable sticky scroll on mobile
        const portfolioProjects = document.querySelector('.portfolio-projects');
        if (portfolioProjects) {
            portfolioProjects.style.height = 'auto';
        }
        
        // Enable simple scroll behavior
        const stickySections = document.querySelectorAll('.sticky-section');
        stickySections.forEach(section => {
            section.style.position = 'relative';
            section.style.height = 'auto';
            section.style.minHeight = '100vh';
        });
        
        console.log('📱 Mobile optimizations applied');
    }
    
    // Handle orientation change
    window.addEventListener('orientationchange', () => {
        setTimeout(() => {
            initViewportHeight();
        }, 500);
    });
}

/* =================================
   UTILITY FUNCTIONS
   ================================= */

// Throttle function for scroll events
function throttle(func, delay) {
    let timeoutId;
    let lastExecTime = 0;
    
    return function (...args) {
        const currentTime = Date.now();
        
        if (currentTime - lastExecTime > delay) {
            func.apply(this, args);
            lastExecTime = currentTime;
        } else {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
                lastExecTime = Date.now();
            }, delay - (currentTime - lastExecTime));
        }
    };
}

// Debounce function for resize events
function debounce(func, delay) {
    let timeoutId;
    
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/* =================================
   PERFORMANCE MONITORING
   ================================= */

// Monitor scroll performance
let scrollCount = 0;
const scrollStartTime = Date.now();

window.addEventListener('scroll', () => {
    scrollCount++;
    
    if (scrollCount % 100 === 0) {
        const elapsed = Date.now() - scrollStartTime;
        const fps = (scrollCount / elapsed) * 1000;
        console.log(`📊 Scroll performance: ${scrollCount} events, ~${fps.toFixed(1)} fps`);
    }
}, { passive: true });

/* =================================
   ERROR HANDLING
   ================================= */

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Portfolio page error:', e.error);
    return false;
});

// Promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Portfolio page promise rejection:', e.reason);
    e.preventDefault();
});

/* =================================
   ACCESSIBILITY
   ================================= */

// Keyboard accessibility for navigation
document.addEventListener('keydown', function(e) {
    // Escape key to exit navigation mode
    if (e.key === 'Escape') {
        document.activeElement.blur();
    }
    
    // Enter/Space for navigation elements
    if ((e.key === 'Enter' || e.key === ' ') && e.target.classList.contains('nav-dot')) {
        e.preventDefault();
        e.target.click();
    }
});

// Announce section changes for screen readers
function announceSection(index) {
    const announcement = `Section ${index + 1} of ${window.portfolioScrollSystem?.getTotalSections() || 6}`;
    
    // Create or update live region
    let liveRegion = document.getElementById('portfolio-live-region');
    if (!liveRegion) {
        liveRegion = document.createElement('div');
        liveRegion.id = 'portfolio-live-region';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.position = 'absolute';
        liveRegion.style.left = '-10000px';
        liveRegion.style.width = '1px';
        liveRegion.style.height = '1px';
        liveRegion.style.overflow = 'hidden';
        document.body.appendChild(liveRegion);
    }
    
    liveRegion.textContent = announcement;
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initStickyScrollSystem,
        initVideoSystem,
        initNavigationSystem,
        throttle,
        debounce
    };
}