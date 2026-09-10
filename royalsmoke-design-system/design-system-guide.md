# RoyalSmoke - Design System & UI Blueprint

**Версія:** 1.0 · Mobile First · UA · публічний storefront  
**Джерело:** `static/css/tokens.css`, `components*.css`, `animations.css`, layout/pages  
**Бренд:** RoyalSmoke · dark luxury tobacco atelier

---

## 1. Design Philosophy & Tokens

- **Core Aesthetic:** dark-mode-first — bark grounds, seashell cream type, champagne gold accents; sharp edges; editorial uppercase tracking; full-bleed photography
- **Design Paradigm:** CSS custom properties (`--rs-*`) + `rs-` BEM + modular CSS; без Tailwind
- **Anti-slop:** без Inter/Roboto, purple gradients, terracotta-cream кліше, emoji, floating badges на hero, rounded product cards

Канонічний файл токенів: [css/tokens.css](css/tokens.css)  
Base / reset / type: [css/base.css](css/base.css)

---

## 2. Typography Stack

- **Primary / Display / UI:** `"Fixel Display", "Helvetica Neue", sans-serif`
- **Weights:** 400, 500 (`--rs-weight-ui`), 600 (`--rs-weight-sub`), 700 (`--rs-weight-display`), 800
- **Self-host:** `fonts/fixel-display/*.woff2` (див. `@font-face` у tokens)
- **Global body:** 14px / 500 / `line-height: 1.5` → 15px @768 → 16px @1024
- **Page titles:** `clamp(28px, 5vw, 42px)` · weight 600 · tracking `0.28–0.3em` · uppercase · `text-indent` = tracking

- **Scale Table:**

| Role | Size | Line-height | Weight | Notes |
|------|------|-------------|--------|-------|
| `H1` Hero | 34px → 56px @1024 | 1.18 | 700 | `.rs-hero__title` |
| Page / section | clamp 28–42px | 1.12 | 600 | `.rs-heading-page` |
| Card title/price | 17 → 23px | 1.25 | 600 | |
| Body | 14 / 15 / 16 | 1.5 | 500 | |
| Kicker | 12px | — | 600 | tracking 0.36em |
| Button | 13px | — | 500 | tracking 0.1em, uppercase |
| Caption / meta | 11–12px | — | 500 | muted, uppercase |

---

## 3. Color Palette

- **Brand / Primary (bark):** `#100d0c` → `--rs-bark` — canvas, header solid, gate
- **Seashell:** `#fcf2ee` → `--rs-seashell` — text, primary CTA, footer top
- **Gold:** `#c99a44` → `--rs-gold` · hover `#d8ac5c` → `--rs-gold-hover`
- **Coffee:** `#1c1715` → `--rs-coffee` — footer bottom
- **Bark light / slot:** `#181412` / `#322a26` — fields / media placeholders

- **Backgrounds:**
  - Main: `#100d0c`
  - Surface / slots: `#322a26`
  - Alt section: `#181412`
  - Footer top: `#fcf2ee` · bottom: `#1c1715`

- **Text Colors:**
  - Primary: `#fcf2ee`
  - Soft: `rgba(252, 242, 238, 0.85)`
  - Muted: `rgba(252, 242, 238, 0.6)`

- **Borders:** hairline `0.14` · soft `0.25` · strong `0.4` (seashell alpha)
- **Validation:** border `#c45c4a` · text `#e8a090`
- **Focus:** `outline: 2px solid var(--rs-gold); outline-offset: 2px`
- **Champagne CTA (catalog/cart):** `--rs-cb-gold-grad: linear-gradient(90deg, #ead7a6 0%, #d4b06a 42%, #b8893a 100%)`

---

## 4. Spacing, Grid & Geometry

- **Container Max-Width:** `1440px` → `--rs-container`
- **Horizontal pad:** `24px` (`20px` ≤359) → `64px` @1024 → `--rs-pad-x` / `--rs-pad-x-lg`
- **Section pad Y:** `40` → `72` @768 → `104` @1024
- **Spacing Scale:** 4 / 8 / 12 / 16 / 24 / 40 / 56 / 104 → `--rs-space-1…8`
- **Header / tap / btn:** `--rs-header-h: 60px` (72 @1024) · `--rs-tap: 44px` · `--rs-btn-h: 48px` (52 @1024)

- **Border Radiuses:**
  - Default / cards / inputs / buttons: `0`
  - Badge: `8px`
  - Float / social: `26px` / `50%`
  - Callback mobile sheet: `16px 16px 0 0`
  - Pill token: `--rs-radius-pill: 150px`

