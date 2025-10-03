# 🔧 ПЛАН РЕФАКТОРИНГУ ТА ОЧИЩЕННЯ КОДОВОЇ БАЗИ PrometeyRenova
## Детальний аналіз сеніор-розробника | Жовтень 2025

---

## 📊 ЗАГАЛЬНА СТАТИСТИКА ПРОЄКТУ

### Файлова структура:
- **HTML Templates**: 15 файлів
- **CSS Files**: 11 файлів (включно з компонентами)
- **JavaScript Files**: 10+ файлів
- **Python Backend**: Django структура
- **Загальний розмір**: ~15,000+ рядків коду

### Технологічний стек:
- **Backend**: Django 5.x + Python 3.13
- **Frontend**: Vanilla JS (сучасний ES6+)
- **Стилі**: Pure CSS з змінними
- **Відео**: HTML5 video з паралакс ефектами
- **Оптимізація**: MobileCore + VideoSystem (2025)

---

## 🔍 ВИЯВЛЕНІ ПРОБЛЕМИ

### 🚨 КРИТИЧНІ ПРОБЛЕМИ

#### 1. **ДУБЛЮВАННЯ VIEWPORT УПРАВЛІННЯ**
**Локація**: `base.js`, `mobile-core.js`, `portfolio.js`

**Проблема**:
```javascript
// base.js - рядки 60-102
setupViewportVars() { ... }

// mobile-core.js - рядки 88-125  
setupViewportSystem() { ... }

// portfolio.js - рядки 69-93
initViewportHeight() { ... }
```

**Вплив**: 
- Конфлікти при одночасному виконанні
- Множинні обробники resize/orientationchange
- Витрата ресурсів на дублікати

**Рейтинг критичності**: ⚠️⚠️⚠️⚠️⚠️ (5/5)

---

#### 2. **КОНФЛІКТ ВІДЕО СИСТЕМ**
**Локація**: `video-system.js` vs `portfolio.js`

**Проблема**:
```javascript
// portfolio.js відключає VideoSystem
window.VideoSystemDisabled = true;

// Але має власну логіку lazy loading відео
// Це призводить до дублювання та непередбачуваності
```

**Наслідки**:
- Різна логіка завантаження відео на різних сторінках
- Неможливість централізовано керувати відео
- Складність підтримки

**Рейтинг критичності**: ⚠️⚠️⚠️⚠️ (4/5)

---

#### 3. **ПОВТОРЮВАНІ ПАРАЛАКС СЕКЦІЇ В CSS**
**Локація**: `home.css`, `blog.css`, `events.css`, `developer.css`, `portfolio.css`

**Проблема**: Кожен файл має ідентичний код:
```css
/* Повторюється в 5+ файлах */
.hero-section {
    position: relative;
    width: 100%;
    min-height: 100vh;
    min-height: calc(var(--vh, 1vh) * 100);
    ...
}

.hero-section .video-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: -1;
}
```

**Обсяг дублювання**: ~200 рядків × 5 файлів = 1000 рядків

**Рейтинг критичності**: ⚠️⚠️⚠️⚠️ (4/5)

---

#### 4. **ГІГАНТСЬКИЙ base.css**
**Локація**: `base.css` - 1337+ рядків

**Проблема**:
- Містить все: reset, typography, layout, navigation, modals, forms, buttons
- Важко підтримувати та розуміти структуру
- Все завантажується на кожній сторінці навіть якщо не використовується

**Структура (фактична)**:
```
base.css (1337 рядків):
├── CSS Reset (30 рядків)
├── Color System (30 рядків)
├── Typography (60 рядків)
├── Layout (100 рядків)
├── Navigation (200 рядків) ❌ Можна винести
├── Mobile Menu (150 рядків) ❌ Можна винести
├── Buttons (120 рядків) ❌ Можна винести
├── Forms (200 рядків) ❌ Можна винести
├── Modals (180 рядків) ❌ Можна винести
├── Footer (100 рядків) ❌ Можна винести
└── Responsive (167+ рядків)
```

**Рейтинг критичності**: ⚠️⚠️⚠️ (3/5)

---

### ⚠️ СЕРЕДНЬОЇ ВАЖЛИВОСТІ

#### 5. **ВИКОРИСТАННЯ !important**
**Локація**: `base.css`, `blog.css`, `mobile-optimizations.css`

**Знайдено 11 випадків**:
```css
/* mobile-optimizations.css */
.reduce-motion *,
.reduce-motion *::before,
.reduce-motion *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
}

/* base.css */
@media (max-width: 767px) {
    .desktop-only {
        display: none !important;
    }
    .mobile-only {
        display: flex !important;
    }
}
```

**Аналіз**:
- ✅ У reduce-motion - виправдано (accessibility)
- ✅ У responsive utilities - виправдано
- ⚠️ Деякі можна замінити на специфічніші селектори

