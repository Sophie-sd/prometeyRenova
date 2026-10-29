"""Експорт КП у zip-пакет (той самий формат, що й імпорт)."""
import datetime as dt
import json
import zipfile
from pathlib import Path, PurePosixPath

from django.core.management.base import BaseCommand, CommandError

from apps.core.proposal_import import serialize_proposal
from apps.core.proposal_models import Proposal


class Command(BaseCommand):
    help = 'export_proposal_package <slug> [--out file.zip]'

    def add_arguments(self, parser):
        parser.add_argument('slug')
        parser.add_argument('--out')

    def handle(self, *args, slug, out=None, **opts):
        p = Proposal.objects.filter(slug=slug).first()
        if not p:
            raise CommandError(f'КП {slug} не знайдено')
        data = serialize_proposal(p)
        data.pop('pair_slug', None)
        ptype = 'corporate_catalog' if p.corp_catalog else p.kind
        hero = p.hero_images.filter(is_active=True).order_by('order', 'pk').first()
        out = Path(out or f'{slug}.zip')
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
            if hero:
                arc = f'media/hero{PurePosixPath(hero.image.name).suffix.lower()}'
                with hero.image.open('rb') as fh:
                    z.writestr(arc, fh.read())
                data['hero_image'] = arc
            else:
                data['hero_image'] = ''
            z.writestr('manifest.json', json.dumps({'type': ptype, 'version': 1, 'title': p.title,
                                                    'created': dt.date.today().isoformat()}, ensure_ascii=False, indent=2))
            z.writestr('proposal.json', json.dumps(data, ensure_ascii=False, indent=2, default=str))
        self.stdout.write(self.style.SUCCESS(f'→ {out}'))
