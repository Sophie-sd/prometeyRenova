#!/usr/bin/env bash
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🌍 Compiling translations (uk, ru, en, cs)..."
python manage.py compilemessages --locale=en --locale=ru --locale=uk --locale=cs --ignore=prometey_env

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

# Бандл CSS, ексклюзивних для головної сторінки, в 1 файл — 10 блокуючих
# <link> замінюються 1 (home.html вантажить бандл лише коли DEBUG=False,
# див. templates/pages/home.html). Порядок КРИТИЧНИЙ — має 1:1 збігатися
# з порядком <link> у {% block page_css %} home.html (каскад залежить
# від порядку: -final/-bridge/-why-cards свідомо йдуть після -v2/-v3).
home_bundle_files = [
    'staticfiles/css/home-redesign/home-redesign-v2.css',
    'staticfiles/css/home-redesign/home-redesign-v3.css',
    'staticfiles/css/home-redesign/home-redesign-final.css',
    'staticfiles/css/home-redesign/home-redesign-bridge.css',
    'staticfiles/css/home-redesign/home-why-cards.css',
    'staticfiles/css/process_block.css',
    'staticfiles/css/services_piano_block.css',
    'staticfiles/css/services_piano_block_mob.css',
    'staticfiles/css/services_piano_video.css',
    'staticfiles/css/home-motion.css',
]
bundle_parts = []
for fp in home_bundle_files:
    p = pathlib.Path(fp)
    if not p.exists():
        print(f'WARNING: {fp} відсутній — home-page-bundle.css буде НЕПОВНИМ!')
        sys.exit(1)
    minified = rcssmin.cssmin(p.read_text(encoding='utf-8'))
    bundle_parts.append(f'/*{p.name}*/' + minified)
bundle_path = pathlib.Path('staticfiles/css/home-page-bundle.css')
bundle_path.write_text(''.join(bundle_parts), encoding='utf-8')
print(f'Home CSS bundle: {bundle_path.stat().st_size/1024:.1f} KiB ({len(bundle_parts)} файлів -> 1)')
"

echo "🗄️  Running migrations..."
python manage.py migrate

echo "👤 Creating superuser..."
python manage.py create_superuser

echo "🔐 Granting staff admin access..."
python manage.py grant_staff_admin_access

echo "🌱 Seeding initial data (blog posts & events)..."
python manage.py seed_initial_data

echo "🖼️  Seeding portfolio projects (from static assets)..."
python manage.py seed_portfolio_projects --prune --force-images

echo "👥 Seeding homepage clients (from static assets)..."
python manage.py seed_clients

echo "📄 Seeding B2B Parts commercial proposal..."
python manage.py seed_proposal_b2b_parts

echo "✅ Build complete!"