**Рейтинг критичності**: ⚠️⚠️ (2/5) - більшість виправдані

---

#### 6. **INLINE STYLES В HTML**
**Локація**: `templates/pages/events.html`

**Знайдено**:
```html
<button class="filter-btn" data-category="{{ category.slug }}"
    style="--category-color: {{ category.color }}">
    {{ category.name }}
</button>
```

**Проблема**: Динамічні кольори категорій
**Рішення**: Використовувати CSS класи або data-атрибути з CSS custom properties

**Рейтинг критичності**: ⚠️⚠️ (2/5)

---

#### 7. **ДУБЛЮВАННЯ iOS SAFARI ФІКСІВ**
**Локація**: Розпорошено по всіх файлах

**Проблема**: Фікси для iOS Safari написані в:
- `base.js` (старі фікси)
- `mobile-core.js` (нові фікси)
- `portfolio.js` (специфічні фікси)
- Кожен CSS файл має свої media queries

**Рейтинг критичності**: ⚠️⚠️ (2/5)

---

### ℹ️ НИЗЬКОЇ ПРІОРИТЕТНОСТІ

#### 8. **ЗАСТАРІЛІ КОМЕНТАРІ ТА CONSOLE.LOG**
```javascript
// Багато console.log для розробки
console.log('Portfolio: MobileCore already initialized');
console.log('VideoSystem initialized:', {...});
```

**Рішення**: Створити debug wrapper для продакшн/dev режимів

**Рейтинг критичності**: ⚠️ (1/5)

---

#### 9. **ВІДСУТНІСТЬ ЦЕНТРАЛІЗОВАНИХ КОНСТАНТ**
**Проблема**: Breakpoints, кольори, розміри дублюються:
```css
/* У кожному файлі */
@media (max-width: 767px) { ... }
@media (min-width: 768px) and (max-width: 1024px) { ... }
```

**Рейтинг критичності**: ⚠️ (1/5)

---

## 📋 ДЕТАЛЬНИЙ ПЛАН РЕФАКТОРИНГУ

### ФАЗА 1: ПІДГОТОВКА (1-2 години)

#### 1.1. Створення резервної копії
```bash
# Створити повну копію проєкту
git checkout -b refactoring/code-cleanup-2025
git add .
git commit -m "Pre-refactoring snapshot"
```

#### 1.2. Налаштування середовища тестування
- ✅ Переконатися що всі сторінки працюють
- ✅ Зробити скріншоти всіх сторінок (десктоп + мобільні)
- ✅ Записати відео основних інтеракцій

#### 1.3. Створення структури нових файлів
```
static/
├── css/
│   ├── core/                    # НОВА ПАПКА
│   │   ├── reset.css           # CSS Reset
│   │   ├── variables.css       # CSS змінні
│   │   ├── typography.css      # Типографіка
│   │   └── layout.css          # Layout utilities
│   ├── components/
│   │   ├── navigation.css      # З base.css
│   │   ├── buttons.css         # З base.css
│   │   ├── forms.css           # З base.css
│   │   ├── modals.css          # З base.css
│   │   ├── footer.css          # З base.css
│   │   ├── hero-parallax.css   # Універсальний паралакс
│   │   └── ... існуючі
│   └── pages/
│       └── ... існуючі файли
├── js/
│   ├── core/                    # НОВА ПАПКА
│   │   ├── config.js           # Конфігурація
│   │   ├── viewport-manager.js # Єдина viewport система
│   │   ├── video-manager.js    # Єдина відео система
│   │   └── debug.js            # Debug utilities
│   └── ... існуючі файли
```

---

### ФАЗА 2: CSS РЕСТРУКТУРИЗАЦІЯ (3-4 години)

#### 2.1. Розбити base.css на модулі

**КРОК 1**: Створити `css/core/reset.css`
```css
/* CSS Reset та базові стилі - перенести з base.css рядки 1-24 */
```

**КРОК 2**: Створити `css/core/variables.css`
```css
/* Всі CSS змінні - перенести з base.css рядки 27-58 */
:root {
    /* Colors */
    --color-red: #e14811;
    --color-black: #000000;
    --color-white: #FFFFFF;
    --color-beige: #090407;
    
    /* Typography Scale */
    --font-mega: clamp(60px, 12vw, 120px);
    --font-large: clamp(32px, 6vw, 50px);
    --font-medium: clamp(20px, 3vw, 24px);
    
    /* Spacing Scale */
    --space-xs: clamp(16px, 2vw, 20px);
    --space-sm: clamp(24px, 4vw, 40px);
    --space-md: clamp(40px, 6vw, 60px);
    --space-lg: clamp(60px, 8vw, 80px);
    --space-xl: clamp(80px, 12vw, 120px);
    
    /* Breakpoints (для JS) */
    --breakpoint-mobile: 767px;
    --breakpoint-tablet: 1024px;
    --breakpoint-desktop: 1200px;
}
```

**КРОК 3**: Створити `css/core/typography.css`
```css
/* Типографічна ієрархія - перенести з base.css рядки 60-110 */
```

**КРОК 4**: Створити `css/core/layout.css`
```css
/* Layout utilities - перенести з base.css рядки 112-150 */
```

**КРОК 5**: Створити компоненти
- `css/components/navigation.css` - з base.css рядки 151-400
- `css/components/buttons.css` - з base.css рядки 600-720
- `css/components/forms.css` - з base.css рядки 800-1000
- `css/components/modals.css` - з base.css рядки 1000-1180
- `css/components/footer.css` - з base.css залишок

#### 2.2. Створити універсальний hero-parallax компонент

**КРОК 1**: `css/components/hero-parallax.css`
```css
/* ===== УНІВЕРСАЛЬНИЙ ПАРАЛАКС HERO =====
 * Використовується на всіх сторінках з відео фоном
 * Замінює дублікати в home.css, blog.css, events.css, developer.css
 */

.hero-parallax {
    position: relative;
    width: 100%;
    min-height: 100vh;
    min-height: calc(var(--vh, 1vh) * 100);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 0;
}

/* Фіксоване відео */
.hero-parallax__video {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: -1;
}

/* Overlay */
.hero-parallax__overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.4);
    z-index: -1;
}

/* Контент */
.hero-parallax__content {
    position: relative;
    z-index: 3;
    width: 100%;
    padding: var(--space-xl) 0;
}

/* Responsive */
.hero-parallax__video--desktop {
    display: block;
}

.hero-parallax__video--mobile {
    display: none;
}

@media (max-width: 767px) {
    .hero-parallax__video--desktop {
        display: none;
    }
    
    .hero-parallax__video--mobile {
        display: block;
    }
}

/* Перша секція після hero */
.content-section--first {
    position: relative;
    background: #090407;
    z-index: 10;
    border-radius: 20px 20px 0 0;
    margin-top: -20px;
    box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.3);
    padding-top: 60px;
}

@media (max-width: 767px) {
    .content-section--first {
        border-radius: 16px 16px 0 0;
        margin-top: -16px;
        padding-top: 40px;
    }
}
```

**КРОК 2**: Видалити дублікати з:
- `home.css` - рядки 3-50 (замінити на використання hero-parallax)
- `blog.css` - рядки 3-70
- `events.css` - рядки 3-60
- `developer.css` - рядки 3-70

**Економія**: ~800 рядків CSS

#### 2.3. Оновити base.html з новою структурою

```html
<!-- CSS Core (порядок важливий!) -->
<link rel="stylesheet" href="{% static 'css/core/reset.css' %}">
<link rel="stylesheet" href="{% static 'css/core/variables.css' %}">
<link rel="stylesheet" href="{% static 'css/core/typography.css' %}">
<link rel="stylesheet" href="{% static 'css/core/layout.css' %}">

<!-- CSS Components -->
<link rel="stylesheet" href="{% static 'css/components/navigation.css' %}">
<link rel="stylesheet" href="{% static 'css/components/buttons.css' %}">
<link rel="stylesheet" href="{% static 'css/components/forms.css' %}">
<link rel="stylesheet" href="{% static 'css/components/modals.css' %}">
<link rel="stylesheet" href="{% static 'css/components/footer.css' %}">
<link rel="stylesheet" href="{% static 'css/components/hero-parallax.css' %}">
<link rel="stylesheet" href="{% static 'css/components/mobile-optimizations.css' %}">

<!-- Page specific CSS -->
{% block page_css %}{% endblock %}
```

---

### ФАЗА 3: JAVASCRIPT ЦЕНТРАЛІЗАЦІЯ (2-3 години)

#### 3.1. Створити єдину систему viewport management

