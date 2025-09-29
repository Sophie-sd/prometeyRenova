# 🔄 BACKUP - Міграція на новий блупринт

## 📅 Дата міграції: 29 вересня 2025

### 🏗️ Поточна структура (ДО міграції):
```
PrometeyRenova/
├── prometey_project/        ← Поточний головний модуль
│   ├── settings_base.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── config/                  ← Workaround для Render
│   ├── settings.py (redirect)
│   └── wsgi.py
├── apps/
│   ├── core/
│   ├── blog/
│   ├── events/
│   └── payment/
├── templates/
├── static/
├── requirements.txt
├── render.yaml
└── build.sh
```

### 🎯 Нова структура (ПІСЛЯ міграції):
```
PrometeyRenova/
├── config/                  ← Новий головний модуль
│   ├── __init__.py
│   ├── settings.py          ← Повністю новий файл
│   ├── urls.py              ← Оновлений з i18n
│   ├── wsgi.py
│   └── asgi.py
├── apps/                    ← Зберігаються без змін
├── locale/                  ← НОВА папка для перекладів
│   ├── uk/LC_MESSAGES/
│   └── en/LC_MESSAGES/
├── templates/               ← Доповнені i18n тегами
├── static/
├── requirements.txt         ← Оновлений
├── render.yaml              ← Оновлений
└── build.sh                 ← Оновлений
```

### 📋 Environment змінні на Render (зберегти):
- SECRET_KEY ✅
- DEBUG=False ✅  
- ALLOWED_HOSTS ✅
- DATABASE_URL ✅
- EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS ✅
- EMAIL_HOST_USER, EMAIL_HOST_PASSWORD ✅
- MONOBANK_TOKEN ✅
- SITE_URL ✅

### 🚀 План дій:
1. ✅ Створити backup поточних налаштувань
2. 🔄 Перенести config/ як головний модуль
3. 🌍 Додати мультимовність (UK/EN)
4. 🔧 Оновити render.yaml та requirements.txt
5. 🧪 Локальне тестування
6. 🚢 Deploy на Render

### ⚠️ Критичні моменти:
- Зберегти всі поточні додатки без змін
- Зберегти домен prometeylabs.com
- Зберегти базу даних та environment змінні
- Додати мультимовність без ламання існуючого функціоналу

