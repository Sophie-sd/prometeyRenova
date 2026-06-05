#!/usr/bin/env bash
set -o errexit

echo "🖼️  Ensuring portfolio media files on disk..."
python manage.py seed_portfolio_projects

echo "👥 Ensuring homepage client logos on disk..."
python manage.py seed_clients

echo "🚀 Starting application..."
exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker
