# RoyalSmoke — Copy-paste UI Snippets

Реальний CSS з `components-*.css` + мінімальний HTML.  
Підключи спочатку [css/tokens.css](css/tokens.css) і [css/base.css](css/base.css), або встав фрагменти нижче після токенів.

---

## Buttons

### HTML

```html
<button class="rs-btn rs-btn--primary" type="button">Каталог</button>
<button class="rs-btn rs-btn--gold" type="button">До кошика</button>
<button class="rs-btn rs-btn--ghost" type="button">Детальніше</button>
<button class="rs-btn rs-btn--primary rs-btn--block" type="submit">Надіслати</button>
<button class="rs-btn rs-btn--underline" type="button">Видалити</button>

<div class="rs-btn-row">
  <button class="rs-btn rs-btn--primary" type="button">Так</button>
  <button class="rs-btn rs-btn--ghost" type="button">Ні</button>
</div>
```

### CSS (канон)

Див. повний блок у [css/components-1.css](css/components-1.css) (`.rs-btn` … `.rs-btn-row`).

```css
.rs-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: var(--rs-btn-h);
  min-width: var(--rs-tap);
  padding: 0 26px;
  font-family: var(--rs-font-ui);
  font-size: 13px;
  font-weight: var(--rs-weight-ui);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  border: 1px solid transparent;
  transition:
    background var(--rs-dur-fast) ease,
    border-color var(--rs-dur-fast) ease,
    color var(--rs-dur-fast) ease,
    transform var(--rs-dur-fast) ease;
  -webkit-tap-highlight-color: transparent;
}
.rs-btn:active { transform: translateY(1px); }
.rs-btn:disabled,
.rs-btn.is-disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}
.rs-btn--primary { background: var(--rs-seashell); color: var(--rs-bark); }
.rs-btn--primary:hover { background: #ffffff; }
.rs-btn--gold { background: var(--rs-gold); color: var(--rs-bark); }
.rs-btn--gold:hover { background: var(--rs-gold-hover); }
.rs-btn--ghost {
  background: transparent;
  border-color: var(--rs-border);
  color: var(--rs-seashell);
}
.rs-btn--ghost:hover { border-color: var(--rs-gold); }
.rs-btn--block { width: 100%; }
.rs-btn--underline {
  min-height: 44px;
  padding: 0;
  background: transparent;
  border: 0;
  color: var(--rs-seashell);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-decoration: underline;
  text-underline-offset: 5px;
  text-decoration-thickness: 1px;
  text-decoration-color: var(--rs-gold);
}
.rs-btn--underline:hover { color: var(--rs-gold); }
```

---

## Form inputs

### HTML

```html
<form class="rs-form" action="#" method="post">
  <div class="rs-field">
    <label for="name">Імʼя</label>
    <input id="name" name="name" type="text" autocomplete="name" />
  </div>

  <div class="rs-field is-invalid">
    <label for="phone">Телефон</label>
    <input id="phone" name="phone" type="tel" inputmode="tel" />
    <p class="rs-field__error">Перевірте формат номера</p>
  </div>

  <div class="rs-field">
    <label for="msg">Повідомлення</label>
    <textarea id="msg" name="message" rows="4"></textarea>
  </div>

  <label class="rs-check">
    <input type="checkbox" name="privacy" required />
    <span>Погоджуюсь з політикою конфіденційності</span>
  </label>

  <div class="rs-form__actions">
    <button class="rs-btn rs-btn--primary rs-btn--block" type="submit">Надіслати</button>
  </div>
</form>
```

### CSS (канон)

```css
.rs-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
  width: 100%;
  max-width: 520px;
}
.rs-field { display: flex; flex-direction: column; gap: 8px; }
.rs-field label {
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--rs-text-muted);
}
.rs-field input,
.rs-field select,
.rs-field textarea {
  width: 100%;
  min-height: 48px;
  padding: 12px 14px;
  background: var(--rs-bark-light);
  border: 1px solid var(--rs-border-soft);
  color: var(--rs-seashell);
  border-radius: 0;
  appearance: none;
  -webkit-appearance: none;
}
.rs-field textarea { min-height: 120px; resize: vertical; }
.rs-field input:focus,
.rs-field select:focus,
.rs-field textarea:focus { border-color: var(--rs-gold); }
.rs-field.is-invalid input,
.rs-field.is-invalid select,
.rs-field.is-invalid textarea { border-color: #c45c4a; }
.rs-field__error { font-size: 12px; color: #e8a090; line-height: 1.4; }
@supports (-webkit-touch-callout: none) {
  .rs-field input,
  .rs-field select,
  .rs-field textarea { font-size: 16px; }
}
.rs-check {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  color: var(--rs-text-soft);
}
.rs-check input {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  accent-color: var(--rs-gold);
  flex-shrink: 0;
}
```

