# Чекліст: EU/CZ compliance та локалізація prometeylabs.com

Джерело: бриф користувача (05.09.2026) + план `EU/CZ compliance та локалізація` (10 кроків).
Норми перевірені на актуальність станом на 05.09.2026 (Digital Omnibus, ODR-платформа, адекватність UA, GCM v2, ÚOOÚ, §1837 NOZ).

Позначення «Хто»:
- **код** — виконує агент у репозиторії
- **CookieYes** — налаштування в дашборді CookieYes (акаунт користувача)
- **носій CS** — професійний носій чеської мови (вичитка перекладу)
- **ручний тест** — QA після деплою (браузер/девайс/Tag Assistant)
- **ви** — рішення/дані від власника проєкту

---

## 1. Юридичні сторінки сайту

| # | Пункт | Файл/де | Як перевірити | Хто | Крок плану |
|---|---|---|---|---|---|
| 1.1 | Privacy Policy: розділ про передачу даних з ЄС в Україну (третя країна без адекватності) | `templates/pages/privacy.html`, `privacy-en.html`, `privacy-ru.html`, `privacy-cs.html` | Розділ згадує SCC (Рішення ЄК 2021/914), ст. 44-46 GDPR, Україну як третю країну | код | 5, 6 |
| 1.2 | Privacy Policy: правова підстава (договір / згода) по кожній меті обробки | той самий файл | Таблиця/список: мета → правова підстава (ст. 6(1)(a)/(b)/(f) GDPR) | код | 5, 6 |
| 1.3 | Privacy Policy: контакт відповідальної особи за дані | той самий файл, `footer.html` | Email/ПІБ відповідальної особи вказано явно (ФОП без обов'язкового DPO за ст. 37) | код | 5, 6 |
| 1.4 | Cookie Policy: категорії cookies (необхідні / аналітика / маркетинг) + провайдер + мета | `templates/pages/cookies.html` (+en/ru/cs) | Таблиця з 3-4 категоріями, назвами cookies, провайдером | код | 5, 6 |
| 1.5 | Cookie Policy: термін зберігання кожної категорії | той самий файл | Колонка «Термін» у таблиці (напр. `_ga` — 2 роки) | код | 5, 6 |
| 1.6 | Cookie Policy: як відмовитись / відкликати згоду | той самий файл, посилання у футері | Кнопка/лінк «Налаштування cookie» (CookieYes revisit widget) працює | код + CookieYes | 5, 6, 8 |
| 1.7 | Offer: пункт про відмову від 14-денного відступлення (EN/CS) | `templates/pages/offer.html` (+en/cs) | Посилання на ст. 16(a)/(c) Directive 2011/83/EU та §1837(a)/(l) NOZ (CZ) | код | 6 |
| 1.8 | Offer: чекбокс явної згоди на відмову від відступлення при оформленні замовлення | `templates/payment/payment_page.html` | Чекбокс **не** pre-checked, `required`, серверна валідація без нього — 400 | код | 7 |
| 1.9 | Offer: ідентифікаційні дані трейдера (ФОП, реєстр. номер, адреса, email) | `templates/pages/offer.html` §11 | ФОП Дмитренко С.Д., РНОКПП 3770706565, адреса, `info@prometeylabs.com` — присутні | код | 5 (вже є, перевірити) |
| 1.10 | Impressum-блок у футері | `templates/components/footer.html` | Юр. назва, номер реєстрації ФОП, email/адреса видимі на кожній сторінці | код | 7 |
| 1.11 | Переклад усіх юридичних сторінок на чеську (професійний, не лише машинний) | `pages/*-cs.html` | Чорновий переклад від агента + **обов'язкова вичитка носієм** перед публікацією | код + носій CS | 6 |
| 1.12 | Прибрати посилання на ODR-платформу (закрита 20.07.2025), якщо десь є | весь `templates/` | `grep -ri "ec.europa.eu/consumers/odr"` — 0 результатів | код (вже перевірено: 0) | 5 |

## 2. Cookie-банер / Consent Mode

| # | Пункт | Де | Як перевірити | Хто | Крок плану |
|---|---|---|---|---|---|
| 2.1 | Встановити Google-сертифікований CMP (CookieYes) | `templates/base.html`, `.env COOKIEYES_ID` | Банер CookieYes рендериться на проді з реальним Site ID | код + CookieYes | 8 |
| 2.2 | Google Consent Mode v2: 4 сигнали (`ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`) | `base.html` inline `gtag('consent','default', …)` | Tag Assistant → Consent tab показує всі 4 параметри | код | 8 |
| 2.3 | Кнопки «Прийняти всі» / «Відхилити всі» однакового розміру й кольору на 1-му шарі, без cookie-wall | CookieYes dashboard → Cookie Banner | Візуальна перевірка банера на всіх мовах | CookieYes | 8 |
| 2.4 | До згоди — всі неесенційні скрипти блокуються (GA4, Google Ads тег, ремаркетинг, FB Pixel) | `base.html`, `middleware.py` CSP | DevTools Network до кліку: немає `_ga`, `fbp` cookies; GTM у cookieless/advanced режимі | код + ручний тест | 8 |
| 2.5 | Термін дії згоди — 12 місяців | CookieYes → Advanced Settings → Consent Expiration | Значення = 365 днів | CookieYes | 8 |
| 2.6 | Повторний запит не раніше 6 місяців після відмови | CookieYes (те саме поле покриває і 12, і 6 міс. за правилами ÚOOÚ) | Задокументовано в Cookie Policy §розділ «Термін згоди» | CookieYes + код | 8 |
| 2.7 | E2E тест: передача конверсій у Google Ads/GA4 після «Прийняти» | Tag Assistant, GA4 DebugView, `/thank-you/` | Реальний клік «Прийняти» → подія в GA4 DebugView + Google Ads conversion | ручний тест | 8 |

## 3. Чеська версія сайту

| # | Пункт | Де | Як перевірити | Хто | Крок плану |
|---|---|---|---|---|---|
| 3.1 | `/cs/` підкаталог з hreflang (en, uk, cs, ru, x-default) | `config/settings.py LANGUAGES`, `apps/core/templatetags/seo_tags.py`, `base.html` | `/cs/` відкривається; `curl -I https://prometeylabs.com/cs/` → 200; `view-source` показує 5 `<link hreflang>` | код | 1 (виконано) |
| 3.2 | Професійний переклад: головна, портфоліо, послуги, калькулятор, контакти | `locale/cs/LC_MESSAGES/django.po` | Кожна сторінка без кирилиці на `/cs/` | код + носій CS | 2, 4 |
| 3.3 | Окремі landing-сторінки під напрямки послуг (tvorba webu, e-shopy, webové aplikace, mobilní aplikace) | `pages/internet-shop-v2.html`, `corporate-website-v2.html` (2 з 4 вже є) | `webové aplikace` / `mobilní aplikace` — нових сторінок немає, потребують окремого рішення (Крок 11, поза меню) | код + ви | 3, 4, 11 |
| 3.4 | Калькулятор: ціна в EUR («od X €», Kč як «orientační») | `templates/pages/calculator.html`, `static/js/calculator.js` | На `/cs/calculator/` результат показує «od X €» | код | 10 |
| 3.5 | Мобільна та iOS Safari адаптація (форми, калькулятор, попапи) | всі форми/модалки | Ручний тест на iPhone/iPad Safari: sticky, 100vh/100dvh, zoom при фокусі інпута (`font-size ≥16px`) | ручний тест | 9, 10 |
| 3.6 | Core Web Vitals | `base-bundle.css`, `home-bundle.js` | Lighthouse mobile ≥ 90 на `/cs/` меню-сторінках після додавання CookieYes | ручний тест | 10 |

## 4. Форма заявки (редизайн)

| # | Поле/вимога | Де | Як перевірити | Хто | Крок плану |
|---|---|---|---|---|---|
| 4.1 | Ім'я* | `templates/components/lead_form_fields.html` | Обов'язкове поле, валідація на фронті й бекенді | код | 9 |
| 4.2 | Email* | той самий | Обов'язкове, формат email валідується | код | 9 |
| 4.3 | Телефон / месенджер (WhatsApp / Telegram / Viber) з вибором | той самий, `FormSubmission.messenger_type` | Select/радіо з 4 варіантами | код | 9 |
| 4.4 | Тип проєкту (сайт / e-shop / веб-застосунок / інше) — dropdown | `FormSubmission.project_type` | Dropdown із 4 опціями, зберігається в БД | код | 9 |
| 4.5 | Орієнтовний бюджет — dropdown | `FormSubmission.budget` | Dropdown, зберігається в БД + видно в адмінці/KeyCRM | код | 9 |
| 4.6 | Бажана мова спілкування (čeština / English) | `FormSubmission.preferred_language` | Select, значення в адмінці | код | 9 |
| 4.7 | Чекбокс згоди на обробку даних з посиланням на Privacy Policy, обов'язковий, **не** pre-checked | той самий партіал | HTML: без `checked`; `required`; серверна 400 без згоди | код | 9 |
| 4.8 | Текст-очікування біля кнопки («Odpovíme e-mailem do 24 hodin…») | той самий партіал | Текст присутній на `/cs/` формах через `{% trans %}` | код | 9 |
| 4.9 | Стратегічна рекомендація (перекладач лише для кваліфікованих лідів, перше спілкування текстом) | процес, не код | Задокументовано нижче в розділі 6 | ви (процес) | — |

## 5. Impressum / трейдер (додатково до розділу 1)

| # | Пункт | Де | Як перевірити | Хто | Крок плану |
|---|---|---|---|---|---|
| 5.1 | Юридична назва ФОП у футері | `footer.html` | Видно на кожній сторінці сайту | код | 7 |
| 5.2 | Номер реєстрації ФОП (РНОКПП) у футері | `footer.html` | Видно | код | 7 |
| 5.3 | Контактний email/адреса у футері | `footer.html` | Видно | код | 7 |
| 5.4 | Дані редаговані з адмінки (не хардкод) | `apps/core/models.py SiteContactSettings` | Поля `legal_name`, `registration_number`, `legal_address` в Unfold admin | код | 7 |

## 6. Native review CS — переклад Кроку 4 (обов'язково перед публікацією `/cs/`)

Машинний переклад (агент, не носій мови) 724 рядків `msgstr` у `locale/cs/LC_MESSAGES/django.po` для shell + меню-сторінок. Термінологія: `tvorba webu`, `e-shop`, `webová aplikace`, `mobilní aplikace`, `nezávazná poptávka`, `landing page`. **Перед публікацією `/cs/` потрібна вичитка носієм чеської** за списком файлів нижче (перевіряти саме відображений текст на `/cs/…`, не сам `.po`):

- [ ] `templates/base.html`, `components/header.html`, `components/footer.html`, `components/burger_menu.html`, `components/modals.html`, `components/mobile_contact_fab.html` — шапка/футер/бургер/попапи (усі сторінки)
- [ ] `pages/home.html` + `components/home/redesign_why.html`, `home_process_intro.html`, `redesign_services_piano.html`, `redesign_clients.html`, `redesign_cta.html`, `components/process_block.html`, `components/pb_step_heading.html` — `/cs/`
- [ ] `pages/portfolio.html` (текст-каркас сторінки; **картки проєктів — окремо, див. нижче**) — `/cs/portfolio/`
- [ ] `pages/internet-shop-v2.html` + 11 файлів `components/internet_shop_v2/*` — `/cs/internet-shop-v2/`
- [ ] `pages/corporate-website-v2.html` + 9 файлів `components/corporate_website_v2/*` — `/cs/corporate-website-v2/`
- [ ] `pages/calculator.html` — `/cs/calculator/`
- [ ] `pages/blog.html`, `blog_detail.html`, `blog_search.html` (каркас; **тексти статей — окремо, див. нижче**) — `/cs/blog/`
- [ ] `pages/contacts.html` — `/cs/contacts/`
- [ ] `apps/core/views.py` — title/meta (og:title, description) усіх вищезгаданих сторінок

**Виявлена й виправлена супутня помилка (усі мови):** `pages/portfolio.html` мав `{% trans %}` з рядком, розбитим на 2 фізичні рядки в шаблоні — Django `makemessages`/рендер не розпізнавали тег, і на `/`, `/en/`, `/ru/`, `/cs/portfolio/` у `<meta description>` показувався сирий нерозпарсений `{% trans "..." %}`. Виправлено (рядок в один physical line) + перекладено EN/RU/CS. Заразом виправлено 20+ `fuzzy`-записів у `process_block.html`/`pb_step_heading.html` (EN мав змішані переклади типу «Процес створення сайту» → «Website Creation Request», RU — «Процес створення сайту» → «Возврат средств» — це блок процесу на головній сторінці, показувався з чужим текстом в EN і RU) та ще 14 `fuzzy`/хибних рядків meta-описів і дрібних лейблів (EN: cookie-policy description показував refund-текст; RU: portfolio meta показував homepage-текст, «Послуги» → «Портфолио», «Пожиттєва гарантія…» → чужий текст).

**Поза межами Кроку 4 (виявлено, потребує окремого рішення):** картки проєктів на `/portfolio/` (`PortfolioProject.title/description` — DB-контент) та статті блогу (`BlogPost` — DB-контент) підтримують лише `uk`/`ru`-поля (`title_ru`, `subtitle_ru` тощо); `en`/`cs`-полів у моделі немає, тому на `/en/portfolio/` та `/cs/portfolio/` (аналогічно `/blog/`) картки й статті показують український текст. Це контент, не рядки `.po` — виправлення вимагає нових полів моделі (`title_en`/`title_cs` тощо) + перекладу контенту, не входить у «Крок 4: django.po для shell + меню-сторінок». Потребує вашого рішення: (а) додати нові мовні поля й перекласти вручну, (б) залишити uk/ru-fallback навмисно (менш критично для SEO, ніж шаблонний текст).

## 7. Native review — юридичні сторінки CS/EN (Крок 6, обов'язково перед публікацією)

Машинний переклад (агент) 5 юридичних документів на EN та CS: `privacy`, `cookies`, `offer`, `refund`, `intellectual-property`. Юридична термінологія (GDPR, ст. 6/28/37, Directive 2011/83/EU, §1837/§1824a NOZ) — **перед публікацією обов'язкова вичитка носієм чеської мови з юридичною освітою або консультація з місцевим юристом** (це договірні та GDPR-документи, а не маркетинговий текст):

- [ ] `pages/privacy-cs.html` — `/cs/privacy/` (правові підстави ст. 6(1), DPO-застереження ст. 37)
- [ ] `pages/cookies-cs.html` — `/cs/cookies/` (таблиця cookies, Google Consent Mode v2, 12/6 міс.)
- [ ] `pages/offer-cs.html` — `/cs/offer/` (§11 «Право на відступлення» — §1837 písm. a)/l), §1824a NOZ — **найвищий пріоритет вичитки**, безпосередньо впливає на права споживача)
- [ ] `pages/refund-cs.html` — `/cs/refund/`
- [ ] `pages/intellectual-property-cs.html` — `/cs/intellectual-property/`

