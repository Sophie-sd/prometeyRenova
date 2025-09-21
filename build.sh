#!/bin/bash

# Build script для Render.com deployment
echo "==> Starting build process..."

# Встановлення залежностей
echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Збір статичних файлів  
echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Build completed successfully!"
