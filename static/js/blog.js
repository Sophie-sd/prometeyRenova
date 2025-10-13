/**
 * BLOG.JS - Blog page specific logic
 * Використовує: base.js (scroll navigation), VideoSystem
 * БЕЗ дублювань
 */

document.addEventListener('DOMContentLoaded', () => {
    initArticleAnimations();
    initArticleTracking();
    setActiveMenuLink();
});

// ===== ARTICLE ANIMATIONS =====
function initArticleAnimations() {
    const articles = document.querySelectorAll('.blog-card, .popular-card');
    if (articles.length === 0) return;
    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    articles.forEach(article => observer.observe(article));
}

// ===== ANALYTICS =====
function initArticleTracking() {
    const articleLinks = document.querySelectorAll('.article-link, .read-more-link');

    articleLinks.forEach(link => {
        link.addEventListener('click', () => {
            const card = link.closest('.blog-card');
            const title = card?.querySelector('.article-link')?.textContent?.trim();

            if (title && typeof gtag !== 'undefined') {
                gtag('event', 'article_click', {
                    article_title: title,
                    page_location: window.location.href
                });
            }
        });
    });
}

// ===== ACTIVE MENU =====
function setActiveMenuLink() {
    const blogLink = document.querySelector('.nav-link[href*="blog"]');
    blogLink?.classList.add('active');
}
