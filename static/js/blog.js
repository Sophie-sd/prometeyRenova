/* BLOG PAGE JAVASCRIPT - PrometeyLabs */

'use strict';

document.addEventListener('DOMContentLoaded', function() {
    console.log('📝 Blog page loaded');
    
    initScrollAnimations();
    initSearchFunctionality();
    initCategoryFiltering();
    initNewsletterForm();
    
    console.log('✅ Blog page initialized');
});

/* =================================
   SCROLL ANIMATIONS
   ================================= */

function initScrollAnimations() {
    const animatedElements = document.querySelectorAll(
        '.category-card, .article-card, .related-link-card'
    );
    
    if (!animatedElements.length) return;
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('in-view');
                }, index * 50);
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
   SEARCH FUNCTIONALITY
   ================================= */

function initSearchFunctionality() {
    const searchForm = document.querySelector('.blog-search-form');
    const searchInput = document.querySelector('.search-input');
    
    if (!searchForm || !searchInput) return;
    
    // Real-time search highlighting
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length >= 2) {
            searchTimeout = setTimeout(() => {
                highlightSearchResults(query);
            }, 300);
        } else {
            clearHighlights();
        }
    });
    
    // Clear search button
    if (searchInput.value) {
        addClearButton();
    }
    
    searchInput.addEventListener('input', function() {
        if (this.value) {
            addClearButton();
        } else {
            removeClearButton();
        }
    });
    
    function addClearButton() {
        if (document.querySelector('.search-clear')) return;
        
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.className = 'search-clear';
        clearButton.innerHTML = '✕';
        clearButton.style.cssText = `
            position: absolute;
            right: 60px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: #666;
            cursor: pointer;
            font-size: 14px;
            padding: 5px;
        `;
        
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            searchInput.focus();
            removeClearButton();
            clearHighlights();
        });
        
        searchForm.querySelector('.search-input-wrapper').appendChild(clearButton);
    }
    
    function removeClearButton() {
        const clearButton = document.querySelector('.search-clear');
        if (clearButton) clearButton.remove();
    }
    
    function highlightSearchResults(query) {
        const articleCards = document.querySelectorAll('.article-card');
        const queryLower = query.toLowerCase();
        
        articleCards.forEach(card => {
            const title = card.querySelector('.article-title a')?.textContent.toLowerCase() || '';
            const excerpt = card.querySelector('.article-excerpt')?.textContent.toLowerCase() || '';
            
            if (title.includes(queryLower) || excerpt.includes(queryLower)) {
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            } else {
                card.style.opacity = '0.3';
                card.style.transform = 'scale(0.95)';
            }
        });
    }
    
    function clearHighlights() {
        const articleCards = document.querySelectorAll('.article-card');
        articleCards.forEach(card => {
            card.style.opacity = '';
            card.style.transform = '';
        });
    }
    
    console.log('🔍 Search functionality initialized');
}

/* =================================
   CATEGORY FILTERING
   ================================= */

function initCategoryFiltering() {
    const categoryCards = document.querySelectorAll('.category-card');
    
    categoryCards.forEach(card => {
        card.addEventListener('click', function(e) {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
        
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    console.log(`📂 Category filtering initialized for ${categoryCards.length} categories`);
}

/* =================================
   NEWSLETTER FORM
   ================================= */

function initNewsletterForm() {
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (!newsletterForm) return;
    
    const emailInput = newsletterForm.querySelector('input[name="email"]');
    
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            const email = this.value;
            const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
            
            if (email && !isValid) {
                this.style.borderLeft = '4px solid #dc3545';
            } else {
                this.style.borderLeft = '';
            }
        });
    }
    
    console.log('📧 Newsletter form initialized');
}

/* =================================
   ARTICLE INTERACTIONS
   ================================= */

document.addEventListener('DOMContentLoaded', function() {
    const articleCards = document.querySelectorAll('.article-card');
    
    articleCards.forEach(card => {
        // Keyboard navigation
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const link = this.querySelector('.article-title a');
                if (link) link.click();
            }
        });
        
        // Reading time color coding
        const readingTime = card.querySelector('.article-reading-time');
        if (readingTime) {
            const time = parseInt(readingTime.textContent);
            if (time > 10) {
                readingTime.style.color = '#dc3545';
            } else if (time > 5) {
                readingTime.style.color = '#ffc107';
            } else {
                readingTime.style.color = '#28a745';
            }
        }
    });
    
    console.log(`📖 Article interactions initialized for ${articleCards.length} articles`);
});

/* =================================
   ACCESSIBILITY
   ================================= */

document.addEventListener('keydown', function(e) {
    // Escape key to clear search
    if (e.key === 'Escape') {
        const searchInput = document.querySelector('.search-input');
        if (searchInput && searchInput === document.activeElement) {
            searchInput.value = '';
            searchInput.blur();
        }
    }
});

// Auto-focus search if coming from search results
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('search')) {
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.setSelectionRange(0, searchInput.value.length);
        }
    }
});

/* =================================
   ERROR HANDLING
   ================================= */

window.addEventListener('error', function(e) {
    console.error('Blog page error:', e.error);
    return false;
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Blog page promise rejection:', e.reason);
    e.preventDefault();
});

/* =================================
   PERFORMANCE MONITORING
   ================================= */

window.addEventListener('load', function() {
    if (window.performance && window.performance.timing) {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log(`📊 Blog page loaded in ${loadTime}ms`);
    }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initScrollAnimations,
        initSearchFunctionality,
        initCategoryFiltering,
        initNewsletterForm
    };
}