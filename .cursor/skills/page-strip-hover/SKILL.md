---
name: page-strip-hover
description: >-
  Бігуча стрічка макетів сторінок: два сети −50%, hover scale усієї картки,
  луп не паузиться. Use when the user mentions ховер карток у стрічці,
  зум макета сторінки, стрічка зупиняється на hover, coverflow став marquee,
  page strip, mockup marquee, Ken Burns plus scale conflict.
  Не для snap-coverflow і не для лого-тікера без карток.
---

# Page Strip Hover

Канон (читати першим): `/Users/sofiadmitrenko/Library/Mobile Documents/com~apple~CloudDocs/Prometey_vault/05_System/Skills/design_skills/motion/page_strip_hover_skill.md`

ERR: `/Users/sofiadmitrenko/Library/Mobile Documents/com~apple~CloudDocs/Prometey_vault/05_System/Skills/_meta/references/page-strip-hover-reference.md`

`/skill page_strip_hover_skill`

## Правила (стисло)

1. Два ідентичні сети + `translate3d(-50%, 0, 0)` + `linear` `infinite`.
2. Loop `translate` лише на треку; hover `scale(1.06)` лише на картці — не на `img`.
3. Не паузити трек на `:hover` / `:has(:hover)`.
4. Hover лише `@media (hover: hover) and (pointer: fine)`. PRM — без лупа і без scale.
5. Скрін = сторінка (світлий PNG). Без fake browser chrome.
6. Не змішувати з snap-JS coverflow і Ken Burns на тому ж корені.
7. Без `!important`, без inline `style=`/`onclick=`.

## Роутер

| Запит | Скіл |
|-------|------|
| Snap, центр більший, стрілки | `coverflow_carousel_skill` |
| Лого/hatch без карток-макетів | `seamless_loop_skill` |
| Макети + hover-zoom, стрічка їде | **цей** |

ID патерну: **SECT-11**.