---

## Product card

### HTML

```html
<article class="rs-card rs-hover-lift">
  <div class="rs-card__media rs-hover-zoom">
    <img src="/media/product.jpg" alt="" width="600" height="800" />
    <button class="rs-card__fav" type="button" aria-label="Wishlist">♥</button>
  </div>
  <div class="rs-card__body">
    <span class="rs-card__brand">Brand</span>
    <h3 class="rs-card__title">Product name</h3>
    <p class="rs-card__price"><del>2 400 ₴</del> 1 990 ₴</p>
    <div class="rs-card__actions">
      <button class="rs-btn rs-btn--ghost" type="button">У кошик</button>
    </div>
  </div>
</article>
```

### CSS (канон)

```css
.rs-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.rs-card__media {
  position: relative;
  aspect-ratio: 3 / 4;
  background: var(--rs-slot);
  overflow: hidden;
}
.rs-card__media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.rs-card__fav {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  background: rgba(252, 242, 238, 0.92);
  color: var(--rs-bark);
}
.rs-card__brand {
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--rs-text-muted);
}
.rs-card__title,
.rs-card__price {
  font-family: var(--rs-font-display);
  font-weight: var(--rs-weight-sub);
  font-size: 17px;
  color: var(--rs-seashell);
}
.rs-card__price { margin-top: 4px; }
.rs-card__price del {
  margin-right: 8px;
  color: var(--rs-text-muted);
  font-size: 14px;
}
```

---

## Category tile

### HTML

```html
<a class="rs-cat rs-hover-zoom" href="/catalog/cigars/">
  <img src="/media/cat.jpg" alt="" />
  <span class="rs-cat__overlay" aria-hidden="true"></span>
  <span class="rs-cat__content">
    <span>
      <span class="rs-cat__name">Сигари</span>
      <span class="rs-cat__meta">42 позиції</span>
    </span>
  </span>
</a>
```

### CSS (канон)

```css
.rs-cat {
  position: relative;
  display: block;
  min-height: 180px;
  background: var(--rs-slot);
  overflow: hidden;
}
.rs-cat img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  inset: 0;
}
.rs-cat__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(16, 13, 12, 0.85) 100%);
}
.rs-cat__content {
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 18px;
}
.rs-cat__name {
  font-family: var(--rs-font-display);
  font-weight: var(--rs-weight-sub);
  font-size: 20px;
  color: var(--rs-seashell);
}
.rs-cat__meta {
  display: block;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--rs-text-muted);
  margin-top: 4px;
}
```

---

## Badge & tag

### HTML

```html
<span class="rs-badge" data-count="3">3</span>
<button class="rs-tag is-active" type="button">Mild</button>
<button class="rs-tag" type="button">Full</button>
```

### CSS (канон)

```css
.rs-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 15px;
  height: 15px;
  padding: 0 4px;
  border-radius: 8px;
  background: var(--rs-seashell);
  color: var(--rs-bark);
  font-size: 9px;
  font-weight: var(--rs-weight-sub);
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.rs-tag {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid var(--rs-border-soft);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--rs-text-muted);
}
.rs-tag.is-active {
  border-color: var(--rs-gold);
  color: var(--rs-seashell);
}
```

---

## Age gate

### HTML

```html
<div class="rs-age-gate" role="dialog" aria-modal="true" aria-labelledby="age-title">
  <div class="rs-age-gate__inner rs-age-ask">
    <div class="rs-age-gate__brand">Royal Smoke</div>
    <h2 class="rs-age-gate__title" id="age-title">Вам виповнилося<br />21 рік?</h2>
    <p class="rs-age-gate__text">Сайт містить інформацію про тютюнові вироби.</p>
    <div class="rs-age-gate__actions">
      <button class="rs-btn rs-btn--primary rs-btn--block" type="button">Мені є 21 рік</button>
      <button class="rs-btn rs-btn--ghost rs-btn--block" type="button">Мені немає 21 року</button>
    </div>
  </div>
</div>
```

### CSS (канон)

Повний блок: [css/components-2.css](css/components-2.css) (`.rs-age-gate` …).

