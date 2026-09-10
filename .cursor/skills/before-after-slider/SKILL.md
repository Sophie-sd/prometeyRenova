---
name: before-after-slider
description: >-
  Слайдер «До і після» (GAL-05): clip-path, knob ≥44px, touch без скролу.
  Use when до і після, before after, image compare, comparison slider,
  тягнеться зображення замість ручки, ba-compare, потягніть роздільник.
  Не coverflow і не PDP thumbs (GAL-01).
---

# Before After Slider

Канон (читати першим): `/Users/sofiadmitrenko/Library/Mobile Documents/com~apple~CloudDocs/Prometey_vault/05_System/Skills/design_skills/patterns/before_after_slider_skill.md`

`/skill before_after_slider_skill`

## Правила (стисло)

1. `--ba` **з `%`** (`52%`…`98%`); JS `setProperty('--ba', v + '%')`. Не unitless у `calc(… * 1%)`.
2. Clip: `inset(0 calc(100% - var(--ba)) 0 0)`; handle: `left: var(--ba)` + `translateX(-50%)`. Clamp 2…98.
3. Drag: клас `is-dragging` → без `transition` на clip і handle. Idle ≤240ms.
4. `touch-action: none` + `setPointerCapture`; cleanup / `data-ba-ready` після HTMX.
5. Cover-fill обох `img`; `pointer-events: none` + `draggable="false"` (інакше тягнеться фото).
6. Knob ≥44px; labels/handle `pointer-events: none`; `role="slider"`.
7. Без `!important`, без inline `style=`/`onclick=` (лише `setProperty('--ba')`).

## Роутер

| Запит | Скіл |
|-------|------|
| Карусель кейсів / coverflow | `coverflow_carousel_skill` |
| PDP thumbs | GAL-01 / gallery thumbs |
| Порівняння двох кадрів / ручка зрізу | **цей** |

ID патерну: **GAL-05**.