**КРОК 1**: `js/core/viewport-manager.js`
```javascript
/**
 * VIEWPORT MANAGER - Єдина система управління viewport
 * Замінює дублікати в base.js, mobile-core.js, portfolio.js
 */

class ViewportManager {
    constructor() {
        this.device = null;
        this.listeners = [];
        this.initialized = false;
        
        // Інтеграція з MobileCore якщо доступний
        if (window.MobileCore) {
            this.device = window.MobileCore.getDevice();
        }
        
        this.init();
    }
    
    init() {
        if (this.initialized) return;
        
        this.setupViewportVars();
        this.setupEventListeners();
        
        this.initialized = true;
        this.dispatch('viewport:initialized');
    }
    
    setupViewportVars() {
        const setVars = () => {
            const vh = window.innerHeight * 0.01;
            const vw = window.innerWidth * 0.01;
            
            document.documentElement.style.setProperty('--vh', `${vh}px`);
            document.documentElement.style.setProperty('--vw', `${vw}px`);
            
            // iOS specific
            if (this.device?.iOS) {
                document.documentElement.style.setProperty(
                    '--mobile-vh', 
                    `${window.innerHeight}px`
                );
            }
            
            this.dispatch('viewport:changed', {
                vw: window.innerWidth,
                vh: window.innerHeight
            });
        };
        
        setVars();
        
        // Debounced resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(setVars, 100);
        }, { passive: true });
        
        // Orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(setVars, 100);
        });
    }
    
    setupEventListeners() {
        // Делегувати до MobileCore якщо доступний
        if (window.MobileCore) {
            document.addEventListener('mobilecore:viewportchange', (e) => {
                this.dispatch('viewport:changed', e.detail);
            });
        }
    }
    
    // Event system
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    off(event, callback) {
        if (!this.listeners[event]) return;
        this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
    
    dispatch(event, data = {}) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
        
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }
    
    // Public API
    getViewport() {
        return {
            width: window.innerWidth,
            height: window.innerHeight,
            isMobile: window.innerWidth <= 767,
            isTablet: window.innerWidth > 767 && window.innerWidth <= 1024,
            isDesktop: window.innerWidth > 1024
        };
    }
}

// Global instance
window.ViewportManager = new ViewportManager();
export default ViewportManager;
```

**КРОК 2**: Оновити `base.js`
```javascript
// Видалити setupViewportVars (рядки 60-102)
// Замінити на:

initWithMobileCore() {
    window.PrometeyPerformance.mark('init-start');
    
    this.device = window.MobileCore?.getDevice() || {};
    this.capabilities = window.MobileCore?.getCapabilities() || {};
    
    // Використовуємо ViewportManager замість власної логіки
    if (window.ViewportManager) {
        window.ViewportManager.on('viewport:changed', () => {
            this.handleResize();
        });
    }
    
    this.setupEventListeners();
    this.setupScrollNavigation();
    // ... решта
}
```

**КРОК 3**: Оновити `portfolio.js`
```javascript
// Видалити initViewportHeight (рядки 69-93)
// Замінити на:

function initViewportHeight() {
    // Використовуємо ViewportManager
    if (window.ViewportManager) {
        window.ViewportManager.on('viewport:changed', () => {
            setTimeout(updateActiveSection, 100);
        });
    }
    
    setTimeout(updateActiveSection, 100);
}
```

#### 3.2. Об'єднати відео системи

**КРОК 1**: Розширити `video-system.js`
```javascript
// Додати метод для portfolio-специфічної логіки

class VideoSystem {
    // ... існуючий код ...
    
    // НОВИЙ МЕТОД для portfolio sticky sections
    enablePortfolioMode() {
        this.portfolioMode = true;
        this.setupPortfolioVideoHandling();
    }
    
    setupPortfolioVideoHandling() {
        const projectSections = document.querySelectorAll('.project-section');
        
        projectSections.forEach((section, index) => {
            // Lazy load відео при наближенні секції
            this.observer.observe(section);
            
            // Відтворення тільки активної секції
            section.addEventListener('section:active', () => {
                this.playVideoForSection(section);
            });
            
            section.addEventListener('section:inactive', () => {
                this.pauseVideoForSection(section);
            });
        });
    }
    
    playVideoForSection(section) {
        const videos = section.querySelectorAll('video');
        videos.forEach(video => {
            if (video.readyState >= 2) {
                video.play().catch(() => {});
            }
        });
    }
    
    pauseVideoForSection(section) {
        const videos = section.querySelectorAll('video');
        videos.forEach(video => video.pause());
    }
}
```

**КРОК 2**: Спростити `portfolio.js`
```javascript
// Замість власної відео логіки (рядки 187-272)
// Використовувати VideoSystem:

function initPortfolio() {
    initViewportHeight();
    initStickyScroll();
    initIOSOptimizations();
    initProjectButtons();
    
    // Використовуємо VideoSystem в portfolio режимі
    if (window.VideoSystem) {
        window.VideoSystem.enablePortfolioMode();
    }
    
    console.log('Portfolio initialized with unified VideoSystem');
}

// Видалити функції:
// - loadVideoForSection
// - playVideoForActiveSection
// - pauseVideoForSection
// Економія: ~100 рядків
```

#### 3.3. Створити debug wrapper

