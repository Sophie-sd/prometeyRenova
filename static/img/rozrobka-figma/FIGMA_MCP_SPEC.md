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
