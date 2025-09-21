#!/bin/bash

# Build script для Render.com deployment
echo "==> Starting build process..."

# Встановлення залежностей
echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Збір статичних файлів переміщено в preDeployCommand
echo "==> Static files will be collected in preDeployCommand"

# Debug info для статичних файлів
echo "==> Debug: Checking static files structure..."
echo "Current directory: $(pwd)"
echo "Static directory exists: $(test -d static && echo 'YES' || echo 'NO')"
echo "Staticfiles directory exists: $(test -d staticfiles && echo 'YES' || echo 'NO')"

if [ -d static ]; then
    echo "Static files:"
    find static -type f -name "*.css" -o -name "*.js" | head -10
fi

echo "==> Build completed successfully!"