**КРОК 1**: `js/core/debug.js`
```javascript
/**
 * DEBUG UTILITIES - Умовне логування для dev/prod
 */

class DebugManager {
    constructor() {
        this.enabled = this.isDevMode();
        this.levels = {
            log: true,
            warn: true,
            error: true,
            info: true
        };
    }
    
    isDevMode() {
        return window.location.hostname === 'localhost' ||
               window.location.hostname === '127.0.0.1' ||
               localStorage.getItem('prometey_debug') === 'true';
    }
    
    log(...args) {
        if (this.enabled && this.levels.log) {
            console.log('[Prometey]', ...args);
        }
    }
    
    warn(...args) {
        if (this.enabled && this.levels.warn) {
            console.warn('[Prometey]', ...args);
        }
    }
    
    error(...args) {
        if (this.levels.error) { // Завжди показувати помилки
            console.error('[Prometey]', ...args);
        }
    }
    
    info(...args) {
        if (this.enabled && this.levels.info) {
            console.info('[Prometey]', ...args);
        }
    }
    
    enable() {
        this.enabled = true;
        localStorage.setItem('prometey_debug', 'true');
    }
    
    disable() {
        this.enabled = false;
        localStorage.removeItem('prometey_debug');
    }
}

window.Debug = new DebugManager();
export default DebugManager;
```

**КРОК 2**: Замінити всі console.log
```javascript
// Було:
console.log('Portfolio: MobileCore already initialized');

// Стало:
Debug.log('Portfolio: MobileCore already initialized');
```

#### 3.4. Створити конфігураційний файл

**КРОК 1**: `js/core/config.js`
```javascript
/**
 * GLOBAL CONFIGURATION
 * Централізовані константи та налаштування
 */

export const Config = {
    // Breakpoints (синхронізовані з CSS)
    breakpoints: {
        mobile: 767,
        tablet: 1024,
        desktop: 1200
    },
    
    // Animations
    animations: {
        duration: {
            fast: 150,
            normal: 300,
            slow: 500
        },
        easing: {
            default: 'ease-out',
            bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
            smooth: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }
    },
    
    // Video settings
    video: {
        loadStrategy: 'lazy', // 'eager', 'lazy', 'progressive'
        autoplay: true,
        preload: {
            mobile: 'metadata',
            desktop: 'auto'
        }
    },
    
    // Performance
    performance: {
        debounceDelay: 100,
        throttleDelay: 16, // ~60fps
        lazyLoadMargin: '50px'
    },
    
    // Debug
    debug: {
        enabled: false, // Буде перевизначено DebugManager
        logLevel: 'info'
    }
};

// Helper functions
export const isMobile = () => window.innerWidth <= Config.breakpoints.mobile;
export const isTablet = () => window.innerWidth > Config.breakpoints.mobile && 
                               window.innerWidth <= Config.breakpoints.tablet;
export const isDesktop = () => window.innerWidth > Config.breakpoints.tablet;

window.Config = Config;
```

---

### ФАЗА 4: HTML ОПТИМІЗАЦІЯ (1 година)

#### 4.1. Виправити inline styles

**events.html - рядок 54**:
```html
<!-- БУЛО -->
<button class="filter-btn" data-category="{{ category.slug }}"
    style="--category-color: {{ category.color }}">

<!-- СТАЛО -->
<button class="filter-btn" data-category="{{ category.slug }}"
    data-color="{{ category.color }}">
```

**events.css - додати**:
```css
.filter-btn[data-color] {
    /* Використовуємо data-атрибут для CSS */
    border-color: attr(data-color color, var(--color-red));
}

/* Fallback для браузерів без підтримки attr() */
.filter-btn[data-color]:hover {
    background: var(--color-red);
    color: var(--color-white);
}

/* JS встановить CSS змінну при завантаженні */
```

**events.js - додати**:
```javascript
// Встановити кольори категорій через CSS змінні
document.querySelectorAll('.filter-btn[data-color]').forEach(btn => {
    const color = btn.getAttribute('data-color');
    if (color) {
        btn.style.setProperty('--btn-color', color);
    }
});
```

#### 4.2. Стандартизувати структуру hero секцій

**Створити компонент**: `templates/components/hero_parallax.html`
```html
{% load static %}
<!-- Універсальний компонент паралакс hero -->
<section class="hero-parallax {{ extra_classes }}">
    <!-- Desktop відео -->
    <video class="hero-parallax__video hero-parallax__video--desktop" 
           autoplay muted loop playsinline>
        <source src="{% static video_desktop %}" type="video/mp4">
    </video>
    
    <!-- Mobile відео -->
    <video class="hero-parallax__video hero-parallax__video--mobile" 
           autoplay muted loop playsinline>
        <source src="{% static video_mobile %}" type="video/mp4">
    </video>
    
    <!-- Overlay -->
    <div class="hero-parallax__overlay"></div>
    
    <!-- Контент -->
    <div class="hero-parallax__content">
        {% block hero_content %}{% endblock %}
    </div>
</section>
```

