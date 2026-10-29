# Підказки: template-corporate-catalog.zip

Порожній `proposal.json` у шаблоні не містить коментарів. Усі пояснення — тут і в INSTRUCTION.md.

- `kind`: `corporate`, `corp_catalog`: `true` — не змінювати.
- Каталог без оплат і кошика: «Купити» відкриває форму заявки.
- У manifest `type` = `corporate_catalog`, але в proposal.json `kind` = `corporate` і `corp_catalog` = `true` (так влаштована модель).
- `slug`, `client_name`, `title`, `issued_on` — обов'язкові.
- Кожен текст — двома мовами: поле без суфікса (UA) і `_ru`.
- `guarantee_html`: «пожиттєва гарантія на код + 1 рік безкоштовної підтримки»; `guarantee_html_ru`: «пожизненная гарантия на код + 1 год бесплатной поддержки».
- `packages[].price` — число з крапкою (`"0.00"` у шаблоні), заповнюється під конкретне КП; `price_high` — `null` або верхня межа.
- `specs[].kind`: `spec` (ТЗ), `recommendation` (рекомендації), `payment` (умови оплати). Додавайте стільки карток, скільки треба.
- `hero_image`: `"media/hero.webp"` або порожньо.
- `is_published`: лишіть `false` до перевірки.
