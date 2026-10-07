# Soft `/rozrobka-sajtiv/` — Figma MCP SSOT (не скріни)

fileKey: `nqf46nnD1zrTI7fvk3BAAd`
Акаунт: prometeyteams@gmail.com

## Ноди (тягни get_design_context / download_assets)

| Секція | nodeId | Дія |
|--------|--------|-----|
| Desktop full | 34:3879 | огляд |
| Design root | 34:4627 | огляд |
| Hero + floating cards | 34:3881 | імплемент |
| Services list | 34:3944 | імплемент |
| Portfolio UPPER («Наші роботи») | 34:4051 | імплемент + скріни карток |
| Portfolio LOWER | 34:4085 | **ВИДАЛИТИ** з шаблону |
| CTA card | 34:4126 | імплемент |

## Токени з MCP (не на око)

- bg page: `#000` / dark
- accent orange CTA fill: `#d05300`
- accent link / #f60: `#ff6600` / `#f60`
- muted text: `#a1a1aa`
- light text: `#f5f5f5`
- Hero CTA bg: `#d05300`, text `#f5f5f5`
- Floating cards: `250×180`, `border-radius: 20px`, rotations ≈ `-5.5°` / `+7°`
- Services title: `50px`
- Service rows: height `91px`
- Service numbers: gradient `#d05300 → black`, `70px`
- Services button: pill `border-radius: 100px`, border white
- Portfolio cards: `358×234`, `r20`, gap `20`
- Portfolio nav circles: `50px`
- Portfolio link color: `#f60`

## Ассети MCP (уже в static/img/rozrobka-figma/)

З `https://www.figma.com/api/mcp/asset/…` — використовувати ці файли, не перемальовувати:

- rings-services.svg, rings-hero.svg, rings-cta1.svg, rings-cta2.svg
- ellipse.svg, arrow-hero.svg, arrow-cta.svg
- portfolio-card1.png, portfolio-card2.png (з MCP raw fills)

## Правило

1. Source = Figma MCP design_context + asset URLs.
2. Скріни get_screenshot — лише візуальна перевірка після імплементації.
3. Тексти/ціни Soft лишаються gettext з Renova; метрики/layout/кольори — з Figma.
4. Django + BEM CSS, без Tailwind.
5. Пуш лише `git push sophie main` з `/Users/sofiadmitrenko/prometeyRenova`. Без GitHub/gh/API.

## Mobile (34:4144 @ 393×3516)

> MCP `get_design_context` / screenshots **skipped this pass** (Figma MCP unavailable). Layout tokens below from prior MCP cache + frame ids.

| Секція | nodeId | Дія |
|--------|--------|-----|
| Mobile root | 34:4144 | огляд 393×3516 |
| Header | 34:4146 | імплемент (site chrome) |
| Overview / hero | 34:4155 | імплемент — prices grid visible; floats hidden |
| Services | 34:4218 | імплемент — stacked rows |
| Admin | 34:4271 | імплемент — stack |
| Portfolio UPPER | 34:4314 | **KEEP** — near-full-width scroll cards |
| Client Logos | 34:4338 | **REMOVE** if present (не в шаблоні Soft) |
| CTA | 34:4376 | імплемент |

### Mobile notes

- Breakpoint Soft: `≤767` mobile-first; floats only `≥1100`.
- Soft offer lock: `pl-rs__prices` + currency лишаються в DOM (gettext 250/500/800 €).
- CSS: `rozrobka-sajtiv.css` + `rozrobka-sajtiv-2.css` (cache `?v=6`).