EN-версії (`*-en.html`) використовують стандартну GDPR/Directive 2011/83/EU термінологію — ризик нижчий, але вичитка носієм англійської з юридичним досвідом також рекомендована для `offer-en.html` §11 (Art. 16(a)/(c)) перед показом реальним EU-клієнтам.

**Примітка щодо обсягу:** §11 «Право на відступлення» (EU-споживачі) додано **лише** в `offer-en.html`/`offer-cs.html` — відповідно до чекліста (п. 1.7, «EN/CS»), оскільки це вимога права ЄС (Directive 2011/83/EU, §1837 NOZ), не застосовна до українських замовників за законодавством України; `offer.html`/`offer-ru.html` цей пункт свідомо не мають.

## 8. Процес роботи з лідами (не код — рекомендація, фіксуємо як пункт контролю)

- [ ] Перше спілкування з новим лідом — **текстом** (email/WhatsApp), переклад через DeepL/Google Translate.
- [ ] Живий перекладач підключається лише для **кваліфікованих** лідів (бюджет + тип проєкту відповідають мінімальному порогу) — на етапі фінальної презентації КП.
- [ ] Критерій кваліфікації ліда = поля `budget` + `project_type` з нової форми (Крок 9).

---

## Що потрібне від вас (лише прод — код закрито)