**Використання в home.html**:
```html
{% extends 'base.html' %}
{% load static %}

{% block content %}
{% include 'components/hero_parallax.html' with video_desktop='videos/desktop/main.mp4' video_mobile='videos/mobile/mainmobile.mp4' %}
    {% block hero_content %}
        <div class="container">
            <div class="hero-text text-center">
                <h1 class="text-mega color-red mb-lg">PrometeyLabs</h1>
                <p class="text-large color-white mb-xl">...</p>
            </div>
        </div>
    {% endblock %}
{% endinclude %}

<!-- Перша секція після hero -->
<section class="services-section content-section--first">
    ...
</section>
{% endblock %}
```

---

### ФАЗА 5: ВИДАЛЕННЯ !important (30 хвилин)

#### 5.1. Аналіз існуючих !important

**✅ ЗАЛИШИТИ (виправдані)**:
```css
/* mobile-optimizations.css - Accessibility */
.reduce-motion *,
.reduce-motion *::before,
.reduce-motion *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
}
/* Причина: Повинно перекривати всі інші анімації для accessibility */
```

**⚠️ МОЖНА ПОКРАЩИТИ**:
```css
/* base.css */
.desktop-only {
    display: none !important;
}
.mobile-only {
    display: flex !important;
}
```

**Замінити на**:
```css
/* Використовуємо більш специфічний контекст */
body .desktop-only {
    display: none;
}

body .mobile-only {
    display: flex;
}

/* Або через CSS classes на body */
.mobile-device .desktop-only {
    display: none;
}

.mobile-device .mobile-only {
    display: flex;
}
```

---

### ФАЗА 6: ТЕСТУВАННЯ (2-3 години)

#### 6.1. Функціональне тестування

**Чек-лист для кожної сторінки**:
- [ ] Hero відео завантажується та відтворюється
- [ ] Паралакс ефект працює при скролі
- [ ] Мобільне меню відкривається/закривається
- [ ] Модальні вікна відкриваються/закриваються
- [ ] Форми працюють коректно
- [ ] Навігація працює
- [ ] Кнопки мають правильні hover ефекти
- [ ] Viewport коректно розраховується на iOS Safari
- [ ] Немає console errors
- [ ] Анімації плавні

**Сторінки для тестування**:
1. Home (`/`)
2. Portfolio (`/portfolio/`)
3. Blog (`/blog/`)
4. Events (`/events/`)
5. Developer (`/developer/`)
6. Calculator (`/calculator/`)
7. Contacts (`/contacts/`)

#### 6.2. Responsive тестування

**Пристрої**:
- iPhone SE (375×667)
- iPhone 12 Pro (390×844)
- iPhone 14 Pro Max (430×932)
- iPad (768×1024)
- iPad Pro (1024×1366)
- Desktop 1920×1080

**Браузери**:
- Chrome (останній)
- Firefox (останній)
- Safari (останній)
- iOS Safari (iPhone 14+)
- Android Chrome

#### 6.3. Performance тестування

**Metrics to track**:
```javascript
// Додати в DebugManager
measurePerformance() {
    const perfData = performance.getEntriesByType('navigation')[0];
    const paintMetrics = performance.getEntriesByType('paint');
    
    return {
        pageLoad: perfData.loadEventEnd - perfData.fetchStart,
        domReady: perfData.domContentLoadedEventEnd - perfData.fetchStart,
        firstPaint: paintMetrics.find(m => m.name === 'first-paint')?.startTime,
        firstContentful: paintMetrics.find(m => m.name === 'first-contentful-paint')?.startTime
    };
}
```

**Цілі**:
- DOMContentLoaded: < 1000ms
- Load: < 2000ms
- First Contentful Paint: < 1500ms

#### 6.4. Візуальне тестування

**Інструменти**:
- Зробити скріншоти всіх сторінок
- Порівняти з оригінальними скріншотами
- Перевірити що немає візуальних регресій

---

### ФАЗА 7: ДОКУМЕНТАЦІЯ (1 година)

#### 7.1. Оновити README.md

