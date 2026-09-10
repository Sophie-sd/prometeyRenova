# RoyalSmoke Design System Skill

Універсальний Cursor Skill для реплікації дизайну **RoyalSmoke** (публічний storefront) у будь-якому проєкті.

## Вміст

| Файл | Призначення |
|------|-------------|
| `SKILL.md` | Інструкції агента (підключи в Cursor Skills) |
| `design-system-guide.md` | Повний Design System & UI Blueprint |
| `snippets.md` | HTML + CSS copy-paste |
| `css/` | Канонічні `tokens`, `base`, `components-1/2`, `motion` |

## Як підключити в Cursor

1. Скопіюй папку в персональні skills:

```bash
cp -R ~/Desktop/royalsmoke-design-system ~/.cursor/skills/royalsmoke-design-system
```

2. Або згадай Skill у чаті: «використай royalsmoke-design-system».

3. Агент має прочитати `SKILL.md`, далі гайд і `css/` за потреби.

## Шрифти

Self-host **Fixel Display** (woff2, 400–800) у `fonts/fixel-display/` поруч із CSS  
(шлях у токенах: `../fonts/fixel-display/…` від `css/`).  
Скопіюй з `~/Sites/RoyalSmoke/static/fonts/fixel-display/`.

## Джерело

Аудит `~/Sites/RoyalSmoke/static/css/*` · публічний storefront · bark / seashell / gold · Fixel Display.
