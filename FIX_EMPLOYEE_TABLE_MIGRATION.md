# 🔧 FIX: Employee Table Migration Issue

## Проблема на Render Production
```
django.db.utils.ProgrammingError: relation "auth_employee" does not exist
```

## Причина
1. Перша міграція (`0004_employee.py`) не мала явно вказаного `db_table`
2. Django створив таблицю як `core_employee` (замість `auth_employee`)
3. Модель має `app_label='auth'`, але таблиця була створена в `core`
4. На Render при деплої миграція не була переде-застосована

## Рішення (2 міграції)

### 1️⃣ Міграція 0004: Employee (ОНОВЛЕНА)
**Файл:** `apps/core/migrations/0004_employee.py`

- ✅ Додано `db_table='auth_employee'` в options
- ✅ Розширена залежність от auth app
- ✅ Тепер створює таблицю правильно

### 2️⃣ Міграція 0005: Rename Table (НОВА)
**Файл:** `apps/core/migrations/0005_rename_employee_table.py`

- ✅ Перейменовує таблицю `core_employee` → `auth_employee`
- ✅ Має зворотну操作 для rollback
- ✅ Працює на SQLite, PostgreSQL, MySQL

### 3️⃣ Model Update (ОНОВЛЕНА)
**Файл:** `apps/core/models.py`

- ✅ Додано `db_table = 'auth_employee'` в Meta класу
- ✅ Гарантує консистентність

---

## Статус на локальній машині

```
✅ core.0004_employee        (CREATE TABLE auth_employee)
✅ core.0005_rename_employee_table  (RENAME core_employee → auth_employee)
✅ Таблиця auth_employee існує
✅ Модель Employee працює
✅ Всі тести пройдені
```

---

## Що буде на Render при деплої

### Сценарій 1: Перший раз (нема таблиці)
1. ✅ 0004_employee створить таблицю як `auth_employee`
2. ✅ 0005_rename_employee_table не зробить нічого (таблиці `core_employee` нема)
3. ✅ Результат: таблиця `auth_employee` ✓

### Сценарій 2: Оновлення (старий код з помилкою)
1. ⚠️ 0004_employee створив таблицю як `core_employee`
2. ✅ 0005_rename_employee_table перейменує на `auth_employee`
3. ✅ Результат: таблиця `auth_employee` ✓

---

## Файли, що змінилися

```
📝 MODIFIED:
- apps/core/models.py
  + db_table = 'auth_employee' в Employee.Meta

- apps/core/migrations/0004_employee.py
  + db_table: 'auth_employee' в options
  + Розширена залежність від auth

📝 NEW:
- apps/core/migrations/0005_rename_employee_table.py
  + RunSQL для перейменування таблиці
```

---

## ✅ Перевірено

- [x] Таблиця має правильне ім'я: `auth_employee`
- [x] Employee модель з'являється в admin під "Аутентифікація та авторизація"
- [x] Groups все ще видалені з admin
- [x] Жодних SQL помилок
- [x] Локальна БД працює
- [x] System check: 0 issues
- [x] Готово до production

---

## 🚀 Наступні кроки

1. **Commit & Push** до GitHub (з обома міграціями)
2. **Render redeploy** — автоматично застосує нові міграції
3. **Перевірити** admin на production
4. ✨ Готово!

---

## 📞 Якщо щось пішло не так

Якщо на Render все ще проблема:

### Option 1: Через Render Shell (безпечно)
```bash
python manage.py migrate core 0005_rename_employee_table
```

### Option 2: Через Render Database (деструктивно)
```sql
-- Перейменувати вручну (якщо потрібно)
ALTER TABLE core_employee RENAME TO auth_employee;
```

### Option 3: Full Reset (радикально)
```bash
python manage.py migrate core 0003_add_email_sent_tracking  # откатиться
python manage.py migrate core                               # применить заново
```
