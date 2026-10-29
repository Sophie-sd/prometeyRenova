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

echo "🔐 Granting staff admin access..."
python manage.py grant_staff_admin_access

echo "🌱 Seeding initial data (blog posts & events)..."
python manage.py seed_initial_data

echo "🖼️  Seeding portfolio projects (from static assets)..."
python manage.py seed_portfolio_projects

echo "👥 Seeding homepage clients (from static assets)..."
python manage.py seed_clients

echo "📄 Seeding B2B Parts commercial proposal..."
python manage.py seed_proposal_b2b_parts

echo "📄 Seeding Liber corporate proposal + classic demo-corp..."
python manage.py seed_proposal_corporate

echo "📄 Seeding glass-factory proposal + classic demo-shop..."
python manage.py seed_proposal_glass

echo "📄 Seeding mangal e-commerce proposal + classic demo-shop..."
python manage.py seed_proposal_mangaly

echo "📄 Seeding garden e-commerce proposal + classic demo-shop..."
python manage.py seed_proposal_garden

echo "📄 Seeding generic e-commerce proposal + classic demo-shop..."
python manage.py seed_proposal_ecom

echo "📄 Seeding second shop proposal (950/1500/3500) + classic demo-shop..."
python manage.py seed_proposal_ecom_b

echo "📄 Seeding agro Prom.ua migration proposal + classic demo-shop..."
python manage.py seed_proposal_agro_prom

echo "📄 Seeding sanitary corporate proposal + classic demo-corp..."
python manage.py seed_proposal_sanitary

echo "📄 Seeding advocate landing proposal + classic demo-landing..."
python manage.py seed_proposal_advocate

echo "📄 Seeding locks shop proposal + classic demo-shop..."
python manage.py seed_proposal_locks

echo "📄 Seeding 4-ISP portal proposal + classic demo-shop..."
python manage.py seed_proposal_4isp

echo "📄 Seeding classic retail shop proposal + classic demo-shop..."
python manage.py seed_proposal_classic

echo "📄 Seeding lingerie shop proposal + classic demo-shop..."
python manage.py seed_proposal_lingerie

echo "📄 Seeding corporate catalog proposal (no demo)..."
python manage.py seed_proposal_catalog

echo "📄 Seeding plants shop proposal + classic demo-shop..."
python manage.py seed_proposal_plants

echo "📄 Seeding outerwear shop proposal + classic demo-shop..."
python manage.py seed_proposal_outerwear

echo "📄 Seeding tools shop proposal + classic demo-shop..."
python manage.py seed_proposal_tools

echo "📄 Seeding autoparts shop proposal + classic demo-shop..."
python manage.py seed_proposal_autoparts

echo "📄 Seeding Sanvit corporate catalog proposal + classic demo-corp..."
python manage.py seed_proposal_sanvit

echo "📄 Seeding print catalog proposal + classic demo-shop..."
python manage.py seed_proposal_print

echo "📄 Seeding concrete corporate proposal + classic demo-corp..."
python manage.py seed_proposal_concrete

echo "📄 Seeding catalog-b corporate proposal + classic demo-corp..."
python manage.py seed_proposal_catalog_b

echo "📄 Seeding DEVISU corporate proposal + classic demo-corp..."
python manage.py seed_proposal_devisu

echo "📄 Seeding jewelry shop proposal + classic demo-shop..."
python manage.py seed_proposal_jewelry

echo "📄 Seeding metal furniture proposal + standard demo-shop..."
python manage.py seed_proposal_metal_furniture

echo "📄 Seeding furniture shop proposal + standard demo-shop..."
python manage.py seed_proposal_furniture_shop

echo "📄 Seeding Ascania FMCG corporate proposal + classic demo-corp..."
python manage.py seed_proposal_ascania

echo "📄 Seeding Kovrik.ua corporate proposal + classic demo-corp..."
python manage.py seed_proposal_kovrik

echo "📄 Seeding 18+ shop proposal + standard demo-shop..."
python manage.py seed_proposal_intim_shop

echo "📄 Seeding 3DS corporate proposal + classic demo-corp..."
python manage.py seed_proposal_3ds

echo "📄 Seeding cosmetics shop proposal + standard demo-shop..."
python manage.py seed_proposal_cosmetics_shop

echo "📄 Seeding Farmlyga corporate proposal + classic demo-corp..."
python manage.py seed_proposal_farmlyga

echo "📄 Seeding medical center corporate proposal + classic demo-corp..."
python manage.py seed_proposal_medcenter

echo "📄 Seeding agro & logistics corporate proposal + classic demo-corp..."
python manage.py seed_proposal_agro_logistics

echo "📄 Seeding Landing Page proposal (300 €) + standard demo-landing..."
python manage.py seed_proposal_landing_page

echo "📄 Seeding autoservice landing proposal (250 €) + standard demo-landing..."
python manage.py seed_proposal_autoservice

echo "📄 Seeding construction corporate proposal (650 €) + classic demo-corp..."
python manage.py seed_proposal_construction

echo "📄 Seeding plumber landing proposal (200 €) + standard demo-landing..."
python manage.py seed_proposal_plumber

echo "📄 Seeding hangar corporate proposal (450–500 €) + classic demo-corp..."
python manage.py seed_proposal_angary

echo "📄 Seeding bakinskybulvar.com corporate catalog proposal (800 €) + standard demo-shop..."
python manage.py seed_proposal_bakinskybulvar

echo "📄 Seeding pet-supplies e-shop proposal (800–900 €) + standard demo-shop..."
python manage.py seed_proposal_zootovary

echo "📄 Seeding turnkey corporate site proposal (BASE 900 € / PREMIUM 1 600 € / PLATINUM 3 500 €) + classic demo-corp..."
python manage.py seed_proposal_corporate_turnkey

echo "📄 Seeding shoes & clothing e-shop proposal (950 € / ads 300 € / combo 1 250 €) + standard demo-shop..."
python manage.py seed_proposal_vzuttia_odiah

echo "📄 Seeding profremservice.com.ua corporate catalog proposal (700 – 720 €) + standard demo-corp..."
python manage.py seed_proposal_profremservice

echo "📄 Seeding photographer portfolio + services catalog corporate proposal (650 €) + standard demo-corp..."
python manage.py seed_proposal_fotograf

echo "📄 Seeding auto goods e-shop proposal (800 €) + standard demo-shop..."
python manage.py seed_proposal_avtotovary

echo "📄 Seeding auto goods e-shop + Prom.ua migration proposal (920 €) + standard demo-shop..."
python manage.py seed_proposal_avtotovary_prom

echo "📄 Seeding fishing goods e-shop proposal (950 €) + standard demo-shop..."
python manage.py seed_proposal_rybalka

echo "📄 Seeding flowers LANDING proposal (250 €) + standard demo-landing..."
python manage.py seed_proposal_kvity_landing

echo "📄 Seeding flowers E-SHOP proposal (1 200 €) + standard demo-shop..."
python manage.py seed_proposal_kvity_shop

echo "✅ Build complete!"