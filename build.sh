#!/bin/bash

# Build script для Render.com deployment
echo "==> Starting build process..."

# Встановлення залежностей
echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Збір статичних файлів переміщено в preDeployCommand
echo "==> Static files will be collected in preDeployCommand"

echo "==> Build completed successfully!"
