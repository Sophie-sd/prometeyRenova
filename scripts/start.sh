#!/usr/bin/env bash
set -o errexit

echo "🖼️  Ensuring portfolio media files on disk..."
python manage.py seed_portfolio_projects

echo "🚀 Starting application..."
exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker
