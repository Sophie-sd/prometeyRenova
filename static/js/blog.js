// BLOG.JS - JavaScript для блогу

document.addEventListener('DOMContentLoaded', function () {
    // Навігація з прозорим хедером
    initScrollNavigation();

    // Анімація з'явлення карток
    initArticleAnimations();

    // Tracking читання статей
    initArticleTracking();
});

// Навігація з прозорим хедером
function initScrollNavigation() {
    const nav = document.querySelector('.main-navigation');

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset;

        if (scrollTop > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });
}

// Анімація з'явлення карток при скролі
function initArticleAnimations() {
    const articles = document.querySelectorAll('.blog-card');

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    articles.forEach((article, index) => {
        article.style.opacity = '0';
        article.style.transform = 'translateY(30px)';
        article.style.transition = `all 0.6s ease-out ${index * 0.1}s`;
        observer.observe(article);
    });
}

// Tracking читання статей для аналітики
function initArticleTracking() {
    const articleLinks = document.querySelectorAll('.article-link, .read-more-link');

    articleLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const articleTitle = this.closest('.blog-card')?.querySelector('.article-link')?.textContent?.trim();

            // Google Analytics tracking (якщо підключено)
            if (typeof gtag !== 'undefined') {
                gtag('event', 'article_click', {
                    article_title: articleTitle,
                    page_location: window.location.href
                });
            }
        });
    });
}

// Активний стан меню для блогу
function setActiveMenuLink() {
    const blogLink = document.querySelector('.nav-link[href*="blog"]');
    if (blogLink) {
        blogLink.classList.add('active');
    }
}

// Ініціалізація при завантаженні
setActiveMenuLink(); 