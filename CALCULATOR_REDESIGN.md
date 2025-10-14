# 🎨 CALCULATOR REDESIGN - Документація

## ✅ ЩО ЗРОБЛЕНО

Повністю переписано блок калькулятора з сучасним мінімалістичним дизайном згідно STYLE.MDC.

### 📋 Зміни в HTML (calculator.html)

**Було:**
- Стандартна сітка 70/30 з benefits-list та емоджі
- Звичайна кнопка "Розпочати тест"
- Класи без БЕМ методології

**Стало:**
- **Асиметричний layout 60/40** - ліворуч великий заголовок + пронумеровані переваги, праворуч CTA
- **ВЕЛИКА кнопка "ПРОЙТИ ТЕСТ"** - мінімум 72px висотою, великий текст, анімація стрілки
- **БЕМ методологія** - всі класи з префіксом `calc-`
- **Без емоджі** - замість них номери 01-04 в помаранчевих квадратах
- **Типографічна домінанта** - величезний заголовок (до 96px)

### 🎨 Зміни в CSS (calculator.css)

**Видалено:**
- ❌ Всі емоджі (⚡, 🔧, 🤖, ✅, 🚀, ⌘, ⟲)
- ❌ Дублювання стилів
- ❌ Використання `!important`
- ❌ Inline styles
- ❌ Старі класи (.calculator-info, .info-content, .benefits-list, .cta-sidebar)

**Додано:**
- ✅ Повний БЕМ набір класів (calc-hero, calc-hero__grid, calc-benefit, calc-cta-btn)
- ✅ Асиметричний grid (60/40)
- ✅ Великі акцентні кнопки з анімацією
- ✅ Мінімалістичний дизайн з білими картками
- ✅ Номери замість емоджі
- ✅ Gradient overlay на hover
- ✅ `:has()` селектор для radio кнопок (виправлено помилку)
- ✅ Responsive для всіх пристроїв (desktop/tablet/mobile)

### ⚙️ Зміни в JS (calculator.js)

**Оновлено:**
- Селектор `.question` → `.calc-question`
- Всі інші селектори залишилися сумісними

---

## 🎯 КЛЮЧОВІ ОСОБЛИВОСТІ ДИЗАЙНУ

### Hero Section
```
┌─────────────────────────────────────────┐
│ [Калькулятор]                          │
│                                         │
│ Розрахувати     ┌──────────────────┐  │
│ вартість        │ 5 простих питань │  │
│ проекту         │                  │  │
│                 │  ПРОЙТИ ТЕСТ →   │  │
│ [01] AI агенти  │                  │  │
│ [02] Django     │ Отримайте оцінку │  │
│ [03] LLM моделі │ за 2 хвилини    │  │
│ [04] Тестування └──────────────────┘  │
└─────────────────────────────────────────┘
```

### Test Section
- Білі картки з помаранчевою лівою межею
- Номери питань 01-05
- Radio кнопки з hover ефектами
- Smooth scroll між питаннями
- Progress bar (створюється JS)

---

## 📱 RESPONSIVE BREAKPOINTS

### Desktop (1025px+)
- Grid 60/40
- Великий заголовок (96px)
- Кнопка CTA (72px висота)

### Tablet (768px-1024px)
- Grid 1 колонка
- CTA по центру
- Заголовок (72px)

### Mobile (<767px)
- Все в 1 колонку
- Заголовок (48px)
- Кнопка (64px висота)
- Input font-size: 16px (запобігає zoom в iOS)

---

## 🔧 ТЕХНІЧНІ ДЕТАЛІ