```markdown
## 📁 Структура проєкту

### CSS Architecture

static/css/
├── core/                     # Базові системи
│   ├── reset.css            # CSS Reset
│   ├── variables.css        # CSS змінні (кольори, розміри, breakpoints)
│   ├── typography.css       # Типографічна система
│   └── layout.css           # Layout utilities
├── components/              # Переисполнительні компоненти
│   ├── navigation.css       # Header навігація
│   ├── buttons.css          # Кнопки всіх типів
│   ├── forms.css            # Форми та inputs
│   ├── modals.css           # Модальні вікна
│   ├── footer.css           # Footer
│   ├── hero-parallax.css    # Універсальний паралакс hero
│   └── mobile-optimizations.css  # Мобільні оптимізації
└── pages/                   # Сторінко-специфічні стилі
    ├── home.css
    ├── portfolio.css
    ├── blog.css
    └── ...

### JavaScript Architecture

static/js/
├── core/                    # Базові системи
│   ├── config.js           # Конфігурація та константи
│   ├── debug.js            # Debug utilities
│   ├── viewport-manager.js # Управління viewport
│   └── video-manager.js    # Управління відео
├── mobile-core.js          # Мобільні оптимізації
├── base.js                 # Базова функціональність
└── pages/                  # Сторінко-специфічні скрипти
    ├── home.js
    ├── portfolio.js
    └── ...

## 🎨 CSS Conventions

### BEM для компонентів
\`\`\`css
.hero-parallax { }              /* Block */
.hero-parallax__video { }       /* Element */
.hero-parallax__video--mobile { } /* Modifier */
\`\`\`

### CSS Custom Properties
\`\`\`css
/* Використовувати CSS змінні замість жорстко закодованих значень */
color: var(--color-red);
padding: var(--space-md);
font-size: var(--font-large);
\`\`\`

## 🔧 Development

### Debug Mode
\`\`\`javascript
// Увімкнути в консолі браузера
Debug.enable();

// Вимкнути
Debug.disable();
\`\`\`

### Performance Monitoring
\`\`\`javascript
// Перевірити performance metrics
Debug.log(window.PrometeyPerformance.marks);
\`\`\`
```

#### 7.2. Створити MIGRATION_GUIDE.md

```markdown
# 🚀 Міграційний посібник (2025 Refactoring)

## Що змінилося

### CSS Changes

#### ❌ Застаріло
\`\`\`html
<!-- Старий спосіб -->
<link rel="stylesheet" href="{% static 'css/base.css' %}">
\`\`\`

#### ✅ Новий підхід
\`\`\`html
<!-- Модульний підхід -->
<link rel="stylesheet" href="{% static 'css/core/reset.css' %}">
<link rel="stylesheet" href="{% static 'css/core/variables.css' %}">
<link rel="stylesheet" href="{% static 'css/core/typography.css' %}">
<link rel="stylesheet" href="{% static 'css/core/layout.css' %}">
<link rel="stylesheet" href="{% static 'css/components/navigation.css' %}">
<!-- ... інші компоненти ... -->
\`\`\`

### JavaScript Changes

#### ❌ Застаріло
\`\`\`javascript
// Власна viewport логіка в кожному файлі
function setupViewportVars() { ... }
\`\`\`

#### ✅ Новий підхід
\`\`\`javascript
// Використовувати ViewportManager
window.ViewportManager.on('viewport:changed', (data) => {
    console.log('Viewport changed:', data);
});
\`\`\`

### Hero Sections

#### ❌ Застаріло
\`\`\`html
<!-- Повторювати структуру в кожному template -->
<section class="hero-section">
    <video class="video-background desktop-video">...</video>
    <video class="video-background mobile-video">...</video>
    <div class="video-overlay"></div>
    ...
</section>
\`\`\`

#### ✅ Новий підхід
\`\`\`html
<!-- Використовувати компонент -->
{% include 'components/hero_parallax.html' with 
   video_desktop='videos/desktop/main.mp4' 
   video_mobile='videos/mobile/mainmobile.mp4' %}
   {% block hero_content %}
       <!-- Ваш контент -->
   {% endblock %}
{% endinclude %}
\`\`\`

## Backwards Compatibility

Всі зміни зворотно сумісні. Старий код продовжить працювати, але рекомендується оновитися.
```

#### 7.3. Додати коментарі в код

```javascript
/**
 * VIEWPORT MANAGER (2025)
 * 
 * Централізована система управління viewport для всього додатка.
 * Замінює дублікати viewport логіки з base.js, mobile-core.js, portfolio.js.
 * 
 * @example
 * // Підписатися на зміни viewport
 * ViewportManager.on('viewport:changed', (data) => {
 *     console.log('New viewport:', data.vw, data.vh);
 * });
 * 
 * // Отримати поточний viewport
 * const viewport = ViewportManager.getViewport();
 * if (viewport.isMobile) {
 *     // Mobile specific code
 * }
 * 
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Visual_Viewport_API
 */
```

---

## 📊 ОЧІКУВАНІ РЕЗУЛЬТАТИ

### Метрики покращення

