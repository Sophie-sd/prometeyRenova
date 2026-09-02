---
name: object-tilt-glare
description: >-
  3D tilt + лаковий блік на будь-якому об’єкті: 18°/24°, лак −40%, glare +60%,
  hover 0.48/0.30. Use when нахил кнопки/кола/фото/картки, лак, блік, glare,
  мат→глянець, будь-який колір/фон. Не райдужна фольга CARD-05 і не CARD-04
  на тій же ноді.
---

# Object Tilt Glare

Канон (читати першим): `/Users/sofiadmitrenko/Prometey_vault/05_System/Skills/design_skills/motion/object_tilt_glare_skill.md`

Eval: `/Users/sofiadmitrenko/Prometey_vault/05_System/Skills/_meta/skill-creator/evals/object-tilt-glare.json`

`/skill object_tilt_glare_skill`

## Правила (стисло)

1. `--tilt-x = -y * 18deg`, `--tilt-y = x * 24deg`; хост `perspective(1000px) translateY(-4px)`.
2. Лак `::before` × −40%; блік `::after` × +60%; без `background-position`.
3. Hover `--tilt-foil: 0.48`, `--tilt-glare: 0.30`. Rest / touch / PRM = 0.
4. Dark: лак `color-dodge`. Light: `overlay`. Glare завжди `screen`.
5. Форма = `overflow: hidden` + `border-radius` / `clip-path` хоста.
6. CARD-04/05 на хості → внутрішній `.obj-tilt`.
7. Без `!important`, без inline `style=`/`onclick=`.

## Роутер

| Запит | Скіл |
|-------|------|
| Райдуга / pokemon-holo / acid foil | `holographic-foil-card-skill` |
| L-кути рамки | `frame-hover-corners-skill` |
| Нахил + лак, будь-яка форма | **цей** |
