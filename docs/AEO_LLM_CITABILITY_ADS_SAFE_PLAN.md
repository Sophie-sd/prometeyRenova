# AEO / LLM-citability план (Ads-safe) — PrometeyLabs

**Дата:** 2026-10-07  
**Аудиторія:** Андрій  
**Скоуп:** покращити цитованість у LLM/пошуку для Ads-кампаній **без** поломки релевантності оголошень, Quality Score і message match.  
**Статус цього документа:** план ONLY — **жодних** code-змін AEO в цьому таску.

---

## Контекст / діагноз

Аудит `prometeylabs.com` (сьогодні):

| Актив | Стан | Наслідок для LLM/Ads |
|--------|------|----------------------|
| `robots.txt` | OK (пошукові боти відкриті; `/admin/`, `/proposal/`, `/demo/`, `/thank-you/` закриті) | База для краулінгу є |
| `llms.txt` | **404** | LLM-асистенти не бачать короткого «паспорта» студії з цінами й URL |
| `sitemap.xml` | **500** | Індексація/перевідкриття URL ламається; цитати й Ads landing discovery страждають |

Бізнес-мета: щоб ChatGPT / Perplexity / Claude / Google AI Overviews **цитували реальні офери** (корп / магазин / бот) з тими самими € і тим самим message, що в Soft і в Ads — не вигадували кейси й не тягнули `/proposal/` чи демо.

У Renova вже є заготовки, які план спирається на (але **не чіпає** в Task A):

- `apps/core/sitemaps.py` — `StaticViewSitemap` + `BlogPostSitemap`
- `templates/robots.txt`
- JSON-LD Organization у `templates/base.html`; Service+Offer на Soft `/rozrobka-sajtiv/`
- LP: `/corporate-website-v2/`, `/internet-shop-v2/`, `/telegram-bot/` (+ Soft hub)
- i18n префікси `/en/`, `/ru/`

---

## Червоні лінії Ads

1. **Не ламати Soft / message match.** Hero Soft і Ads final URL мають говорити про той самий офер (лендінг 250 € / корп 500 € / магазин 800 € на Soft; на сервісних LP — діапазони з тієї ж сторінки). Розбіжність = QS і Relevance падають.
2. **Не міняти Soft € без узгодження з Андрієм.** Ціни в DOM (`pl-rs__prices` + currency) і в Ads — lock.
3. **Не чіпати Ads landing copy mid-campaign без QA.** Будь-який rewrite above-fold на LP, що є final URL — тільки staged deploy + візуальний/текстовий diff + перевірка відповідності RSA.
4. **Не пушити AEO-правки на `origin`/BonisOleg.** Soft-код — лише `git push sophie main` (як у робочих правилах).
5. **Не індексувати** `/admin/`, `/proposal/`, `/demo/`, `/thank-you/` — ні в sitemap, ні в `llms.txt`.
6. **Не вигадувати кейси** з цифрами/іменами клієнтів без письмового дозволу на публікацію name+numbers.
7. **Не ставити Crawl-delay** і не блокувати масово LLM-ботів так, щоб зламати citability (опційно лише GPTBot — див. фазу P1).

---

## Фази P0–P3 з Definition of Done

### P0 — День 1 (критичний шлях citability + Ads safety)

**Що зробити**

1. **Полагодити `sitemap.xml` 500**  
   - У sitemap мають бути: home, 3 сервіси (corp v2 / shop v2 / telegram-bot), Soft hub за потреби, portfolio, contacts, blog (+ пости), **EN-дзеркала** сервісів/ключових сторінок.  
   - **Виключити:** `/admin/`, `/proposal/`, `/demo/` (+ demo-landing/demo-site), `/thank-you/`, тонкий search блогу.
2. **Додати root `llms.txt`**  
   - Короткий блер PrometeyLabs.  
   - Посилання з цінами з реальних LP: корп **500–700 €**, магазин **800–1400 €**, бот (ціна з LP), contacts.  
   - **Без** вигаданих case-URL.
3. **Hero cite-параграфи** на 3 сервісних LP (corp / shop / bot): щільний quoteable абзац над fold, **видима дата оновлення цін**, таблиця include/exclude; прибрати слоганний fluff із quote-блоку.
4. **Schema Offer**  
   - Home: Organization з телефоном `+380639520565`, `info@prometeylabs.com`, **реальний** `sameAs` only; без фейкової вулиці.  
   - Service pages: `Service` + `Offer` EUR з тієї ж сторінки.  
   - `LocalBusiness` — **лише** якщо є публічний офіс (зараз — ні → не ставити).

**DoD P0**

- [ ] `GET /sitemap.xml` → 200, валідний XML, містить home + 3 services + portfolio + contacts + blog + EN mirrors; немає excluded paths.
- [ ] `GET /llms.txt` → 200, UTF-8, ціни збігаються з LP, немає invented cases.
- [ ] На 3 LP: quoteable абзац + price-update date + include/exclude видимі без JS.
- [ ] JSON-LD Organization/Service/Offer валідується (Rich Results / schema validator); немає fake street.
- [ ] Soft € і Ads RSA headline/description **без змін** або з явним QA-signoff.
- [ ] Ads final URL message match перевірено вручну (same offer line / same price band).

### P1 — Тиждень 1 (боти + EN + URL policy)

5. **robots.txt політика для LLM**  
   - Залишити search bots open.  
   - Опційно: `Disallow` **лише GPTBot** (якщо продукт-рішення — блокувати тренувальний краул, не search).  
   - **Без** Crawl-delay.  
   - **Не** блокувати OAI-SearchBot / PerplexityBot / Claude-*.
6. **EN mirrors** для 3 service URL + `canonical` / `hreflang` (uk / en / ru / x-default). Ціни лишаються **EUR**.
7. **Стабілізація URL** `/corporate-website-v2/` і `/internet-shop-v2/`  
   - Або залишити v2 як канон і цитувати їх у `llms.txt`,  
   - Або one-time clean URLs **з 301** на новий path **до** того, як `llms.txt`/Ads почнуть масово цитувати.  
   - Відкрите рішення — див. кінець документа.

**DoD P1**

- [ ] robots: search open; optional GPTBot only; no Crawl-delay; OAI-SearchBot/PerplexityBot/Claude-* allowed.
- [ ] EN URL 200 + hreflang взаємно узгоджені; EUR на EN.
- [ ] Зафіксовано рішення v2 stabilize vs redirect; якщо redirect — 301 покривають старі Ads/llms URL.

### P2 — Кейси (лише з дозволу)

8. Portfolio → **citeable case pages** тільки коли клієнт дозволяє **name + numbers**.  
   - Після дозволу: окрема сторінка кейсу + **2** посилання в `llms.txt`.  
   - До дозволу: у `llms.txt` лише загальне `/portfolio/`, без фейкових метрик.

**DoD P2**

- [ ] Письмовий OK клієнта збережено (нотатка в задачі).
- [ ] Case URL у sitemap + 2 лінки в `llms.txt`.
- [ ] Жодних invented ROI/«+300%» без джерела.

### P3 — Операційний ритм

9. **Щотижневі LLM query checks** + аналітика реферерів `chatgpt.com` / `perplexity` / `claude`.  
   - Чекліст питань — нижче.  
   - Алерти, якщо цитата розходиться з Ads price/offer.

**DoD P3**

- [ ] Щотижневий лог (дата, запит, відповідь моделі, URL-цитата, match Soft/Ads: yes/no).
- [ ] У GA4/аналітиці сегмент LLM-referrers або UTM-нотатки.
- [ ] Ескалація Андрію, якщо mismatch цін/оферу.

---

## Що чіпати в Renova (файли / зони)

| Зона | Ймовірні файли / точки | Фаза |
|------|------------------------|------|
| Sitemap 500 | `apps/core/sitemaps.py`, підключення в `prometey_project/urls.py`, i18n URL names для EN mirrors, тести `apps/core/tests/test_*.py` | P0 |
| `llms.txt` | новий static/`templates/llms.txt` **або** view + route на root; деплой static/collectstatic | P0 |
| robots | `templates/robots.txt` (опційний GPTBot block) | P1 |
| JSON-LD | `templates/base.html` (Organization); LP templates corp/shop/bot (Service+Offer); **не** дублювати суперечливі типи | P0 |
| Hero cite / price date / include-exclude | компоненти `corporate_website_v2`, `internet_shop_v2`, `telegram-bot` (+ RU/EN варіанти) | P0 |
| i18n EN | locale файли, hreflang у `extra_head`, URL patterns | P1 |
| Case pages | portfolio detail templates + seed/CMS; оновлення `llms.txt` | P2 |
| URL stabilize | urls + redirects middleware/nginx/`django.contrib.redirects` | P1 open |
| Analytics | GTM/GA4 — LLM referrer exploration (без нових пікселів «для галочки») | P3 |

---

## Що НЕ робити зараз

- Нові marketing pixels / CAPI «для AEO».
- Email lists / newsletter scrape під citability.
- Invented case studies або чужі лого з вигаданими цифрами.
- Rename URL mid-flight **без** 301 і без синхрону Ads final URL.
- Блокувати всі LLM-боти «про запас».
- Crawl-delay.
- Міняти Soft 250/500/800 € або Ads RSA mid-campaign без QA.
- Публікувати фейкову адресу / LocalBusiness без офісу.
- Тягнути `/proposal/`, `/demo/`, thank-you в sitemap або `llms.txt`.
- Масовий rewrite блогу «під LLM» у P0 (спочатку інфраструктура + LP).