Після деплою коду агент більше нічого не змінює в репо для EU/CZ. Лишається ручне:

1. **Render → Environment → `COOKIEYES_ID`**  
   Site ID з CookieYes (слот уже в [`render.yaml`](../render.yaml) з `sync: false`). Без значення банер не рендериться (`{% if COOKIEYES_ID %}` у `base.html`).

2. **CookieYes dashboard**  
   Support GCM ON; шаблон GDPR; Accept/Reject однакові на 1-му шарі, без cookie-wall; Consent Expiration = 365; Revisit Consent ON; мови uk/en/ru/cs; Consent Log ON; auto-block не-Google скриптів.

3. **GTM (`GTM-K2FVPPTK`) Consent Settings**  
   На тегах GA4 / Ads / FB: require `analytics_storage` / `ad_storage` + `ad_user_data` / `ad_personalization`.

4. **E2E на https://prometeylabs.com/cs/**  
   Tag Assistant: до Accept немає `_ga`; після Accept — granted + подія в GA4 DebugView; Google Ads conversion на `/thank-you/`.

5. **Smoke після деплою (iPhone Safari, опційно)**  
   Форми / модалки / `/cs/calculator/` → «od X €»; sticky header; CookieYes Accept/Reject.

**Відкладено (не блокер прод-налаштувань):** вичитка носієм CS (розділи 6–7); крок 11 (`webové aplikace` / `mobilní aplikace`); EN/CS поля контенту портфоліо/блогу в БД.

