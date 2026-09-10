---
name: royalsmoke-design-system
description: >-
  Replicates RoyalSmoke public storefront look & feel (bark/seashell/gold,
  Fixel Display, sharp geometry, CSS variables, rs- BEM) in any project. Use
  when the user asks to apply RoyalSmoke design, copy RS UI, dark luxury
  tobacco atelier style, or replicate this design system elsewhere.
---

# RoyalSmoke Design System Replicator

Універсальний Skill: переносить **точний** візуал і поведінку публічного RoyalSmoke у будь-який проєкт (HTML/CSS, Django, React тощо).

## When to apply

- «зроби як RoyalSmoke», «bark/seashell/gold», «Fixel Display»
- реплікація кнопок / карток / forms / age gate / drawer glass / hero
- новий storefront з тією ж дизайн-системою

## Hard rules

1. **Лише CSS variables** з [css/tokens.css](css/tokens.css) — не вигадувати інші HEX.
2. **Шрифт:** лише **Fixel Display** 400–800 (self-host woff2). Не Bodoni/Archivo з мокапів, не Inter/Roboto.
3. **Без** `!important`, purple gradients, terracotta-cream кліше, emoji, floating badges на hero, rounded cards за замовчуванням.
4. **Геометрія:** `border-radius: 0` майже всюди; pill лише для float/badge/seal.
5. **Mobile First** + iOS Safari: `safe-area-inset-*`, `100dvh`, tap ≥44px, inputs `16px` на iOS, `-webkit-backdrop-filter`.
6. **Motion:** UI ≤250ms; luxury reveal ~1000ms; завжди `prefers-reduced-motion`.
7. Класи — **`rs-` BEM** як у джерелі (`.rs-btn--primary`, `.rs-card__media`, `.rs-field`).
8. Пояснення українською; код і class names — англійською / `rs-`.

## Replication workflow

```
Task Progress:
- [ ] 1. Підключити Fixel Display + tokens.css + base.css
- [ ] 2. Підключити components-1.css + components-2.css
- [ ] 3. За потреби — motion.css
- [ ] 4. Зібрати UI з HTML-сніпетів у snippets.md
- [ ] 5. Перевірити checklist нижче
```

### Step 1 — Fonts (обовʼязково)

Скопіюй woff2 у `fonts/fixel-display/` (відносно static). `@font-face` уже в [css/tokens.css](css/tokens.css):

- `FixelDisplay-Regular.woff2` → 400
- `FixelDisplay-Medium.woff2` → 500
- `FixelDisplay-SemiBold.woff2` → 600
- `FixelDisplay-Bold.woff2` → 700
- `FixelDisplay-ExtraBold.woff2` → 800

### Step 2 — CSS load order

1. `css/tokens.css`
2. `css/base.css`
3. `css/components-1.css`
4. `css/components-2.css`
5. `css/motion.css` (опційно)

Повний гайд: [design-system-guide.md](design-system-guide.md)  
Copy-paste HTML: [snippets.md](snippets.md)

### Step 3 — Адаптація під стек

| Стек | Дія |
|------|-----|
| Static / Django | Скопіювати `css/*` + fonts у static; підключити як у гайді |
| React / Next | Імпортувати CSS глобально; className = ті самі `rs-` класи |
| Tailwind | **Не** перекладати в utilities — підключати канонічний CSS |

## Checklist (done = виглядає як RoyalSmoke)

- [ ] Canvas `#100d0c`, text `#fcf2ee`, accent `#c99a44`
- [ ] Font: Fixel Display; body 14→15→16px; headings uppercase wide tracking
- [ ] Primary CTA: seashell fill / bark text; ghost: border seashell; gold fill optional
- [ ] Inputs: bark-light fill, soft border, focus gold, radius 0; iOS font-size 16px
- [ ] Cards: media `3/4`, slot `#322a26`, no drop-shadow (lift on hover)
- [ ] Radius default 0; float btn pill 52×52; badge 8px
- [ ] Reveal: `--motion-reveal: 1000ms`, `--ease-out`, `data-rs-reveal` + `.is-in`
- [ ] Safe areas + `100dvh`; нема Inter / purple / clutter у hero

## Source of truth

Витягнуто з проєкту RoyalSmoke (`static/css/tokens.css`, `components*.css`, `animations.css`).  
При розбіжності — перемагає вміст папки `css/` цього Skill.
