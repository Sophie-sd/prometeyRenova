#!/usr/bin/env bash
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🌍 Compiling translations..."
python manage.py compilemessages --ignore=prometey_env

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️  Running migrations..."
python manage.py migrate

echo "👤 Creating superuser..."
python manage.py create_superuser

echo "🌱 Seeding initial data (blog posts & events)..."
python manage.py seed_initial_data

echo "✅ Build complete!"