```css
.rs-age-gate {
  position: fixed;
  inset: 0;
  z-index: var(--rs-z-gate);
  background: var(--rs-bark);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: calc(24px + var(--rs-safe-t)) var(--rs-pad-x) calc(24px + var(--rs-safe-b));
  min-height: 100dvh;
  transition: opacity 320ms ease, transform 320ms ease;
}
.rs-age-gate.is-gate-out {
  opacity: 0;
  transform: scale(1.02);
  pointer-events: none;
}
.rs-age-gate__inner { width: 100%; max-width: 420px; text-align: center; }
.rs-age-gate__brand {
  font-family: var(--rs-font-display);
  font-weight: var(--rs-weight-display);
  font-size: 34px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.rs-age-gate__title {
  margin: 44px 0 14px;
  font-family: var(--rs-font-display);
  font-weight: var(--rs-weight-sub);
  font-size: 27px;
  line-height: 1.25;
}
.rs-age-gate__text {
  color: var(--rs-text-muted);
  font-size: 14px;
  line-height: 1.55;
  margin-bottom: 28px;
}
.rs-age-gate__actions { display: flex; flex-direction: column; gap: 12px; }
```

---

## Callback modal

### HTML

```html
<div class="rs-callback" role="dialog" aria-modal="true" aria-labelledby="cb-title">
  <div class="rs-callback__dialog">
    <h2 class="rs-callback__title" id="cb-title">Зворотний дзвінок</h2>
    <p class="rs-callback__text">Залиште номер — ми зателефонуємо.</p>
    <!-- rs-form … -->
    <button class="rs-btn rs-btn--primary rs-btn--block" type="submit">Чекаю дзвінка</button>
  </div>
</div>
```

### CSS (канон)

```css
.rs-callback {
  position: fixed;
  inset: 0;
  z-index: 260;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: calc(24px + var(--rs-safe-t)) var(--rs-pad-x) calc(24px + var(--rs-safe-b));
  min-height: 100dvh;
  background: rgba(16, 13, 12, 0.92);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
}
.rs-callback__dialog {
  width: 100%;
  max-width: 420px;
  padding: 32px 24px;
  background: var(--rs-bark);
  border: 1px solid var(--rs-hairline);
  text-align: center;
}
@media (max-width: 767px) {
  .rs-callback { align-items: flex-end; }
  .rs-callback__dialog {
    max-width: none;
    border-radius: 16px 16px 0 0;
    padding: 28px 20px calc(28px + env(safe-area-inset-bottom, 0px));
  }
}
```

---

## Float actions

### HTML

```html
<div class="rs-float">
  <button class="rs-float__btn" type="button" aria-label="Up">↑</button>
  <button class="rs-float__btn rs-float__btn--fill" type="button" aria-label="Call">☎</button>
</div>
```

### CSS (канон)

```css
.rs-float {
  position: fixed;
  right: calc(16px + var(--rs-safe-r));
  bottom: calc(16px + var(--rs-safe-b));
  z-index: var(--rs-z-float);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.rs-float__btn {
  width: 52px;
  height: 52px;
  border-radius: 26px;
  border: 1px solid var(--rs-border-soft);
  background: var(--rs-bark);
  color: var(--rs-seashell);
  display: grid;
  place-items: center;
  box-shadow: 0 10px 24px var(--rs-shadow);
}
.rs-float__btn:hover { border-color: var(--rs-gold); }
.rs-float__btn--fill {
  background: var(--rs-seashell);
  color: var(--rs-bark);
  border-color: var(--rs-seashell);
}
```

---

## Scroll reveal (motion)

### HTML

```html
<section data-rs-reveal>
  <h2 class="rs-heading-page">Секція</h2>
</section>

<div data-rs-reveal="left">…</div>
<div data-rs-reveal="scale">…</div>
```

### CSS (канон)

Підключи [css/motion.css](css/motion.css). JS: IntersectionObserver → додати `.is-in`.

```css
[data-rs-reveal] {
  opacity: 0;
  transform: translate3d(0, var(--rs-reveal-y), 0);
  transition:
    opacity var(--rs-reveal-duration) var(--rs-reveal-easing) var(--rs-reveal-delay),
    transform var(--rs-reveal-duration) var(--rs-reveal-easing) var(--rs-reveal-delay);
}
[data-rs-reveal].is-in {
  opacity: 1;
  transform: none;
}
```

---

## Page heading / kicker

### HTML

```html
<p class="rs-kicker">Tobacco Atelier</p>
<h1 class="rs-heading-page">Калькулятор підбору</h1>
<p class="rs-meta">Оберіть смак і міцність</p>
```

Стилі вже в [css/base.css](css/base.css).
