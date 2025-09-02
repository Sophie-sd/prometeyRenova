# Інструкції з розгортання Prometey Renova

## Налаштування для Render.com

### 1. Обов'язкові змінні оточення

Встановіть наступні змінні в Dashboard → Environment Variables:

**Обов'язкові:**
- `SECRET_KEY` - Django secret key (Render може згенерувати автоматично)
- `DEBUG` = `False`
- `DJANGO_SETTINGS_MODULE` = `prometey_project.settings`
- `PYTHON_VERSION` = `3.11.0`

**База даних:**
- `DATABASE_URL` - URL до PostgreSQL бази даних (отримується від Render при створенні PostgreSQL сервісу)

**Хости:**
- `ALLOWED_HOSTS` = `your-app-name.onrender.com`
- `RENDER_EXTERNAL_URL` = `https://your-app-name.onrender.com`

**Безпека:**
- `SECURE_SSL_REDIRECT` = `True`

### 2. Створення PostgreSQL бази даних

1. В Dashboard Render створіть новий PostgreSQL сервіс
2. Скопіюйте DATABASE_URL з інформації про базу даних
3. Додайте DATABASE_URL як змінну оточення у вашому web сервісі

### 3. Структура файлів

Переконайтеся що у вас є:
- `requirements.txt` - всі залежності Python
- `render.yaml` - конфігурація для Render
- `prometey_project/settings.py` - налаштування Django

### 4. Локальна розробка

Для локальної розробки створіть файл `.env`:

```
DEBUG=True
SECRET_KEY=your-local-secret-key
DATABASE_URL=  # Залишити порожнім для SQLite
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Вирішення проблем

Якщо build падає з помилкою "No support for ''":
- Перевірте чи встановлена змінна DATABASE_URL
- Якщо DATABASE_URL порожня, система автоматично використовуватиме SQLite

### 6. Первинне розгортання

1. Підключіть GitHub репозиторій до Render
2. Створіть PostgreSQL сервіс
3. Створіть Web Service з render.yaml
4. Встановіть змінні оточення
5. Запустіть розгортання

## Структура проекту

```
prometey_project/
├── apps/                # Django додатки
├── static/             # Статичні файли
├── templates/          # HTML шаблони
├── prometey_project/   # Налаштування Django
├── requirements.txt    # Python залежності
├── render.yaml        # Конфігурація Render
└── manage.py          # Django management
```
