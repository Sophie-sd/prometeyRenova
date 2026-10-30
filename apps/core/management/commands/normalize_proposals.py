"""Спільний канон даних для ВСІХ КП у БД (lead, highlights, 50/50, дубль гарантії в рекомендаціях).

Dry-run за замовчуванням; запис лише з --apply. Ідемпотентно. Клієнтський контент
(напр. apply_copy_corp_budivnytstvo) — окремими командами, не тут.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.proposal_canon import (
    LANGS, is_guarantee_dup_row, normalize_highlight, normalize_payment_text, sanitize_lead,
)
from apps.core.proposal_models import Proposal


class Command(BaseCommand):
    help = 'Нормалізує дані всіх КП за спільним каноном (dry-run; --apply для запису).'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')
        parser.add_argument('--slug', help='лише один КП')

    def handle(self, *args, apply=False, slug=None, **opts):
        qs = Proposal.objects.all().order_by('slug')
        if slug:
            qs = qs.filter(slug=slug)
        total = 0
        with transaction.atomic():
            for p in qs:
                changes = self._normalize(p)
                for c in changes:
                    self.stdout.write(f'{p.slug}: {c}')
                total += len(changes)
            if not apply:
                transaction.set_rollback(True)
        self.stdout.write(f'Змін: {total}. ' + ('Застосовано.' if apply else 'Dry-run. Додайте --apply.'))

    def _normalize(self, p):
        out, dirty = [], []
        for l in LANGS:
            f = f'lead{l}'
            v = getattr(p, f, '') or ''
            if v and sanitize_lead(v) != v:
                setattr(p, f, sanitize_lead(v))
                dirty.append(f)
                out.append(f'{f}: «Кодописн…» → «Написаний з нуля…»')
        if dirty:
            p.save(update_fields=dirty)
        for h in p.highlights.all():
            hd = [f for f in ('title', 'title_ru', 'title_en', 'title_cs')
                  if getattr(h, f, '') and normalize_highlight(getattr(h, f)) != getattr(h, f)]
            for f in hd:
                setattr(h, f, normalize_highlight(getattr(h, f)))
                out.append(f'highlight #{h.pk}.{f}: нормалізовано')
            if hd:
                h.save(update_fields=hd)
        for s in p.specs.filter(kind='payment'):
            sd = [f'{b}{l}' for l in LANGS for b in ('title', 'body')
                  if getattr(s, f'{b}{l}', '') and normalize_payment_text(getattr(s, f'{b}{l}')) != getattr(s, f'{b}{l}')]
            for f in sd:
                setattr(s, f, normalize_payment_text(getattr(s, f)))
                out.append(f'payment #{s.pk}.{f}: → 50/50')
            if sd:
                s.save(update_fields=sd)
        for s in p.specs.filter(kind='recommendation'):
            if is_guarantee_dup_row(s.title, s.body, p.guarantee_html):
                out.append(f'recommendation «{s.title}»: дубль гарантії — DELETE')
                s.delete()
        return out
