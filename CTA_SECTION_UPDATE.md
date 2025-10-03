# 🎬 CTA SECTION WITH VIDEO BACKGROUND

## Зміни

### Розділення Services Section

**Було:** Одна секція `.services-section` з CTA блоком всередині

**Стало:** Дві окремі секції:
1. **`.services-section`** - тільки картки послуг
2. **`.cta-section`** - окрема секція з відео фоном

---

## Структура

### 1. Services Section (Послуги)
```html
<section class="services-section">
    <!-- Картки послуг -->
    <div class="services-grid">
        <div class="service-card">...</div>
        <!-- 4 картки -->
    </div>
</section>
```

**Стилі:**
- Темний фон `#090407`
- Перша секція після hero з rounded top
- `z-index: 10` - поверх відео
- Border-radius: 20px (desktop), 16px (mobile)

---

### 2. CTA Section (Заклик до дії)
```html
<section class="cta-section">
    <!-- Фіксоване відео -->
    <video class="video-background desktop-video">
        <source src="main.mp4" type="video/mp4">
    </video>
    <video class="video-background mobile-video">
        <source src="mainmobile.mp4" type="video/mp4">
    </video>
    
    <!-- Overlay -->
    <div class="video-overlay"></div>
    
    <!-- Контент -->
    <div class="cta-content">
        <h2>Готові почати?</h2>
        <p>Зв'яжіться з нами...</p>
        <div class="cta-buttons">
            <a href="..." class="btn">Розрахувати вартість</a>
            <a href="..." class="btn">Telegram консультація</a>
        </div>
    </div>
</section>
```

---

## CSS Стилі

### CTA Section з паралакс ефектом

```css
.cta-section {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    z-index: 0;
}

/* Фіксоване відео */
.cta-section .video-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    object-fit: cover;
}

/* Фіксований overlay */
.cta-section .video-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    z-index: -1;
}
```

### Контент

```css
.cta-content {
    position: relative;
    z-index: 3;
    max-width: 800px;
    text-align: center;
}

.cta-content h2 {
    font-size: 80px;  /* Desktop */
    font-weight: 700;
    color: white;
    text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
}

.cta-content p {
    font-size: 20px;
    color: white;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
}
```

---

## Мобільна адаптація

```css
@media (max-width: 767px) {
    .cta-content h2 {
        font-size: 48px;
        letter-spacing: -1px;
    }
    
    .cta-content p {
        font-size: 16px;
    }
    
    .cta-buttons {
        flex-direction: column;
    }
    
    .cta-buttons .btn {
        width: 100%;
    }
}
```

---

## Особливості

### ✅ Паралакс ефект
- Відео залишається фіксованим на фоні
- Контент скролиться поверх відео
- Той самий ефект як на hero секції

### ✅ Відео оптимізація
- Desktop: `main.mp4`
- Mobile: `mainmobile.mp4`
- Автопрогравання з loop
- Оптимізація для iOS Safari

### ✅ Чистий код
- Без `!important`
- Без inline стилів
- Без дублювань
- Правильний CSS каскад

### ✅ Z-Index ієрархія
```
-1  → CTA відео та overlay (фон)
0   → CTA section (скролиться)
3   → CTA контент (текст та кнопки)
10  → Services section (поверх hero відео)
```

---

## JavaScript

Не потрібні зміни в JS - функція `initVideoSystem()` автоматично знаходить всі відео за класом `.video-background` і налаштовує їх:

```javascript
function initVideoSystem() {
    const videos = document.querySelectorAll('.video-background');
    videos.forEach(video => {
        // Автоплей, loop, обробка помилок
    });
}
```

---

## Результат

🎬 **Hero Section** → Відео фон (паралакс)
📦 **Services Section** → Темна секція з картками
🎯 **CTA Section** → Відео фон (паралакс) + заклик до дії
📄 **Footer** → Темний footer

Всі секції плавно скроляться з паралакс ефектом!

