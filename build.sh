#!/usr/bin/env bash
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🌍 Compiling translations (uk, ru, en)..."
python manage.py compilemessages --locale=en --locale=ru --locale=uk --ignore=prometey_env

echo "📁 Collecting static files (з автоматичною compression)..."
python manage.py collectstatic --no-input

echo "🗜️  Minifying CSS and JS..."
python3 -c "
import rcssmin, rjsmin, pathlib, sys

css_saved = 0
js_saved = 0

for f in pathlib.Path('staticfiles/css').glob('*.css'):
    original = f.read_text(encoding='utf-8')
    minified = rcssmin.cssmin(original)
    saved = len(original) - len(minified)
    if saved > 0:
        f.write_text(minified, encoding='utf-8')
        css_saved += saved

js_globs = list(pathlib.Path('staticfiles/js').glob('*.js'))
js_globs += list(pathlib.Path('staticfiles/js/core').glob('*.js'))
for f in js_globs:
    original = f.read_text(encoding='utf-8')
    minified = rjsmin.jsmin(original)
    saved = len(original) - len(minified)
    if saved > 0:
        f.write_text(minified, encoding='utf-8')
        js_saved += saved

print(f'CSS saved: {css_saved/1024:.1f} KiB, JS saved: {js_saved/1024:.1f} KiB')
"

echo "🗄️  Running migrations..."
python manage.py migrate

echo "👤 Creating superuser..."
python manage.py create_superuser

echo "🌱 Seeding initial data (blog posts & events)..."
python manage.py seed_initial_data

echo "✅ Build complete!"