"""Спільний guard для seed_proposal_*: не перезаписувати імпортовані та м'яко видалені КП.

Лише читання. Викликається першим рядком handle() кожної seed-команди, до transaction.atomic()
і до _provision_demo — тож для пропущеного slug не виконується ні seed, ні provision.
Файл з префіксом «_» і без класу Command — Django не реєструє його як команду.
"""
from apps.core.proposal_models import Proposal


def seed_must_skip(slug: str) -> str | None:
    """Причина пропуску seed для slug або None (КП немає або воно source=seed і не видалене)."""
    p = Proposal.objects.filter(slug=slug).only('source', 'deleted_at').first()
    if p is None:
        return None
    if p.source != Proposal.Source.SEED:
        return 'source=import'
    if p.deleted_at is not None:
        return 'soft-deleted'
    return None
