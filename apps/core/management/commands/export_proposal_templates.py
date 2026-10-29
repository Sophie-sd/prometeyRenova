"""Копіює шаблони пакетів КП + інструкцію з apps/core/kp_templates у вказану теку."""
import shutil
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.core.proposal_import_admin import KP_TEMPLATES_DIR


class Command(BaseCommand):
    help = 'Експорт шаблонів КП (landing/shop/corporate/corporate_catalog) та INSTRUCTION.md'

    def add_arguments(self, parser):
        parser.add_argument('--out', default='kp_templates_export')

    def handle(self, *args, out, **opts):
        dst = Path(out)
        dst.mkdir(parents=True, exist_ok=True)
        for f in sorted(KP_TEMPLATES_DIR.iterdir()):
            if f.is_file():
                shutil.copy2(f, dst / f.name)
                self.stdout.write(f'→ {dst / f.name}')
