/**
 * BLOG.JS - Refactored v2.0
 * Без дублювань
 */

import { animateOnScroll } from '../core/observers.js';
import analytics from '../core/analytics.js';

class BlogPage {
    constructor() {
        this.init();
    }

    init() {
        // Анімації (централізовано)
        animateOnScroll('.blog-card, .popular-card');

        // Active menu link
        this.setActiveMenuLink();

        // Article click tracking вже в analytics.js
        // Специфічний tracking якщо потрібен
        this.setupBlogTracking();
    }

    setActiveMenuLink() {
        const blogLink = document.querySelector('.nav-link[href*="blog"]');
        blogLink?.classList.add('active');
    }

    setupBlogTracking() {
        // Tracking search
        const searchForm = document.querySelector('.search-form');
        searchForm?.addEventListener('submit', (e) => {
            const query = searchForm.querySelector('input[name="q"]')?.value;
            if (query) {
                analytics.trackSearch(query, 0); // Results count можна додати пізніше
            }
        });

        // Tracking category filters
        document.querySelectorAll('.category-filter').forEach(filter => {
            filter.addEventListener('click', () => {
                const category = filter.textContent.trim();
                analytics.trackFilter('category', category);
            });
        });
    }
}

// ===== AUTO INIT =====
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new BlogPage());
} else {
    new BlogPage();
}

