# 🎯 CALCULATOR FINAL STRUCTURE - Фінальне розташування

## ✅ СТРУКТУРА ВИПРАВЛЕНА

### Проблема була:
```html
<div class="calc-hero__grid" (position: relative)>
    <div class="calc-hero__info">текст</div>
    <div class="calc-hero__cta" (position: absolute, right: 0)>CTA</div>
</div>
```
❌ CTA позиціонувався відносно grid і не міг перекривати контент правильно

### Фінальне рішення:
```html
<div class="calc-hero__wrapper" (position: relative, max-width: 1200px)>
    <div class="calc-hero__content" (max-width: 650px)>текст</div>
    <div class="calc-hero__cta" (position: absolute, right: -20px)>CTA</div>
</div>
```
✅ CTA тепер позиціонується відносно wrapper і перекриває контент

---

## 📐 ВІЗУАЛЬНА СХЕМА

### Desktop (1200px wrapper):
```
┌──────────────── calc-hero__wrapper (max-width: 1200px) ────────────────┐
│                                                                         │
│  ┌─── calc-hero__content (max-width: 650px) ───┐                      │
│  │                                               │   ┌────────────┐    │
│  │  [КАЛЬКУЛЯТОР]                                │   │            │    │
│  │                                               │   │  CTA BOX   │    │
│  │  Розрахувати                                  ├───┤            │    │
│  │  вартість                                     │   │  ПРОЙТИ    │    │
│  │  проекту                                      │   │   ТЕСТ →   │    │
│  │                                               │   │            │    │
│  │  [01] AI агенти                               │   │ Отримайте  │    │
│  │  [02] Django                                  │   │  оцінку    │    │
│  │  [03] LLM моделі                              │   └────────────┘    │
│  │  [04] Тестування                              │        ↑            │
│  └───────────────────────────────────────────────┘  right: -20px      │
│                                                   перекриває контент   │
└─────────────────────────────────────────────────────────────────────────┘
         ← центрований margin: 0 auto →
```

---

## 🎯 КЛЮЧОВІ МОМЕНТИ

### 1. **Wrapper (calc-hero__wrapper)**
```css
.calc-hero__wrapper {
    max-width: 1200px;      /* обмежена ширина */
    margin: 0 auto;          /* центрування */
    position: relative;      /* для absolute CTA */
    min-height: 500px;       /* мінімальна висота */
}
```
**Призначення:** Контейнер що центрує весь блок та надає базу для absolute позиціонування

### 2. **Content (calc-hero__content)**
```css
.calc-hero__content {
    max-width: 650px;       /* обмежена ширина тексту */
    padding-top: clamp(20px, 4vw, 40px);
}
```
**Призначення:** Текстовий контент зліва, не розтягується на всю ширину

### 3. **CTA (calc-hero__cta)**
```css
.calc-hero__cta {
    position: absolute;      /* абсолютне позиціонування */
    right: -20px;            /* виходить за wrapper на 20px */
    top: 50%;                /* вертикально по центру */
    transform: translateY(-50%);
    width: 380px;
    z-index: 10;             /* зверху над контентом */
}
```
**Призначення:** Перекриває контент справа, створює ефект накладання

---

## 🔍 ДЕТАЛІ ПОЗИЦІОНУВАННЯ

### Right: -20px - ЧОМУ?
```
wrapper край →│                     CTA виходить за межі →
              │         ┌──────────┐
              │         │   CTA    │
       текст  ├─────────┤  BOX     │
              │         │          │
              │         └──────────┘
              ←─ 20px ─→
```
**Пояснення:** 
- `-20px` зсуває CTA трохи праворуч за межі wrapper
- Створює ефект "пливучого" блоку
- Перекриває частину контенту як на mockup

---

## 📱 RESPONSIVE BREAKPOINTS

### Великі екрани (≥1440px):
```css
.calc-hero__wrapper { max-width: 1400px; }
.calc-hero__content { max-width: 700px; }
.calc-hero__cta { width: 420px; right: 0; }
```

### Стандарт (1200-1439px):
```css
.calc-hero__wrapper { max-width: 1200px; }
.calc-hero__content { max-width: 650px; }
.calc-hero__cta { width: 380px; right: -20px; }
```

### Середні (1025-1199px):
```css
.calc-hero__wrapper { max-width: 1000px; }
.calc-hero__content { max-width: 550px; }
.calc-hero__cta { width: 340px; right: 0; }
```

### Планшети (≤1024px):
```css
.calc-hero__cta {
    position: static;      /* звичайне позиціонування */
    transform: none;
    width: 100%;
    margin-top: 60px;      /* знизу під контентом */
}
```

---

## ✅ ВІДПОВІДНІСТЬ MOCKUP

| Вимога | Статус |
|--------|--------|
| Контент зібраний до центру | ✅ `max-width: 1200px`, `margin: 0 auto` |
| Текст обмежений шириною | ✅ `max-width: 650px` |
| CTA перекриває контент справа | ✅ `position: absolute`, `right: -20px` |
| CTA по вертикалі по центру | ✅ `top: 50%`, `transform: translateY(-50%)` |
| CTA зверху над текстом | ✅ `z-index: 10` |
| Велика тінь для глибини | ✅ `box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15)` |

---

## 🔧 ЗМІНЕНІ КЛАСИ

### HTML:
- `.calc-hero__grid` → `.calc-hero__wrapper`
- `.calc-hero__info` → `.calc-hero__content`
- `.calc-hero__cta` - залишився без змін

### CSS:
Всі стилі оновлені відповідно до нової структури.

---

## 🎨 ВІЗУАЛЬНИЙ ЕФЕКТ

**До:**
```
[────────── Текст ──────────] [── CTA ──]
← весь екран розтягнутий →
```

**Після:**
```
      [───── Текст ─────]──┐
                         ┌─┴─ CTA ─┐
                         └──────────┘
     ← центрований блок →
```

---

## 📦 ФАЙЛИ ОНОВЛЕНО

1. ✅ `templates/pages/calculator.html` - нова структура HTML
2. ✅ `static/css/calculator.css` - оновлені стилі
3. ✅ `staticfiles/` - зібрано
4. ✅ Немає linter помилок

---

**Тепер layout точно як на mockup:**
- Контент центрований і не розтягнутий
- CTA box перекриває текстову частину справа
- Створює сучасний ефект накладання
- Адаптивний для всіх розмірів екранів

**Дата:** 14.10.2025  
**Версія:** 2.2 FINAL  
**Статус:** ✅ ГОТОВО

