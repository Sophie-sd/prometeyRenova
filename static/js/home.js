/* =================================
   HOME PAGE JAVASCRIPT
   Scroll animations and interactions
   ================================= */

'use strict';

document.addEventListener('DOMContentLoaded', function() {
    console.log('🏠 Home page loaded');
    
    initScrollAnimations();
    initParallaxEffects();
    initCounterAnimations();
    initSmoothScrolling();
    
    console.log('✅ Home page initialized');
});

/* =================================
   SCROLL ANIMATIONS
   ================================= */

function initScrollAnimations() {
    const animatedElements = document.querySelectorAll(
        '.service-card, .feature-item, .project-preview-card, .badge'
    );
    
    if (!animatedElements.length) return;
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Add delay for staggered animation
                setTimeout(() => {
                    entry.target.classList.add('in-view');
                }, index * 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
    
    console.log(`📱 Scroll animations initialized for ${animatedElements.length} elements`);
}

/* =================================
   PARALLAX EFFECTS
   ================================= */

function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.hero-visual, .tech-stack');
    
    if (!parallaxElements.length) return;
    
    let ticking = false;
    
    function updateParallax() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        parallaxElements.forEach(element => {
            element.style.transform = `translateY(${rate}px)`;
        });
        
        ticking = false;
    }
    
    function requestParallaxUpdate() {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }
    
    // Only enable parallax on non-mobile devices and if user doesn't prefer reduced motion
    const isMobile = window.innerWidth <= 768;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (!isMobile && !prefersReducedMotion) {
        window.addEventListener('scroll', requestParallaxUpdate, { passive: true });
        console.log('🎭 Parallax effects enabled');
    } else {
        console.log('🎭 Parallax effects disabled (mobile or reduced motion)');
    }
}

/* =================================
   COUNTER ANIMATIONS
   ================================= */

function initCounterAnimations() {
    const counters = document.querySelectorAll('.stat-number');
    
    if (!counters.length) return;
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
    
    console.log(`🔢 Counter animations initialized for ${counters.length} counters`);
}

function animateCounter(element) {
    const target = parseInt(element.textContent);
    const duration = 2000; // 2 seconds
    const step = target / (duration / 16); // 60fps
    let current = 0;
    
    const timer = setInterval(() => {
        current += step;
        
        if (current >= target) {
            element.textContent = target + (element.textContent.includes('+') ? '+' : '');
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current) + (element.textContent.includes('+') ? '+' : '');
        }
    }, 16);
}

/* =================================
   SMOOTH SCROLLING
   ================================= */

function initSmoothScrolling() {
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href === '#') {
                e.preventDefault();
                return;
            }
            
            const targetId = href.substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                
                const headerHeight = document.querySelector('.header')?.offsetHeight || 0;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    console.log(`🔗 Smooth scrolling initialized for ${smoothScrollLinks.length} links`);
}

/* =================================
   HERO INTERACTIONS
   ================================= */

// Add hover effects to hero badges
document.addEventListener('DOMContentLoaded', function() {
    const badges = document.querySelectorAll('.badge');
    
    badges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.05)';
        });
        
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

/* =================================
   SERVICE CARDS INTERACTIONS
   ================================= */

function initServiceCardInteractions() {
    const serviceCards = document.querySelectorAll('.service-card');
    
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Add glow effect
            this.style.boxShadow = '0 20px 50px rgba(220, 20, 60, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            // Remove glow effect
            this.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.08)';
        });
    });
    
    console.log(`🎨 Service card interactions initialized for ${serviceCards.length} cards`);
}

// Initialize service card interactions when DOM is loaded
document.addEventListener('DOMContentLoaded', initServiceCardInteractions);

/* =================================
   PERFORMANCE OPTIMIZATIONS
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
   RESPONSIVE ADJUSTMENTS
   ================================= */

function handleResponsiveChanges() {
    const isMobile = window.innerWidth <= 768;
    const heroStats = document.querySelector('.hero-stats');
    
    if (isMobile && heroStats) {
        heroStats.style.flexDirection = 'column';
        heroStats.style.gap = '20px';
    } else if (heroStats) {
        heroStats.style.flexDirection = 'row';
        heroStats.style.gap = '40px';
    }
}

// Handle resize events
window.addEventListener('resize', debounce(handleResponsiveChanges, 250));

// Initial check
document.addEventListener('DOMContentLoaded', handleResponsiveChanges);

/* =================================
   ACCESSIBILITY IMPROVEMENTS
   ================================= */

// Add keyboard navigation for interactive elements
document.addEventListener('DOMContentLoaded', function() {
    const interactiveElements = document.querySelectorAll('.btn, .service-link, .contact-value');
    
    interactiveElements.forEach(element => {
        element.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    console.log(`♿ Accessibility improvements applied to ${interactiveElements.length} elements`);
});

/* =================================
   ERROR HANDLING
   ================================= */

// Global error handler for this page
window.addEventListener('error', function(e) {
    console.error('Home page error:', e.error);
    
    // Don't break the page functionality
    return false;
});

// Promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Home page promise rejection:', e.reason);
    e.preventDefault();
});

/* =================================
   PERFORMANCE MONITORING
   ================================= */

// Log page load performance
window.addEventListener('load', function() {
    if (window.performance && window.performance.timing) {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log(`📊 Home page loaded in ${loadTime}ms`);
    }
});

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initScrollAnimations,
        initParallaxEffects,
        initCounterAnimations,
        initSmoothScrolling,
        throttle,
        debounce
    };
}