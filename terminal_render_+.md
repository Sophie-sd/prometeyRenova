# 🚀 Render Remote Terminal - Quick Setup

Швидке налаштування віддаленого доступу до Render сервера через термінал.

---

## 📋 Крок 1: Отримати API ключ

1. Відкрити https://dashboard.render.com/account/api-keys
2. Натиснути **"Create API Key"**
3. Скопіювати ключ (формат: `rnd_XXXXXXXXXXXXX`)

---

## 📋 Крок 2: Встановити Render CLI

```bash
# macOS
brew install render

# Перевірка
render --version
```

---

## 📋 Крок 3: Налаштувати CLI

```bash
# Спосіб 1: Інтерактивний логін
render login

# Спосіб 2: Через API ключ (для автоматизації)
mkdir -p ~/.render
echo "api_key: rnd_YOUR_API_KEY_HERE" > ~/.render/config.yaml
```

---

## 📋 Крок 4: Знайти Service ID

```bash
export RENDER_API_KEY=rnd_YOUR_API_KEY_HERE
render services list -o json
```

Скопіювати `"id": "srv-xxxxx"` вашого сервісу.

---

## 📋 Крок 5: Створити скрипт виконання команд

Створити файл `render-cmd.sh`:

```bash
#!/bin/bash
# Render Remote Command Executor

API_KEY="rnd_YOUR_API_KEY_HERE"
SERVICE="srv-YOUR_SERVICE_ID_HERE"

if [ -z "$1" ]; then
    echo "Usage: ./render-cmd.sh 'command'"
    exit 1
fi

export RENDER_API_KEY=$API_KEY

echo "🚀 Executing: $1"

# Create job
JOB_JSON=$(render jobs create $SERVICE --start-command "$1" -o json 2>&1)
JOB_ID=$(echo "$JOB_JSON" | grep -o 'job-[a-z0-9]*' | head -1)

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to create job"
    exit 1
fi

echo "⏳ Job $JOB_ID running..."

# Wait for completion
for i in {1..60}; do
    sleep 1
    if [ $((i % 5)) -eq 0 ]; then
        STATUS=$(render jobs list $SERVICE -o json 2>/dev/null | grep -A 3 "$JOB_ID" | grep "status" | cut -d'"' -f4)
        if [ "$STATUS" = "succeeded" ] || [ "$STATUS" = "failed" ]; then
            break
        fi
    fi
done

echo ""
echo "📄 Output:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
render logs -r $JOB_ID --limit 500 -o text 2>/dev/null | tail -n +2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Complete"
```

Зробити виконуваним:
```bash
chmod +x render-cmd.sh
```

---

## 🎯 Використання

### Виконання команд:
```bash
./render-cmd.sh "python manage.py check"
./render-cmd.sh "ls -la"
./render-cmd.sh "df -h"
./render-cmd.sh "pip list"
```

### Перегляд логів:
```bash
export RENDER_API_KEY=rnd_YOUR_API_KEY_HERE

# Останні 100 логів
render logs -r srv-YOUR_SERVICE_ID --limit 100 -o text

# Real-time логи
render logs -r srv-YOUR_SERVICE_ID --tail -o text

# З фільтрацією
render logs -r srv-YOUR_SERVICE_ID --level error --limit 50 -o text
```

### Управління сервісом:
```bash
# Список сервісів
render services list -o json

# Історія деплоїв
render deploys list srv-YOUR_SERVICE_ID -o json

# Перезапуск
render restart srv-YOUR_SERVICE_ID -o json

# Список jobs
render jobs list srv-YOUR_SERVICE_ID -o json
```

---

## 🔐 Безпека

**Важливо!** Додати в `.gitignore`:
```
render-cmd.sh
terminal_render_+.md
```

Або видалити API ключ з файлу та використовувати змінні середовища:
```bash
export RENDER_API_KEY=rnd_YOUR_API_KEY_HERE
./render-cmd.sh "command"
```

---

## 🎯 Корисні команди

### Django:
```bash
./render-cmd.sh "python manage.py check --deploy"
./render-cmd.sh "python manage.py showmigrations"
./render-cmd.sh "python manage.py collectstatic --noinput"
./render-cmd.sh "python manage.py createsuperuser"
```

### Системна діагностика:
```bash
./render-cmd.sh "df -h"              # Дисковий простір
./render-cmd.sh "free -m"            # Пам'ять
./render-cmd.sh "ps aux | head -10"  # Процеси
./render-cmd.sh "env | grep DJANGO"  # Змінні середовища
```

### База даних:
```bash
./render-cmd.sh "ls -lh db.sqlite3"
./render-cmd.sh "sqlite3 db.sqlite3 '.tables'"
./render-cmd.sh "sqlite3 db.sqlite3 'SELECT COUNT(*) FROM auth_user;'"
```

---

## ⚡ Швидкі алиаси (опціонально)

Додати в `~/.zshrc` або `~/.bashrc`:

```bash
alias rcmd='cd /path/to/project && ./render-cmd.sh'
alias rlogs='export RENDER_API_KEY=rnd_YOUR_KEY && render logs -r srv-YOUR_ID --tail -o text'
```

Після цього:
```bash
rcmd "python manage.py check"
rlogs
```

---

## 🔄 Troubleshooting

### Job не виконується:
- Перевірити Service ID: `render services list -o json`
- Перевірити API ключ: `render whoami -o text`
- Подивитися логи job: `render logs -r job-xxxxx -o text`

### Timeout:
- Jobs мають обмеження за часом (5-10 хвилин)
- Для тривалих операцій використати background jobs

### Permission denied:
- Filesystem read-only (окрім `/tmp`)
- Для змін коду робити новий deploy

---

**Готово!** 🎉 Тепер можна виконувати команди на Render сервері з локального терміналу.