### БЕМ Структура класів:
```
calc-hero
├── calc-hero__grid
├── calc-hero__info
│   ├── calc-hero__label
│   ├── calc-hero__title
│   └── calc-hero__benefits
│       └── calc-benefit
│           ├── calc-benefit__number
│           └── calc-benefit__text
└── calc-hero__cta
    └── calc-cta-box
        ├── calc-cta-box__subtitle
        ├── calc-cta-btn
        │   ├── calc-cta-btn__text
        │   └── calc-cta-btn__arrow
        └── calc-cta-box__note

calc-test (hidden спочатку)
├── calc-test__wrapper
├── calc-test__header
├── calc-form
│   ├── calc-question (x5)
│   │   ├── calc-question__header
│   │   │   ├── calc-question__number
│   │   │   └── calc-question__title
│   │   └── calc-options
│   │       └── calc-option (x4-5)
│   │           ├── input[type="radio"]
│   │           └── calc-option__text
│   └── calc-user-data
│       ├── calc-user-data__fields
│       │   └── calc-field (x2)
│       │       ├── calc-field__label
│       │       └── calc-field__input
│       └── calc-submit-btn
│           └── calc-submit-btn__text
```

### CSS Змінні (використовуються з core/variables.css):
- `--color-brand-orange`: #E65100
- `--color-beige`: #F5F1ED
- `--color-white`: #FFFFFF
- `--color-black`: #000000
- `--font-large`: clamp(32px, 6vw, 50px)
- `--space-xl`: clamp(80px, 12vw, 120px)

### Анімації:
- `calc-loading-spin` - для loading стану
- Hover ефекти: translateY(-2px), box-shadow
- Gradient overlay на кнопках
- Smooth scroll між питаннями

---

## ✅ ЧЕКЛИСТ ВІДПОВІДНОСТІ

- ✅ БЕЗ !important
- ✅ БЕЗ inline styles
- ✅ БЕЗ inline scripts
- ✅ БЕЗ емоджі
- ✅ БЕМ методологія
- ✅ Класи замість ID (крім form inputs)
- ✅ Асиметричний дизайн (60/40)
- ✅ Типографічна домінанта (великий заголовок)
- ✅ Мінімалізм з акцентами
- ✅ Контрастність (білі картки на бежевому)
- ✅ Великі відступи
- ✅ Responsive (mobile-first)
- ✅ iOS Safari оптимізації
- ✅ Accessibility (semantic HTML)
- ✅ Performance (CSS animations замість JS)

---

## 🚀 ЯК ТЕСТУВАТИ

1. **Desktop (>1024px):**
   - Перевірити асиметричний layout 60/40
   - Hover ефекти на кнопках
   - Анімація стрілки на CTA

2. **Tablet (768-1024px):**
   - Grid перетворюється в 1 колонку
   - CTA центрується

3. **Mobile (<767px):**
   - Всі елементи в 1 колонку
   - Кнопки зручного розміру (56-64px)
   - Текст читабельний
   - Input не викликає zoom (16px)

4. **Функціональність:**
   - Натиснути "ПРОЙТИ ТЕСТ" → показується форма
   - Вибрати відповідь → smooth scroll до наступного питання
   - Progress bar оновлюється
   - Після всіх відповідей → фокус на поля імені/телефону
   - Submit → відправка форми через base.js

---

## 📝 ЗАЛИШЕНІ БЕЗ ЗМІН

- ✅ Логіка тесту (питання, відповіді A-E)
- ✅ JavaScript обробка (збереження в sessionStorage)
- ✅ Form submission (через base.js)
- ✅ CSRF токен
- ✅ Progress bar логіка
- ✅ Auto-scroll до наступного питання

---

## 🔍 ВИПРАВЛЕНІ КОНФЛІКТИ

1. **CSS selector для radio buttons:**
   - Було: `.options input[type="radio"]:checked+span` (НЕ ПРАЦЮВАВ)
   - Стало: `.calc-option:has(input[type="radio"]:checked)` (ПРАЦЮЄ)

2. **Видалені дублікати:**
   - Старі класи (.calculator-info, .benefits-list) більше не конфліктують
   - БЕМ класи унікальні та ізольовані

3. **Виправлені селектори в JS:**
   - `.question` → `.calc-question`

---

## 📦 ФАЙЛИ ЩО ЗМІНИЛИСЯ

1. `templates/pages/calculator.html` - повністю переписано
2. `static/css/calculator.css` - повністю переписано
3. `static/js/calculator.js` - оновлено селектори
4. Статичні файли зібрано: `python3 manage.py collectstatic`

---

**Дата оновлення:** 14.10.2025  
**Версія:** 2.0  
**Статус:** ✅ ГОТОВО