**Ціни калькулятора:** дефолт з головної (250 / 400 / 500 / 800 / 1500 €) у `calculator_estimate.py` / `calculator-prices.js` — змінювати лише якщо потрібні інші діапазони.

**Impressum:** дефолти вже в `SiteContactSettings` (ФОП Дмитренко…); правити з Unfold за потреби.

### CWV baseline (код, без CookieYes)
- `base-bundle.css` ≈ 100 KB (`100702` байт)
- `home-bundle.js` ≈ 72 KB (`72688` байт)
- Повтор Lighthouse mobile ≥ 90 на `/cs/` — **після** увімкнення CookieYes на проді (п. 4).

## Прогрес виконання (оновлювати по кроках)

- [x] **Крок 1** — Чекліст (цей файл) + `cs` у `LANGUAGES`, `locale/cs/`, hreflang templatetag, sitemap alternates.
- [x] **Крок 2** — Заповнено 40 порожніх `msgstr` в `locale/en` та 26 у `locale/ru` для `apps/core/views.py`, `templates/base.html`, `home_process_intro.html`, `process_block.html`, `process_flow_block.html`, `calculator.html`, `portfolio.html`. `compilemessages`, `manage.py check`, ручна перевірка через test client — без кириличних заглушок на `/en/`, `/ru/` меню-сторінках.
- [x] **Крок 3** — `{% trans %}`/`{% blocktrans trimmed %}` для всіх 2 сторінок (`pages/internet-shop-v2.html`, `corporate-website-v2.html`) + 20 компонентів `internet_shop_v2/*`, `corporate_website_v2/*` (~400 рядків). EN+RU переклад 319+32 нових рядків, знято `fuzzy`-мітки з хибно змерджених рядків (заголовки/навігація/од. виміру). Перевірено та виправлено JS: аварійні хардкод-рядки винесено в `data-*` атрибути шаблонів — валідація телефону (`corporate-website-v2-quiz.js`), aria-label каруселі клієнтів, текст toggle «Читати далі/Згорнути» (`internet-shop-v2.js`), повний i18n інтерактивної демо-адмінки (`internet-shop-v2-admin-mock.js`, 27 підписів через `data-i18n-*` на `admin.html`; демо-дані клієнтів/товарів навмисно залишено українською як флейвор-контент макету). Заразом виправлено 2 суміжні `fuzzy`-баги в спільних `header.html`/`burger_menu.html` (пункти меню «Послуги»/«Інтернет-магазини»/«Корпоративні сайти та лендінги» не показувались перекладеними в RU) та хардкод-посилання в `footer.html`. `compilemessages`, `manage.py check` — 0 помилок; ручний скан через test client `/en/` та `/ru/` обох v2-сторінок — 0 залишкових українських фрагментів у видимому контенті.
- [x] **Крок 4** — Переклад 724 рядків `msgstr` у `locale/cs/LC_MESSAGES/django.po` для shell (`header`/`footer`/`burger_menu`/`modals`/`mobile_contact_fab`) + `home` (+ `process_block`/`pb_step_heading`) + `portfolio` (каркас) + `internet-shop-v2`/`corporate-website-v2` (усі 20 компонентів) + `calculator` + `blog`/`blog_detail`/`blog_search` (каркас) + `contacts` + title/meta з `apps/core/views.py`. Термінологія ринку (`tvorba webu`, `e-shop`, `webová aplikace`, `nezávazná poptávka`). Блок «Native review CS» з переліком файлів — розділ 6 вище. Супутньо виправлено: розбитий на 2 рядки `{% trans %}` у `portfolio.html` (не рендерився/не екстрактувався жодною мовою), 20+ `fuzzy`/хибних записів у `process_block.html` (EN+RU) та 14 інших `fuzzy`/хибних meta-описів (EN+RU) — див. розділ 6. `compilemessages` (uk/en/ru/cs), `manage.py check` — 0 помилок; ручний скан через test client `/`, `/en/`, `/ru/`, `/cs/` для 7 сторінок — 0 кириличних фрагментів поза DB-контентом (портфоліо-картки/статті блогу, брендові назви, адреса) і поза формовими `value=""` ідентифікаторами квізу.
- [x] **Крок 5** — При перевірці виявлено, що `privacy.html`/`cookies.html`/`offer.html`/`refund.html`/`intellectual-property.html` (UA) вже відповідали редакції `.docx` від 22.07.2026 (SCC, Data Processor ст. 28 GDPR, 72h data breach — вже присутні) — переносити текст не було потреби. Виконано інше з обсягу кроку: **(1)** `apps/core/mixins.py` — `LocalizedLegalTemplateMixin(legal_base_name)` з fallback-ланцюжком `ru→ru.html`, `cs→cs.html→en.html`, `en→en.html`, усі → базовий `uk.html`; замінено 5 хендкодних `get_template_names()` у `views.py` (`OfferView`, `PrivacyView`, `CookiesView`, `RefundPolicyView`, `IntellectualPropertyView`) — код став коротшим і готовим під `-cs.html`/`-en.html` з Кроку 6 без подальших змін у `views.py`. **(2)** Додано розділи з блоку «Юридичні рішення», яких не було: у `privacy.html`+`privacy-ru.html` §3.2 — список «мета обробки → правова підстава» (ст. 6(1)(a)/(b)/(c)/(f) GDPR замість загального речення); §9 — назва відповідальної особи (ФОП Дмитренко С.Д.) + застереження про звільнення від обов'язку DPO за ст. 37 GDPR. У `cookies.html`+`cookies-ru.html` §6.5 — згадка Google Consent Mode v2 (cookieless-режим до згоди, 12/6 міс.). Дата «Останнє оновлення» на цих 4 файлах → 5 вересня 2026 (реальна дата випуску); `offer.html`/`refund.html`/`intellectual-property.html` без змін контенту — дата 22.07.2026 лишена (14-денна відмова — окремо, Крок 6-7). **(3)** Підтверджено: 0 згадок ODR-платформи (п. 1.12), усі 5 файлів < 500 рядків. `manage.py check`, `manage.py test apps.core` — 0 помилок; ручний рендер `/`, `/en/`, `/ru/`, `/cs/` × 5 сторінок (20 комбінацій) — коректний fallback-шаблон і дата на кожній.
- [x] **Крок 6** — Створено 10 нових шаблонів: `privacy`/`cookies`/`offer`/`refund`/`intellectual-property` × `-en.html`/`-cs.html` (усі < 300 рядків, підключаються автоматично через `LocalizedLegalTemplateMixin` з Кроку 5 — жодних змін у `views.py` не знадобилось). Title/meta беруться через існуючі `_()` у `views.py` — переклад цих msgid уже готовий з Кроків 2/4 (EN з попередніх кроків, CS із Кроку 4), перевірено рендером `<title>` на всіх 4 мовах. До `offer-en.html`/`offer-cs.html` додано новий §11 «Право на відступлення для споживачів ЄС» (Directive 2011/83/EU art. 16(a)/(c) в EN; §1837 písm. a)/l) + §1824a NOZ в CS) — свідомо **лише** в EN/CS версіях (не в UA/RU — вимога права ЄС, не застосовна до українських замовників), Реквізити Виконавця зсунуто на §12. RU-версії (`*-ru.html`) не потребували синхронізації — контент `offer.html`/`refund.html`/`intellectual-property.html` (UA) не змінювався в Кроці 6, тож RU лишається в синку; `privacy`/`cookies` RU вже синхронізовано в Кроці 5. Перевірено: 0 кириличних фрагментів поза `{% trans %}`/`{% block title %}` у нових файлах (`rg` скан), 0 згадок ODR-платформи (2 фолс-позитиви `podrobn-`/`dodržování`, перевірено вручну), 0 `!important`. `manage.py check`, `manage.py test apps.core` — 0 помилок; ручний рендер `/`, `/en/`, `/ru/`, `/cs/` × 5 сторінок (20 комбінацій) — усі 200, кожна мова показує власний шаблон (не fallback на uk), заголовки й дати коректні. Блок «Native review CS/EN» з переліком файлів і пріоритетом (`offer` — найвищий) — розділ 7 вище.
- [x] **Крок 7** — Impressum: поля `legal_name` / `registration_number` / `legal_address` / `data_protection_email` у `SiteContactSettings` + міграція `0021` + fieldset Unfold + блок `.footer-impressum` (назва, реєстр. №, адреса, email захисту даних, кнопка CookieYes `cky-banner-element`) + CSS планшет/мобіль/iOS. Чекаут: чекбокси `withdrawal_waiver` + `data_consent` на `payment_page.html` (не pre-checked, `required`) — еквайринг і банківський шлях; серверна 400 без обох у `create_invoice` / `record_consent` / тестовому POST; `record_checkout_consent` пише час+IP на `PaymentLink`; readonly fieldset в адмінці. Лист `payment/emails/payment_confirmation.txt` після першого `mark_paid` (webhook) + той самий текст на `payment_success.html` (§1824a NOZ, без ODR). Переклади EN/RU/CS. `compilemessages`, `manage.py check`.
- [x] **Крок 8** — Код: `COOKIEYES_ID` у `settings.py` + `.env.example` + `context_processors` + слот `COOKIEYES_ID` (`sync: false`) у `render.yaml`; у `base.html` порядок consent→CookieYes→GTM; CSP CookieYes. **Лише прод:** Site ID у Render; CookieYes dashboard; GTM Consent Settings; E2E Tag Assistant (див. «Що потрібне від вас»).
- [x] **Крок 9** — Редизайн лідової форми: `FormSubmission` поля `messenger_type` / `project_type` / `budget` / `preferred_language` / `consent_at`/`consent_ip` + міграція `0022`; партіал `lead_form_fields.html` (full + compact) у contacts / call-request-modal / footer; серверна 400 без consent/email; KeyCRM comment; `phone-mask-intl.js` (+420 для cs); `lead-form.css` (iOS ≥16px); переклади EN/RU/CS (consent blocktrans з escaped quotes). Перевірено test client `/en/contacts/`, `/cs/contacts/` — згода перекладена, чекбокс без `checked`.
- [x] **Крок 10** — Калькулятор: `apps/core/calculator_estimate.py` + `static/js/calculator-prices.js` + JSON у `calculator.html`; результат «od X €» / «from €X» + «orientačně ~Y Kč» для cs/en, UAH для uk/ru; модалка `#test-result-modal` замість редіректу на thank-you; CSS secondary price у `modals.css` + `base-bundle.css`. **CWV (виміряно файли):** `base-bundle.css` ≈ 100 KB, `home-bundle.js` ≈ 72 KB. **Дозакриття коду (prod-only leftover):** GDPR email+consent на v2 quiz / free_analysis / легасі shop+corp / calculator `test_submission`; `COOKIEYES_ID` у `render.yaml`; CS CTA «Nezávazná poptávka»; чекліст зведений до прод-ранбуку. Lighthouse mobile з CookieYes + iOS smoke — лише на проді після Site ID.
- [ ] Крок 11 (за рішенням) — landing-сторінки `webové aplikace` / `mobilní aplikace`.

### iOS Safari QA (Крок 10) — ручний чекліст
- [ ] Форми (footer / contacts / call-modal / v2 quiz): focus інпута без zoom (`font-size ≥ 16px`), safe-area.
- [ ] Модалки: `100dvh` / max-height, закриття backdrop, scroll lock.
- [ ] `/cs/calculator/`: wizard кроків, email+consent, submit → модалка з «od X €» + Kč.
- [ ] CookieYes банер (prod ID): Accept/Reject, не блокує LCP критично.
- [ ] Sticky header + burger на iPhone/iPad.
- [ ] `sitewatch` L0/L1 по `/cs/` (якщо CLI доступний у середовищі).

### Прод-ранбук (чеклист виконання)
- [ ] Render: `COOKIEYES_ID` заповнено
- [ ] CookieYes dashboard: GCM / GDPR / 365 / мови / Consent Log
- [ ] GTM Consent Settings на GA4/Ads/FB
- [ ] E2E Tag Assistant + GA4 DebugView на `/cs/`
