# Kontur+ - Design System & UI Blueprint

**Версія:** 2.0 · Mobile First · UA · Landing v2  
**Джерело:** `static/css/tokens.css`, `base.css`, `components-*.css`, `motion.css`, `sections-1.css`  
**Бренд:** Kontur+ · сервісний лендінг (ремонт під ключ, Одеса)

---

## 1. Design Philosophy & Tokens

- **Core Aesthetic:** editorial service landing — warm cream canvas, graphite ink, lime CTA, pill chrome; повітря замість декоративного шуму
- **Design Paradigm:** pure CSS custom properties (`:root`) + BEM class components + mobile-first media queries; без Tailwind
- **Dials:** DESIGN_VARIANCE 6–7 · MOTION_INTENSITY 3–4 · VISUAL_DENSITY 2–3
- **Anti-slop:** без Inter/Roboto, purple gradients, terracotta-cream кліше, emoji, floating badges на hero, окремої thank-you page

Канонічний файл токенів: [css/tokens.css](css/tokens.css)

---

## 2. Typography Stack

- **Primary Font Family:** `"Outfit", "Helvetica Neue", sans-serif` (weights 300, 400, 500, 600)
- **Secondary / Accent Font:** `"Space Grotesk", ui-monospace, monospace` (500, 700) — ціни, індекси, trust metrics (клас `.mono`)
- **Google Fonts:**

```html
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
```

- **Global body:** 16px / weight 400 / `line-height: 1.62` (`--lh-body`) / `-webkit-font-smoothing: antialiased`
- **Headings (h1–h3, .brand-mark):** weight 500 · `line-height: 1.06` · `letter-spacing: -0.035em` · `text-wrap: balance`
- **Measure:** `max-width: 65ch` на `p`

- **Scale Table:**

| Role | Size | Line-height | Weight | Letter-spacing |
|------|------|-------------|--------|----------------|
| `H1` Hero | `clamp(2.125rem, 5.6vw, 4.875rem)` ≈ 34–78px | 1.02 | 500 | -0.04em |
| `H2` Section | `clamp(1.75rem, 3.2vw, 2.875rem)` ≈ 28–46px | 1.06 | 500 | -0.035em |
| Brand name | `clamp(1.1875rem, 1.8vw, 1.375rem)` ≈ 19–22px | 1.05 | 600 | -0.035em |
| `Body` | 16px (lead: `clamp(1rem, 1.25vw, 1.1875rem)`) | 1.62 | 400 | — |
| Section lead | 1.0625rem (17px) | 1.62 | 400 | muted |
| `Small/Caption` | 0.8125rem (13px) labels / 0.75rem indexes | 1.45 | 500 | indexes: 0.12em |
| Price mono | `clamp(2.375rem, 4vw, 3.25rem)` | 1 | 500 | -0.05em |
| Button | 0.9375rem (pill tel: 0.875rem / 600) | — | 500–600 | -0.01em |

---

## 3. Color Palette

- **Brand / Primary (accent lime):** `#dff250` → `--accent` — primary CTA, tel pills, recommended card fill
- **Accent hover:** `#eaff6b` → `--accent-hover`
- **Accent mark / stars:** `#a8bc22` → `--accent-mark` — list dots, focus border
- **Accent deep / eyebrows:** `#7e8f1c` → `--accent-deep`
- **Accent link:** `#5f6e12` → `--accent-link`
- **On accent:** `#16181a` → `--on-accent`
- **Accent soft (rings):** `rgba(223, 242, 80, 0.28)` → `--accent-soft`

- **Secondary / Accent:** lime stack вище; dark CTA `#16181a` / hover `#33383c`

- **Backgrounds:**
  - Main: `#f7f6f4` → `--canvas` / `--cream`
  - Surface / Cards: `#ffffff` → `--surface`
  - Soft sections / calc: `#eae6e0` → `--surface-soft`
  - Dark panels / footer / nav-sheet: `#16181a` → `--ink`

- **Text Colors:**
  - Primary text: `#16181a` → `--ink`
  - Muted / Secondary: `#6b6560` → `--muted`
  - Muted deep (list items): `#4a4642` → `--muted-deep`
  - On dark: `#f7f6f4` / `rgba(247,246,244,0.76)` lead

- **Borders & Dividers:** `#dcd8d2` → `--border`

- **Semantic:**
  - Success: `#2e6b52` · soft `rgba(46,107,82,0.1)`
  - Error: `#a13d3d` · soft `rgba(161,61,61,0.08)`
  - Overlay: `rgba(22,24,26,0.52)` → `--overlay`

- **Hero scrim:** `--scrim` / `--scrim-side` — vertical gradient graphite 0.72→0.24→0.62→0.92

---

## 4. Spacing, Grid & Geometry

- **Container Max-Width:** `1360px` → `--content-max`
- **Horizontal pad:** `clamp(1.25rem, 3.5vw, 3.5rem)` → `--pad-x`
- **Section padding-block:** `clamp(2.75rem, 6vw, 5.5rem)` → `--space-section`
- **Header height token:** 64px mobile / 72px ≥768px → `--header-h` (glass bar фактично auto/min 56px)
- **Spacing Scale:** rem-based; типовий ритм 0.375 / 0.5 / 0.625 / 0.75 / 0.875 / 1 / 1.25 / 1.375 / 1.5 / 1.75 / 2 rem (≈ 8px-сітка з clamp)

