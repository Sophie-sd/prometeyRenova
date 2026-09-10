# Kontur+ — Copy-paste UI Snippets

Реальний CSS з `static/css/components-*.css` + мінімальний HTML.  
Підключи спочатку [css/tokens.css](css/tokens.css) і [css/base.css](css/base.css), або встав фрагменти нижче після токенів.

---

## Buttons

### HTML

```html
<button class="btn btn--primary" type="button">Замовити розрахунок</button>
<button class="btn btn--dark" type="button">Детальніше</button>
<button class="btn btn--ghost" type="button">Дивитись пакети</button>
<a class="btn btn--primary btn--pill" href="tel:+380000000000">+380 …</a>
<button class="btn btn--ghost btn--on-dark" type="button">На темному</button>
<button class="btn btn--primary btn--block" type="submit">Надіслати</button>
```

### CSS (канон)

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 50px;
  min-width: 44px;
  padding: 0.875rem 1.625rem;
  border: 1px solid transparent;
  border-radius: var(--radius);
  font-size: 0.9375rem;
  font-weight: 500;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: background var(--dur) var(--ease), border-color var(--dur) var(--ease),
    color var(--dur) var(--ease), opacity var(--dur) var(--ease),
    transform var(--dur) var(--ease);
  -webkit-tap-highlight-color: transparent;
  text-align: center;
}
.btn:disabled { opacity: 0.55; cursor: not-allowed; }
.btn--primary { background: var(--accent); color: var(--on-accent); }
.btn--primary:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
}
.btn--dark { background: var(--ink); color: var(--cream); }
.btn--dark:hover:not(:disabled) { background: #33383c; }
.btn--ghost {
  background: transparent;
  border-color: var(--border);
  color: var(--ink);
}
.btn--ghost:hover:not(:disabled) {
  border-color: var(--accent-mark);
  background: #fbfaf8;
}
.btn--block { width: 100%; }
.btn--pill {
  border-radius: var(--radius-pill);
  min-height: 46px;
  padding: 0.75rem 1.375rem;
  font-size: 0.875rem;
  font-weight: 600;
}
.btn--on-dark {
  border-color: rgba(247, 246, 244, 0.34);
  color: var(--cream);
  background: transparent;
}
.btn--on-dark:hover:not(:disabled) {
  border-color: var(--cream);
  background: rgba(247, 246, 244, 0.06);
  color: var(--cream);
}
```

---

## Form inputs

### HTML

```html
<div class="field">
  <label class="field__label" for="name">Імʼя</label>
  <input class="field__input" id="name" name="name" type="text" autocomplete="name" />
</div>

<div class="field field--error">
  <label class="field__label" for="phone">Телефон</label>
  <input class="field__input" id="phone" name="phone" type="tel" inputmode="tel" />
  <span class="field__hint">Перевірте формат номера</span>
</div>

<label class="checkbox">
  <input type="checkbox" name="privacy" required />
  <span>Погоджуюсь з <a href="/privacy">політикою конфіденційності</a></span>
</label>
```

### CSS (канон)

```css
.field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin-bottom: 1rem;
}
.field__label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--muted);
}
.field__input {
  min-height: 48px;
  width: 100%;
  padding: 0.75rem 0.875rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  transition: border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease);
}
.field__input:focus {
  outline: none;
  border-color: var(--accent-mark);
  box-shadow: 0 0 0 3px var(--accent-soft);
}
.field--error .field__input {
  border-color: var(--error);
  box-shadow: 0 0 0 3px var(--error-soft);
}
.field__hint { font-size: 0.8125rem; color: var(--muted); }
.field--error .field__hint { color: var(--error); }

.checkbox {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  font-size: 0.875rem;
  color: var(--muted);
  line-height: 1.45;
  margin: 0.5rem 0 1.25rem;
}
.checkbox input {
  width: 20px;
  height: 20px;
  min-width: 20px;
  margin-top: 2px;
  accent-color: var(--accent-mark);
}
.checkbox a {
  color: var(--ink);
  text-decoration: underline;
  text-underline-offset: 2px;
}
```

---

## Package card

### HTML

```html
<article class="card card--pkg">
  <div class="card__panel">
    <div class="card__top">
      <p class="card__index mono">01</p>
      <h3 class="card__title">Comfort</h3>
      <p class="card__desc">Базовий пакет під ключ</p>
    </div>
    <p class="card__price">
      <span class="card__price-value">460</span>
      <span class="card__price-unit">$/м²</span>
    </p>
    <ul class="card__list">
      <li>Дизайн-проєкт</li>
      <li>Матеріали</li>
      <li>Роботи та здача</li>
    </ul>
    <button class="card__cta" type="button" data-modal="lead">Обрати</button>
  </div>
</article>

<!-- Recommended (lime fill) -->
<article class="card card--pkg card--rec">…той самий markup…</article>
```

### CSS — підключай повний блок `.card*` з [css/components-1.css](css/components-1.css) (рядки ~162–388). Ключові правила:

```css
.card__panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  min-height: 100%;
  padding: clamp(1.375rem, 3vw, 2rem);
  background: var(--card-fill, var(--surface));
  border-radius: 1.25rem;
}
.card--rec { --card-fill: var(--accent); color: var(--ink); }
.card__cta {
  margin-top: auto;
  width: 100%;
  min-height: 2.875rem;
  border: 0;
  border-radius: var(--radius-pill);
  background: var(--ink);
  color: var(--cream);
  font-size: 0.875rem;
  font-weight: 600;
}
.card--rec .card__cta {
  background: var(--ink);
  color: #fff;
  box-shadow: inset 0 0 0 1.5px rgba(255, 255, 255, 0.88);
}
.card__list li::before {
  content: "";
  width: 0.375rem;
  height: 0.375rem;
  margin-top: 0.45em;
  border-radius: 50%;
  background: var(--accent-mark);
  flex: none;
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .card--pkg:hover { transform: translateY(-3px); }
}
```

---

## Accordion (FAQ)

### HTML

```html
<div class="accordion">
  <div class="accordion__item is-open">
    <button class="accordion__btn" type="button" aria-expanded="true">
      Скільки триває ремонт?
      <span class="accordion__icon" aria-hidden="true"></span>
    </button>
    <div class="accordion__panel">60 робочих днів за договором до старту.</div>
  </div>
  <div class="accordion__item">
    <button class="accordion__btn" type="button" aria-expanded="false">
      Що входить у ціну?
      <span class="accordion__icon" aria-hidden="true"></span>
    </button>
    <div class="accordion__panel">Дизайн, матеріали, роботи, здача.</div>
  </div>
</div>
```

Повний CSS: кінець [css/components-1.css](css/components-1.css) + початок [css/components-2.css](css/components-2.css).

---

## Modal

### HTML

```html
<div class="modal-root is-open" role="dialog" aria-modal="true" aria-labelledby="m-title">
  <div class="modal-root__backdrop" data-close-modal></div>
  <div class="modal">
    <button class="modal__close" type="button" aria-label="Закрити" data-close-modal>
      <span></span><span></span>
    </button>
    <h2 class="modal__title" id="m-title">Заявка</h2>
    <p class="modal__sub">Передзвонимо протягом дня</p>
    <p class="modal__context">Пакет: Optimal · 580 $/м²</p>
    <!-- fields + btn--primary btn--block -->
  </div>
</div>
```

### CSS (канон, скорочено)

```css
.modal-root {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: none;
  align-items: flex-end;
  justify-content: center;
  padding: var(--safe-t) var(--pad-x) calc(1rem + var(--safe-b));
}
.modal-root.is-open { display: flex; }
.modal-root__backdrop {
  position: absolute;
  inset: 0;
  background: var(--overlay);
}
.modal {
  position: relative;
  width: 100%;
  max-width: 420px;
  max-height: min(90dvh, 720px);
  overflow-y: auto;
  background: var(--surface);
  border-radius: var(--radius-modal);
  padding: 1.75rem 1.5rem;
  -webkit-overflow-scrolling: touch;
}
@media (min-width: 768px) {
  .modal-root { align-items: center; }
}
```

---

## Header (glass pill) + brand

### HTML

```html
<header class="site-header">
  <div class="site-header__inner">
    <a class="brand" href="#hero">
      <span class="brand__name">Kontur+</span>
      <span class="brand__desc">Ремонт під ключ</span>
    </a>
    <nav class="site-header__nav" aria-label="Основна">
      <a href="#packages">Пакети</a>
      <a href="#calculator">Розрахунок</a>
      <a href="#faq">FAQ</a>
    </nav>
    <div class="site-header__actions">
      <a class="site-header__tel-icon" href="tel:+380000000000" aria-label="Подзвонити">
        <!-- phone SVG 17×17 stroke -->
      </a>
      <a class="site-header__tel" href="tel:+380000000000">+380 …</a>
      <button class="burger" type="button" aria-label="Меню" aria-expanded="false">
        <span class="burger__lines"><span></span><span></span><span></span></span>
      </button>
    </div>
  </div>
</header>
```

### CSS — ключовий glass (повний файл: components-2)

```css
.site-header {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 80;
  padding: calc(12px + var(--safe-t)) clamp(12px, 2.5vw, 32px) 0;
  background: transparent;
  pointer-events: none;
}
.site-header__inner {
  pointer-events: auto;
  min-height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.35rem 0.5rem 0.35rem 0.75rem;
  background: rgba(22, 24, 26, 0.38);
  -webkit-backdrop-filter: blur(22px) saturate(1.35);
  backdrop-filter: blur(22px) saturate(1.35);
  border-radius: var(--radius-pill);
  border: 1px solid rgba(247, 246, 244, 0.22);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.14),
    0 8px 28px rgba(22, 24, 26, 0.12);
}
.site-header.is-scrolled .site-header__inner {
  background: rgba(22, 24, 26, 0.72);
  border-color: rgba(247, 246, 244, 0.3);
  -webkit-backdrop-filter: blur(28px) saturate(1.45);
  backdrop-filter: blur(28px) saturate(1.45);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.18),
    0 12px 36px rgba(22, 24, 26, 0.2);
}
```

JS: при `scrollY > 8` додавай `.is-scrolled` на `.site-header`.

---

## Section shell

```html
<section class="section section--soft" id="packages">
  <div class="container">
    <div class="section__head">
      <h2 class="section__title">Пакети ремонту</h2>
      <p class="section__lead">Фіксована ставка за м² до старту робіт.</p>
    </div>
    <!-- content -->
  </div>
</section>
```

Стилі `.container` / `.section*` — у [css/base.css](css/base.css).

---

## Reveal (motion)

```html
<body class="js">
  <div data-reveal-stagger>
    <article class="reveal reveal--up">…</article>
    <article class="reveal reveal--up">…</article>
  </div>
</body>
```

IO: коли елемент у вʼюпорті — `.is-inview`, після анімації — `.is-settled`.  
Повний CSS: [css/motion.css](css/motion.css).

---

## Мінімальний bootstrap нового проєкту

```html
<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/tokens.css" />
  <link rel="stylesheet" href="css/base.css" />
  <link rel="stylesheet" href="css/components-1.css" />
  <link rel="stylesheet" href="css/components-2.css" />
  <link rel="stylesheet" href="css/motion.css" />
</head>
<body class="js">
  <!-- snippets вище -->
</body>
</html>
```
