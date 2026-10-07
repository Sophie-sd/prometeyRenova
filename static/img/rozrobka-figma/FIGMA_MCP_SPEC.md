# Soft `/rozrobka-sajtiv/` — Figma MCP SSOT (не скріни)

fileKey: `9F0Aop3cwrYgowNjrbzRcf`  
Акаунт: prometeyteams@gmail.com  
**НЕ** використовувати старий View-rate-limited файл `nqf46nnD1zrTI7fvk3BAAd`.

## Ноди (тягни get_design_context / download_assets)

| Секція | nodeId | Дія |
|--------|--------|-----|
| Design root | 1:54 | огляд |
| Desktop full | 1:55 | огляд 1440×3800 |
| Hero Background | 1:56 | MCP `imgHeroBackground` → `hero-bg.webp` |
| Hero floats + H1 + CTA | 1:57 | імплемент (250×180 r20) |
| Admin | 1:120 | імплемент |
| Portfolio UPPER («Наші роботи») | 1:164 | **KEEP** + MCP crops |
| Portfolio LOWER logos | 1:198 | **DO NOT implement** (SSOT: remove) |
| CTA card | 1:239 | імплемент + glow |
| Mobile root | 1:332 | огляд 393×3516 |

## Section order (Desktop SSOT)

Hero (floats+H1+CTA) → Services list → Admin (`1:120`) → Portfolio upper (`1:164`) → CTA (`1:239`)

Live Soft includes must match: `hero → products → admin → portfolio → calc`.

## Токени з MCP (не на око)

- bg page: `#000`
- accent orange CTA fill: `#d05300`
- accent link / #f60: `#ff6600` / `#f60`
- muted text: `#a1a1aa`
- light text: `#f5f5f5`
- Hero CTA bg: `#d05300`, text `#f5f5f5`, pill `border-radius: 100px`
- Floating cards: `250×180`, `border-radius: 20px`, rotations ≈ `-5.46°` / `+7.17°` / `-7.05°` / `+2.57°`
- Soft € lock: gettext **250 / 500 / 800**; float «Платформи» = `індивідуально` (не форсити Figma 1500€)
- Currency switcher + `pl-rs__prices` DOM MUST remain (tests)

## Ассети MCP (static/img/rozrobka-figma/)

- `hero-bg.webp` — MCP Hero Background PNG (optimized)
- `rings-hero.svg`, `rings-services.svg`, `rings-cta1.svg`, `rings-cta2.svg`
- `ellipse.svg`, `arrow-hero.svg`, `arrow-cta.svg`, `arrow-nav.svg`, `arrow-orange.svg`
- `card-feder.webp`, `card-elit.webp` — upper portfolio MCP crops (fallback when DB empty)

Не комітити huge raw MCP dumps (`_raw/`, multi-MB uncropped PNGs).

## Правило

1. Source = Figma MCP design_context + asset URLs (fileKey вище).
2. Скріни get_screenshot — лише візуальна перевірка після імплементації.
3. Тексти/ціни Soft лишаються gettext з Renova; метрики/layout/кольори — з Figma.
4. Django + BEM CSS, без Tailwind.
5. Пуш лише `git push sophie main` з `/Users/sofiadmitrenko/prometeyRenova`. Без GitHub/gh/API / BonisOleg.

## Mobile (1:332 @ 393×3516) — shipped

Breakpoint Soft: `≤767`. Desktop floats absolute only `≥1100`. Tablet `768–1099`: prices grid, no rotated floats.

### Nodes implemented (MCP get_design_context)

| Node | Section | Shipped |
|------|---------|---------|
| `1:343` | Services Overview (hero+cards) | Yes |
| `1:349` | Service Cards 2×2 | Yes — reuse `.pl-rs__float` as grid |
| `1:406` | Services list rows | Yes — ~95px, pill outline right |
| `1:459` | Admin | Yes — stack + screen ~240px r20 |
| `1:502` | Portfolio UPPER | Yes (existing) |
| `1:526` / desktop `1:198` | Client Logos / lower strip | **DO NOT implement** |
| `1:564` | Calc CTA | Yes — 4 stacked full-width buttons |

### Layout metrics (≤767)

- Hero `1:343`: flex-col gap **60px** between copy+CTA and cards; H1 **34px** / tracking **-1.7px** / `#f5f5f5` center; lead **12px** `#a1a1aa` max ~316px; CTA full-width h **44** radius **100px** bg `#d05300`.
- Cards `1:349`: **grid 2 cols**, gap **14px**, min-h ~328; card radius **20px**; title **14px** bold; price label **10px** + value **20px**; chip full-width `rgba(255,255,255,0.1)` + 6px ellipse.
- Soft € lock: floats **250 / 500 / 800 €**; platforms = gettext **`індивідуально`** (Figma card 1500€ NOT applied). Chip «окремий бриф» kept.
- `pl-rs__prices` + currency switcher + hero secondary links: **kept in DOM** for tests; prices/actions visually clipped on mobile when floats grid shows.
- Services `1:406`: H2 34 center; rows h 95 / r20 / gap 14; title 14 bold; desc 12; price top-right 12; outline pill «Детальніше» ~124×44.
- Calc `1:564`: card r20, pad ~40/16; H2 34; note 12; actions stack gap 14, width 100%, h 44; primary `#d05300` + 3 outline white.

### CSS / cache

- `rozrobka-sajtiv.css` + `rozrobka-sajtiv-2.css` (cache `?v=8`).
- Hero DOM order: copy+CTA → floats → prices → actions (desktop floats still absolute ≥1100).
