// Theme init — runs synchronously before render to avoid flash of wrong theme.
// Default is dark; persisted in localStorage under key "admin-theme".
(function () {
    const stored = localStorage.getItem('admin-theme');
    if (stored === 'light') {
        document.documentElement.classList.remove('dark');
    } else {
        document.documentElement.classList.add('dark');
    }
}());

// Inject theme toggle button after DOM is ready.
document.addEventListener('DOMContentLoaded', function () {
    const btn = document.createElement('button');
    btn.className = 'admin-theme-toggle';
    btn.setAttribute('aria-label', 'Змінити тему');
    btn.setAttribute('title', 'Змінити тему');
    btn.setAttribute('type', 'button');

    const updateIcon = function () {
        btn.textContent = document.documentElement.classList.contains('dark') ? '☀' : '🌙';
    };
    updateIcon();

    btn.addEventListener('click', function () {
        const html = document.documentElement;
        if (html.classList.contains('dark')) {
            html.classList.remove('dark');
            localStorage.setItem('admin-theme', 'light');
        } else {
            html.classList.add('dark');
            localStorage.setItem('admin-theme', 'dark');
        }
        updateIcon();
    });

    // Place in Unfold topbar; fall back to body if selector changes between versions.
    const target =
        document.querySelector('[data-django-admin-topbar]') ||
        document.querySelector('.flex.items-center.gap-2') ||
        document.querySelector('header') ||
        document.getElementById('header') ||
        document.body;

    target.appendChild(btn);
});
