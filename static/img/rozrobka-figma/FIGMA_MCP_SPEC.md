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

## Mobile (1:332 @ 393×3516)

- Breakpoint Soft: `≤767`; floats only `≥1100`.
- Soft offer lock: `pl-rs__prices` + currency лишаються в DOM (gettext 250/500/800 €).
- CSS: `rozrobka-sajtiv.css` + `rozrobka-sajtiv-2.css` (cache `?v=7`).
