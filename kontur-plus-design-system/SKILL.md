---
name: kontur-plus-design-system
description: >-
  Replicates Kontur+ Landing v2 look & feel (lime/cream/pill, Outfit + Space
  Grotesk, CSS variables, BEM) in any project. Use when the user asks to apply
  Kontur+ design, copy Kontur UI, lime cream landing style, or replicate this
  design system elsewhere.
---

# Kontur+ Design System Replicator

Універсальний Skill: переносить **точний** візуал і поведінку Kontur+ Landing v2 у будь-який проєкт (HTML/CSS, Django, React тощо).

## When to apply

- «зроби як Kontur+», «lime/cream», «outfit + space grotesk»
- реплікація кнопок / header glass pill / modal / package cards
- новий лендінг з тією ж дизайн-системою

## Hard rules

1. **Лише CSS variables** з [css/tokens.css](css/tokens.css) — не вигадувати інші HEX.
2. **Шрифти:** Outfit 300–600 + Space Grotesk 500/700 (Google Fonts link нижче).
3. **Без** `!important`, Inter/Roboto, purple gradients, terracotta-cream кліше, emoji, floating badges на hero.
4. **Mobile First** + iOS Safari: `safe-area-inset-*`, `100dvh`, tap ≥44px, `-webkit-backdrop-filter`.
5. **Motion:** лише `opacity`/`transform` (окрім існуючих shadow/border transitions на chrome); завжди `prefers-reduced-motion`.
6. Класи — **BEM** як у джерелі (`.btn--primary`, `.site-header__inner`, `.card--rec`).
7. Пояснення українською; код і class names — англійською.

## Replication workflow

```
Task Progress:
- [ ] 1. Підключити fonts + tokens.css + base.css
- [ ] 2. Підключити components-1.css + components-2.css (порядок!)
- [ ] 3. За потреби — motion.css
- [ ] 4. Зібрати UI з HTML-сніпетів у snippets.md
- [ ] 5. Перевірити checklist нижче
```

### Step 1 — Fonts (обовʼязково)

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
```

### Step 2 — CSS load order

1. `css/tokens.css`
2. `css/base.css`
3. `css/components-1.css`
4. `css/components-2.css` ← починається з `}` що закриває accordion з файлу 1 — **не видаляти**
5. `css/motion.css` (опційно)

Повний гайд: [design-system-guide.md](design-system-guide.md)  
Copy-paste HTML: [snippets.md](snippets.md)

### Step 3 — Адаптація під стек

| Стек | Дія |
|------|-----|
| Static / Django | Скопіювати `css/*` у static; підключити як у гайді |
| React / Next | Імпортувати CSS глобально; className = ті самі BEM-класи |
| Tailwind | **Не** перекладати в utilities — підключати канонічний CSS |

## Checklist (done = виглядає як Kontur+)

- [ ] Canvas `#f7f6f4`, accent `#dff250`, ink `#16181a`
- [ ] Header: dark glass pill + `backdrop-filter: blur(22px)`
- [ ] Primary CTA: lime, radius 10px, min-height 50px
- [ ] Tel у хедері: pill 999px, lime
- [ ] Inputs: focus ring `0 0 0 3px var(--accent-soft)`
- [ ] Recommended card: `--card-fill: var(--accent)`
- [ ] Modal: overlay 52%, panel radius 12px, bottom sheet на mobile
- [ ] Reveal: `--dur-reveal: 700ms`, `--ease-reveal`
- [ ] Немає Inter / purple / cards-in-hero clutter

## Source of truth

Витягнуто з проєкту Kontur+ (`static/css/*`, Landing v2).  
При розбіжності — перемагає вміст папки `css/` цього Skill.
