"""Остаточне видалення КП. Лише soft-deleted, лише з --confirm (залізне правило Олега)."""
from django.core.management.base import BaseCommand, CommandError

from apps.core.proposal_models import Proposal


class Command(BaseCommand):
    help = 'purge_proposal --slug X --confirm (тільки мʼяко видалені КП)'

    def add_arguments(self, parser):
        parser.add_argument('--slug', required=True)
        parser.add_argument('--confirm', action='store_true')

    def handle(self, *args, slug, confirm, **opts):
        p = Proposal.objects.filter(slug=slug).first()
        if not p:
            raise CommandError(f'КП {slug} не знайдено')
        if p.deleted_at is None:
            raise CommandError('КП не мʼяко видалене — спершу soft-delete в адмінці')
        if not confirm:
            self.stdout.write(f'Dry-run: буде видалено КП {slug} (імпортів: {p.imports.count()}). Додайте --confirm.')
            return
        p.delete()
        self.stdout.write(self.style.SUCCESS(f'КП {slug} видалено остаточно'))