- **Shadows (Elevation):**

```css
/* Float */
box-shadow: 0 10px 24px var(--rs-shadow);

/* Search popover */
box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);

/* Drawer */
box-shadow: -20px 0 50px var(--rs-shadow);

/* Footer seal */
box-shadow:
  0 0 0 4px var(--rs-footer-top-bg),
  0 0 0 5px rgba(201, 154, 68, 0.35),
  0 12px 28px rgba(0, 0, 0, 0.35);
```

Картки товарів **без** drop-shadow — elevation через `.rs-hover-lift` (`-3px`).

- **Safe areas:** `--rs-safe-t/r/b/l: env(safe-area-inset-*, 0px)`
- **Z-index:** header 100 · drawer 200 · overlay 250 · callback 260 · gate 300 · float 80

---

## 5. UI Components Blueprint

Повні HTML + реальний CSS: [snippets.md](snippets.md)  
Сирі файли: [css/components-1.css](css/components-1.css), [css/components-2.css](css/components-2.css)

### Короткий контракт класів

| Компонент | Класи |
|-----------|--------|
| Buttons | `.rs-btn` + `--primary` / `--gold` / `--ghost` / `--underline` / `--block` |
| Fields | `.rs-form` > `.rs-field` > `label` + `input`/`textarea`; error: `.is-invalid` + `.rs-field__error` |
| Checkbox | `.rs-check` |
| Product card | `.rs-card` > `__media` `__fav` `__body` `__brand` `__title` `__price` |
| Category | `.rs-cat` > `__overlay` `__content` `__name` |
| Badge / tag | `.rs-badge` · `.rs-tag` (+ `.is-active`) |
| Age gate | `.rs-age-gate` (+ `.is-gate-out` / `.is-denied`) |
| Callback | `.rs-callback` > `__dialog` |
| Float | `.rs-float` > `__btn` (+ `--fill`) |
| Qty | `.rs-qty` |
| Type utils | `.rs-heading-page` · `.rs-kicker` · `.rs-meta` · `.rs-link-gold` · `.rs-display` |

---

## 6. Motion & Visual Effects

Канон: [css/motion.css](css/motion.css)

- **UI:** `--t-fast: 160ms` · `--t-base: 250ms` · `--ease-ui: cubic-bezier(0.2, 0.8, 0.25, 1)`
- **Luxury out:** `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`
- **Reveal:** `--motion-reveal: 1000ms` · y `24px` (18 mobile) · attr `data-rs-reveal` + class `.is-in`
- **Hover:** lift `-3px` · zoom `1.035` · underline grow gold · soft `500ms`
- **Hero crossfade:** `700ms` ease-out
- **Glass:** search `blur(16px)`, drawer `blur(18px)`, calc `blur(36px)`, callback `blur(6px)`
- **Reduced motion:** у `base.css` (scroll) і `motion.css` — reveal миттєво видимі, hover transform off

### Стандартні transition-рядки з проєкту

```css
/* .rs-btn */
transition:
  background var(--rs-dur-fast) ease,
  border-color var(--rs-dur-fast) ease,
  color var(--rs-dur-fast) ease,
  transform var(--rs-dur-fast) ease;

/* [data-rs-reveal] */
transition:
  opacity var(--rs-reveal-duration) var(--rs-reveal-easing) var(--rs-reveal-delay),
  transform var(--rs-reveal-duration) var(--rs-reveal-easing) var(--rs-reveal-delay);
```

---

## 7. Breakpoints (фактичні)

| Breakpoint | Використання |
|------------|--------------|
| `≤359` | pad-x-sm |
| `≤767` | mobile; reveal offsets; callback bottom sheet |
| `≥768` | tablet; body 15px; section 72px |
| `≥1024` | desktop; pad-x-lg; btn-h-lg; header 72; hero title 56 |

---

## 8. CSS file map (Skill + оригінал)

| Skill | Оригінал проєкту | Роль |
|-------|------------------|------|
| `css/tokens.css` | частина `tokens.css` | :root + @font-face |
| `css/base.css` | частина `tokens.css` | reset, type, focus, headings |
| `css/components-1.css` | `components1.css` | btn, card, form, badge |
| `css/components-2.css` | `components2.css` | gate, float, callback, cart line |
| `css/motion.css` | `animations.css` | reveal + hover |
| — | `layout*.css`, `footer.css`, `pages*.css` | chrome / секції (див. повний аудит) |