#### Розмір коду:
- **CSS**: -800 рядків (видалення дублікатів паралакс секцій)
- **JavaScript**: -200 рядків (централізація viewport та відео логіки)
- **HTML**: +50 рядків (нові компоненти)
- **Загальне зменшення**: ~950 рядків (-6% від загального об'єму)

#### Продуктивність:
- **Менше CSS для парсингу**: base.css 1337 → розділено на 4 core + 6 components = менше reflows
- **Менше JS execution**: Видалення дублікатів viewport handlers
- **Кращий caching**: Модульні файли краще кешуються браузером

#### Підтримуваність:
- ✅ **DRY принцип**: Немає дублювання коду
- ✅ **Separation of Concerns**: Логіка розділена по відповідальності
- ✅ **Single Responsibility**: Кожен модуль має одну задачу
- ✅ **Легше тестувати**: Модулі можна тестувати окремо
- ✅ **Легше розуміти**: Зрозуміла структура папок та файлів

#### Розширюваність:
- ✅ Легко додавати нові компоненти
- ✅ Легко модифікувати існуючі без ризику зламати інше
- ✅ Централізовані налаштування в одному місці

---

## ⚠️ РИЗИКИ ТА MITIGATION

### Ризик 1: Поломка існуючої функціональності
**Ймовірність**: Середня  
**Вплив**: Критичний  
**Mitigation**:
- Створити резервну копію перед початком
- Тестувати кожну зміну окремо
- Використовувати git branches
- Мати можливість швидкого rollback

### Ризик 2: CSS порушення через зміну порядку завантаження
**Ймовірність**: Низька  
**Вплив**: Середній  
**Mitigation**:
- Ретельно продумати порядок підключення CSS
- Тестувати візуально після кожної зміни
- Використовувати CSS specificity правильно

### Ризик 3: JavaScript помилки через зміну глобальних об'єктів
**Ймовірність**: Низька  
**Вплив**: Середній  
**Mitigation**:
- Зберігати backwards compatibility
- Старі змінні залишити як alias до нових
- Поступова міграція

### Ризик 4: Регресія на iOS Safari
**Ймовірність**: Середня  
**Вплив**: Високий  
**Mitigation**:
- Тестувати на реальних iOS пристроях
- Зберегти всі iOS Safari фікси
- Використовувати MobileCore як єдине джерело iOS логіки

---

## 🎯 КРИТЕРІЇ УСПІХУ

### Технічні критерії:
- [ ] Всі сторінки працюють як до рефакторингу
- [ ] Немає console errors
- [ ] Немає візуальних регресій
- [ ] Всі відео завантажуються та відтворюються
- [ ] iOS Safari працює коректно
- [ ] Performance метрики не погіршилися
- [ ] Код проходить linting без помилок

### Якісні критерії:
- [ ] Код легше читається та розуміється
- [ ] Немає дублювання логіки
- [ ] Структура файлів логічна та зрозуміла
- [ ] Додавання нових фічей стало простішим
- [ ] Документація оновлена

### Метрики:
- [ ] Розмір коду зменшився на 5%+
- [ ] Кількість !important зменшилась
- [ ] Відсутні inline styles (окрім Django template variables)
- [ ] Viewport handlers: 3 → 1
- [ ] Відео логіка: 2 системи → 1 система

---

## 📅 TIMELINE

### День 1 (6-8 годин):
- ✅ Фаза 1: Підготовка (1-2 години)
- ✅ Фаза 2: CSS реструктуризація (3-4 години)
- ✅ Фаза 3: Початок JavaScript централізації (2 години)

### День 2 (4-5 годин):
- ✅ Фаза 3: Завершення JavaScript централізації (1-2 години)
- ✅ Фаза 4: HTML оптимізація (1 година)
- ✅ Фаза 5: Видалення !important (30 хвилин)
- ✅ Фаза 6: Початок тестування (1-2 години)

### День 3 (3-4 години):
- ✅ Фаза 6: Завершення тестування (2-3 години)
- ✅ Фаза 7: Документація (1 година)

**Загальний час**: 13-17 годин роботи

---

## 🔄 ROLLBACK PLAN

Якщо щось піде не так:

### Швидкий rollback (< 5 хвилин):
```bash
# Повернутися до попереднього коміту
git reset --hard HEAD~1

# Або до конкретного коміту
git reset --hard <commit-hash>

# Скасувати всі зміни
git checkout main
```

### Частковий rollback:
```bash
# Відмінити зміни в конкретному файлі
git checkout HEAD -- path/to/file.css

# Відмінити всі CSS зміни
git checkout HEAD -- static/css/

# Відмінити всі JS зміни  
git checkout HEAD -- static/js/
```

### Backup файли:
- Створити `_backup` папку з копіями всіх файлів перед зміною
- Зберігати оригінальний `base.css` як `base.css.backup`
- Можливість швидко замінити назад

---

## 📝 ВИСНОВОК

Цей рефакторинг зробить кодову базу:
- **Чистішою**: Без дублікатів та конфліктів
- **Швидшою**: Оптимізовано завантаження та виконання
- **Зрозумілішою**: Логічна структура файлів
- **Підтримуванішою**: Легше вносити зміни
- **Безпечнішою**: Централізоване управління критичними системами

**Всі зміни будуть зворотно сумісними та не порушать існуючу функціональність.**

---

**Автор**: Сеніор розробник  
**Дата**: Жовтень 2025  
**Версія**: 1.0

