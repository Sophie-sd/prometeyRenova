#!/bin/bash

# Build script для Render.com deployment
echo "==> Starting build process..."

# Встановлення залежностей
echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Збір статичних файлів (ВИПРАВЛЕНО: preDeployCommand не працює)
echo "==> Collecting static files in buildCommand..."
python manage.py collectstatic --noinput --clear --verbosity=2

echo "==> DEBUG: Post-collectstatic check..."
echo "Current directory: $(pwd)"
echo "Staticfiles directory exists: $(test -d staticfiles && echo 'YES' || echo 'NO')"

if [ -d staticfiles ]; then
    echo "==> SUCCESS: staticfiles directory created!"
    echo "Staticfiles content:"
    find staticfiles -name "*.css" -o -name "*.js" | head -10
    echo "Total files in staticfiles: $(find staticfiles -type f | wc -l)"
else
    echo "==> ERROR: staticfiles directory NOT created!"
    echo "Static source files exist: $(test -d static && echo 'YES' || echo 'NO')"
    if [ -d static ]; then
        echo "Source static files:"
        find static -name "*.css" -o -name "*.js" | head -5
    fi
fi

echo "==> Build completed successfully!"
