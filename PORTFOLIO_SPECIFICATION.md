# 📋 СПЕЦИФІКАЦІЯ СТОРІНКИ ПОРТФОЛІО

## 🎯 **ОПИС СТОРІНКИ:**

Сторінка портфоліо має демонструвати наші роботи з використанням **sticky scroll ефекту** - кожен проект "прилипає" до верху екрану при скролі.

## 🏗️ **СТРУКТУРА HTML:**

### **1. Hero секція:**
```html
<section class="portfolio-hero">
    <div class="hero-content">
        <h1 class="hero-title">СТВОРЕНІ НАМИ <span class="highlight">САЙТИ ПІД КЛЮЧ</span></h1>
        <p class="hero-description">Приклади наших робіт - сучасні веб-рішення для різних сфер бізнесу</p>
    </div>
</section>
```

### **2. Проектні секції (6 штук):**
```html
<section class="portfolio-projects">
    <!-- PROJECT 01 -->
    <div class="project-section" data-project="1">
        <div class="project-content">
            <h2 class="project-title">PROJECT 01</h2>
            <p class="project-description">Сучасний веб-сайт з інноваційним дизайном</p>
            <button class="project-button">Замовити подібний</button>
        </div>
    </div>
    
    <!-- Повторити для PROJECT 02-06 -->
</section>
```

## 🎨 **CSS СТИЛІ:**

### **Основні класи:**
- `.portfolio-hero` - повноекранна hero секція
- `.portfolio-projects` - контейнер для проектів
- `.project-section` - кожна sticky секція проекту
- `.project-content` - контент всередині секції
- `.project-title` - заголовок проекту
- `.project-description` - опис проекту
- `.project-button` - кнопка замовлення

### **Ключові CSS властивості:**
```css
.portfolio-hero {
    height: 100vh;
    height: calc(var(--vh, 1vh) * 100);
    background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
}

.project-section {
    position: sticky;
    top: 0;
    height: 100vh;
    height: calc(var(--vh, 1vh) * 100);
    background: #000;
    transition: all 0.3s ease;
}

.project-section.active {
    background: #111;
    border-bottom-color: #e14811;
}
```

## ⚡ **JAVASCRIPT ФУНКЦІОНАЛ:**

### **Основні функції:**
1. **`initStickyScroll()`** - основний sticky scroll ефект
2. **`initViewportHeight()`** - viewport height для iOS Safari
3. **`initIOSOptimizations()`** - оптимізації для iOS
4. **`initProjectButtons()`** - обробка кліків по кнопках

### **Логіка sticky scroll:**
```javascript
function updateActiveSection() {
    const scrollTop = window.pageYOffset;
    const heroHeight = document.querySelector('.portfolio-hero').offsetHeight;
    const scrollAfterHero = Math.max(0, scrollTop - heroHeight);
    const sectionHeight = window.innerHeight;
    const currentSectionIndex = Math.min(
        Math.floor(scrollAfterHero / sectionHeight),
        projectSections.length - 1
    );
    
    // Оновлюємо активну секцію
    projectSections.forEach((section, index) => {
        if (index === currentSectionIndex) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });
}
```

## 📱 **RESPONSIVE АДАПТАЦІЯ:**

### **Breakpoints:**
- **Десктоп**: >1024px - повні розміри
- **Планшети**: 768px-1024px - зменшені заголовки
- **Мобільні**: <768px - мобільна версія

### **Розміри заголовків:**
- **Hero**: 120px → 80px → 60px
- **Проекти**: 80px → 60px → 40px

## 🌐 **iOS SAFARI ОПТИМІЗАЦІЯ:**

### **Обов'язкові властивості:**
```css
@supports (-webkit-touch-callout: none) {
    .portfolio-hero,
    .project-section {
        height: 100vh;
        height: calc(var(--vh, 1vh) * 100);
        min-height: 100vh;
    }
    
    .project-section {
        -webkit-overflow-scrolling: touch;
        -webkit-transform: translateZ(0);
        will-change: transform;
    }
}
```

### **Safe areas для iPhone:**
```css
@supports (padding: max(0px)) {
    .portfolio-hero,
    .project-section {
        padding-left: max(20px, env(safe-area-inset-left) + 20px);
        padding-right: max(20px, env(safe-area-inset-right) + 20px);
    }
}
```

## 🎨 **КОЛЬОРОВА СИСТЕМА:**

### **Основна палітра:**
- **Червоний акцент**: #e14811
- **Чорний фон**: #000000
- **Темно-сірий**: #111111
- **Білий текст**: #FFFFFF
- **Сірий бордер**: #333333

## 📁 **СТРУКТУРА ФАЙЛІВ:**

```
templates/pages/portfolio.html    # HTML структура
static/css/portfolio.css         # Стилі портфоліо
static/js/portfolio.js          # JavaScript логіка
```

## 🚨 **ВАЖЛИВІ ПРИМІТКИ:**

### **Не використовувати:**
- ❌ Відео файли (викликають помилки)
- ❌ Складні анімації
- ❌ Конфліктуючі з base.js функції
- ❌ Зайві CSS змінні

### **Обов'язково:**
- ✅ Простий sticky scroll ефект
- ✅ Responsive дизайн
- ✅ iOS Safari оптимізація
- ✅ Чистий код без конфліктів

## 🔄 **ВІДНОВЛЕННЯ:**

Для відновлення сторінки портфоліо:
1. Створити `templates/pages/portfolio.html`
2. Створити `static/css/portfolio.css`
3. Створити `static/js/portfolio.js`
4. Додати посилання в навігацію
5. Протестувати sticky scroll ефект

---

**Автор специфікації**: AI Assistant  
**Дата створення**: 2024  
**Статус**: Файли видалено, специфікація збережена
