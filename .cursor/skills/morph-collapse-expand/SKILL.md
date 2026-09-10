---
name: morph-collapse-expand
description: >-
  Плавне згортання/розгортання одного органу: капсула↔кулька, панель, картка.
  Край скла, stagger --i, без layout-стрибків. Use when хедер морфить у burger,
  лого стрибає, кулька лишається відкритою, collapse/expand меню чи блоку.
  Не щоденний burger (emil) і не catalog flyout.
---

# Morph Collapse Expand

Канон (читати першим): `/Users/sofiadmitrenko/Library/Mobile Documents/com~apple~CloudDocs/Prometey_vault/05_System/Skills/design_skills/motion/morph_collapse_expand_skill.md`

ERR: `/Users/sofiadmitrenko/Library/Mobile Documents/com~apple~CloudDocs/Prometey_vault/05_System/Skills/_meta/references/morph-collapse-expand-reference.md`

Eval: `/Users/sofiadmitrenko/Library/Mobile Documents/com~apple~CloudDocs/Prometey_vault/05_System/Skills/_meta/skill-creator/evals/morph-collapse-expand.json`

`/skill morph_collapse_expand_skill`

## Правила (стисло)

1. Один хост; скло = `::before` `width`; не два елементи (капсула + окремий burger).
2. Діти: лише `opacity` + `transform`; `--i` + `calc`. Без untransitioned `margin`/`padding`.
3. Expanded: wordmark у resting-слоті; кулька `opacity: 0`.
4. `--morph-ball` з height хоста. Скрол: sentinel + hysteresis (~48px OFF).
5. Не sticky в `flex: 1` (iOS). Не `clip-path` + `backdrop-filter`.
6. Кінематограф 0.8–1.3s лише для рідкісного морфу. UI-мікро → Emil ≤300ms.
7. Без `!important`, без inline `style=`/`onclick=`.

## Роутер

| Запит | Скіл |
|-------|------|
| Burger 100+/день, HTMX | `emil_motion_skill` |
| Каталог hover-міст | `catalog_dropdown_menu_skill` |
| Mega mouseleave / overlay opacity | `nav_menu_fix_skill` |
| Капсула↔кулька / collapse будь-чого | **цей** |

ID патерну: **NAV-04**.