---

## Ризики релевантності реклами і мітигація

| Ризик | Як зламає Ads | Мітигація |
|-------|---------------|-----------|
| Ціна в `llms.txt`/schema ≠ Ads | Низький message match, скарги, QS | Єдине джерело правди = LP copy; `llms.txt` і Offer лише копіюють LP; Soft € lock |
| Rewrite hero mid-flight | Landing experience / Expected CTR | Staged deploy; diff before/after; QA checklist; rollback path |
| Canonical вказує не на Ads final URL | Дублікати, «не той» лендінг у AI Overview | hreflang+canonical узгодити з Ads final URL до цитування в `llms.txt` |
| v2 → clean URL без 301 | 404 з старих оголошень | Спочатку 301 + оновлення Ads, потім `llms.txt` |
| Case з цифрами без дозволу | Юридичний/репутаційний; недовіра LLM | P2 gate: клієнтський OK |
| Блок Perplexity/Claude | Втрата citability-каналу | Блокувати лише GPTBot за потреби; search LLM bots leave open |
| Sitemap знову 500 після деплою | Втрата індексу | Тест на CI + smoke `curl -I` після релізу |

**Правило staged deploy:** P0 schema/`llms`/sitemap → verify → потім hero copy на 1 LP → Ads QA → решта LP.

---

## Чекліст тижневої перевірки питань користувача

Прогоняти **щопонеділка** (Europe/Kyiv) у ChatGPT, Perplexity, Claude (web); фіксувати цитату + URL.

1. «Скільки коштує корпоративний сайт у PrometeyLabs?»
2. «Скільки коштує інтернет-магазин PrometeyLabs?»
3. «Telegram-бот розробка PrometeyLabs ціна»
4. «PrometeyLabs контакти / телефон / email»
5. «PrometeyLabs portfolio / кейси» (чи не вигадує цифри)
6. «Різниця лендінг vs корпоративний vs магазин PrometeyLabs»
7. Англійською: “PrometeyLabs corporate website price EUR”
8. «Чи є офіс PrometeyLabs адреса» (очікування: без фейкової вулиці)
9. Перевірка реферерів у аналітиці: `chatgpt.com`, `perplexity.ai`, `claude.ai` (або аналоги)
10. Spot-check: цитована ціна == Soft/Ads; цитована URL ∈ sitemap і ≠ proposal/demo

**Pass:** ціна й офер збігаються; URL публічний; немає invented cases.  
**Fail →** не крутити нову Ads copy; фіксити джерело (LP/`llms.txt`/schema) і повторити check.

---

## Відкриті рішення

### A. Стабілізувати `/corporate-website-v2/` + `/internet-shop-v2/` vs clean URL + redirects

| Варіант | Плюси | Мінуси | Рекомендація |
|---------|-------|--------|--------------|
| **Stabilize v2** | Нуль ризику для поточних Ads final URL; швидкий P0 `llms.txt` | «v2» у URL виглядає тимчасово | **За замовчуванням для P0–P1**, якщо Ads уже крутять v2 |
| **Clean URL + 301** | Чистіші цитати надовго | Потрібні 301, оновлення Ads, GSC, `llms.txt`, hreflang — one-time вікно | Лише як окремий реліз **до** широкого LLM-цитування; не mid-campaign без QA |

**Рішення потрібне від Андрія перед P1 URL-роботою.** До рішення: у `llms.txt` цитувати **поточні канонічні** URL (ті самі, що Ads final URL).

### B. Блокувати GPTBot чи ні

- Так — менше тренувального скрейпу; search-цитати через інші боти лишаються.  
- Ні — максимальна поверхня для майбутніх GPT-search фіч.  
**За замовчуванням у плані:** опційно, окремим комітом після P0.

### C. Чи додавати Soft `/rozrobka-sajtiv/` у `llms.txt` як hub

Так, якщо Soft лишається Ads-сумісним hub з 250/500/800; ні — якщо хочемо цитувати лише product LP. Узгодити з Ads structure.

---

## Порядок виконання (коротко)

```
P0 day1:  sitemap 500 → llms.txt → schema Offer/Org → hero cite×3 (staged)
P1:       robots LLM policy → EN mirrors/hreflang → URL decision
P2:       case pages only with client OK → 2 links in llms.txt
P3:       weekly LLM queries + referrer analytics
```

**Task A complete = цей файл.** Імплементація AEO — окремі таски після approve плану.