- **Border Radiuses:**
  - Small / buttons / inputs: `10px` → `--radius`
  - Medium / Cards panel: `1.25rem` (20px) на `.card__panel`
  - Modal: `12px` → `--radius-modal`
  - Pill / Buttons tel / header shell: `999px` → `--radius-pill`

- **Shadows (Elevation):**

```css
/* Header glass (default) */
box-shadow:
  inset 0 1px 0 rgba(255, 255, 255, 0.14),
  0 8px 28px rgba(22, 24, 26, 0.12);

/* Header scrolled */
box-shadow:
  inset 0 1px 0 rgba(255, 255, 255, 0.18),
  0 12px 36px rgba(22, 24, 26, 0.2);

/* Input focus */
box-shadow: 0 0 0 3px var(--accent-soft);

/* Input error */
box-shadow: 0 0 0 3px var(--error-soft);

/* Recommended card CTA inset ring */
box-shadow: inset 0 0 0 1.5px rgba(255, 255, 255, 0.88);
```

Картки пакетів **без** drop-shadow — elevation через hover `translateY(-3px)` і колір панелі.

- **Safe areas:** `--safe-t/b/l/r: env(safe-area-inset-*, 0px)`

---

## 5. UI Components Blueprint

Повні HTML + реальний CSS: [snippets.md](snippets.md)  
Сирі файли: [css/components-1.css](css/components-1.css), [css/components-2.css](css/components-2.css)

### Короткий контракт класів

| Компонент | Класи |
|-----------|--------|
| Buttons | `.btn` + `.btn--primary` / `--dark` / `--ghost` / `--pill` / `--block` / `--on-dark` / `--light` |
| Fields | `.field` > `.field__label` + `.field__input` + `.field__hint`; error: `.field--error` |
| Checkbox | `.checkbox` |
| Package card | `.card.card--pkg` (+ `.card--rec`); `.card__panel`, `__price`, `__list`, `__cta` |
| Accordion | `.accordion` > `.accordion__item` (+ `.is-open`) |
| Modal | `.modal-root` (+ `.is-open`) > `__backdrop` + `.modal` |
| Header | `.site-header` (+ `.is-scrolled`) > `__inner`, `__nav`, `__tel`, `__tel-icon`, `.burger` |
| Mobile nav | `.nav-sheet` (+ `.is-open`) |
| Brand | `.brand` > `__name` + `__desc` |

---

## 6. Motion & Visual Effects

Канон: [css/motion.css](css/motion.css)

- **Transitions (UI):** `220ms` → `--dur` · `cubic-bezier(0.22, 1, 0.36, 1)` → `--ease`
- **Reveal:** `700ms` → `--dur-reveal` · `cubic-bezier(0.22, 0.61, 0.36, 1)` → `--ease-reveal`
- **Reveal offset:** `--reveal-y: 20px` · `--reveal-x: 16px` · `--stagger: 70ms`
- **Hero enter:** `kp-enter` 760ms, delays 0 / 90 / 160 / 230ms
- **Modal:** `kp-rise` 240ms · backdrop `kp-fade` 200ms
- **Nav sheet:** `kp-fade` 260ms
- **Hero Ken Burns:** `kp-zoom` 12s scale 1.02→1.11 на active slide img
- **Glassmorphism header:** `rgba(22,24,26,0.38)` + `blur(22px) saturate(1.35)`; scrolled → `0.72` + `blur(28px)`
- **Hover micro:** image scale 1.035 / 720ms; card/review/styles `translateY(-2px|-3px)`; btn active `scale(0.985)`
- **Reduced motion:** у `base.css` і `motion.css` — анімації/transition → ~0; `.reveal` миттєво видимі

### Стандартні transition-рядки з проєкту

```css
/* .btn */
transition: background var(--dur) var(--ease), border-color var(--dur) var(--ease),
  color var(--dur) var(--ease), opacity var(--dur) var(--ease),
  transform var(--dur) var(--ease);

/* .field__input */
transition: border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease);

/* .site-header__inner */
transition:
  background 320ms var(--ease-reveal),
  border-color 320ms var(--ease-reveal),
  box-shadow 320ms var(--ease-reveal),
  -webkit-backdrop-filter 320ms var(--ease-reveal),
  backdrop-filter 320ms var(--ease-reveal);
```

---

## 7. Breakpoints (фактичні)

| Breakpoint | Використання |
|------------|--------------|
| `<480px` | щільніші card CTA |
| `≥768px` | section head 2-col; desktop nav; tel pill; modal center; header-h 72 |
| `768–1023` | менші card titles |
| `≥1024px` | header inner padding tweak |

---

## 8. CSS file map (оригінал проєкту)

| Файл | Роль |
|------|------|
| `tokens.css` | :root tokens |
| `base.css` | reset, type, container, section |
| `components-1.css` | btn, field, card, accordion start |
| `components-2.css` | accordion end, modal, header, nav |
| `motion.css` | reveal, hero enter, hovers |
| `sections-*.css` | hero, packages, grids |
| `calc.css` / `cases.css` / `reviews.css` / `footer.css` | секції |
| `cookie-consent.css` / `privacy.css` / `errors.css` | утиліти |
