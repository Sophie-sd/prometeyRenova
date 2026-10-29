"""Імпорт КП з zip-пакета (Copy-формат: manifest.json + proposal.json + media/).

Етапи: validate (dry-run, без запису) → transaction.atomic (запис).
nh3 — лише тут, на шляху імпорту (seed-и не чіпаємо).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import re
import zipfile
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import PurePosixPath

import nh3
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from .proposal_models import (
    Proposal, ProposalHeroImage, ProposalImport, ProposalModule, ProposalPackage, ProposalSpec,
)
from .proposal_visual_models import ProposalArchNode, ProposalHighlight

MAX_ZIP_BYTES = 20 * 1024 * 1024
MAX_ENTRIES = 50
MAX_RATIO = 100
MAX_UNPACKED = 200 * 1024 * 1024
MAX_IMAGE_BYTES = 3 * 1024 * 1024
MAX_IMAGE_SIDE = 2560
IMAGE_EXT = {'.webp': 'WEBP', '.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG'}

SLUG_RE = re.compile(r'^[a-z0-9](?:[a-z0-9-]{2,62}[a-z0-9])$')
RESERVED_SLUGS = {
    'admin', 'api', 'static', 'media', 'proposal', 'proposals', 'demo', 'demo-site',
    'demo-landing', 'blog', 'payment', 'login', 'logout', 'new', 'import', 'edit', 'delete',
}
PACKAGE_TYPES = {
    'landing': (Proposal.DemoKind.LANDING, False),
    'shop': (Proposal.DemoKind.SHOP, False),
    'corporate': (Proposal.DemoKind.CORPORATE, False),
    'corporate_catalog': (Proposal.DemoKind.CORPORATE, True),
}
LANGS = ('', '_ru', '_en', '_cs')
HTML_FIELDS = {f'{b}{l}' for b in ('intro_html', 'guarantee_html') for l in LANGS}
TEXT_FIELDS = {f'{b}{l}' for b in ('title', 'lead', 'recommendations_lead', 'cta_label') for l in LANGS}
NH3_TAGS = {'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'ul', 'ol', 'li', 'a', 'h3', 'h4', 'blockquote'}
NH3_ATTRS = {'a': {'href', 'title'}}

CHILD_SPECS = {
    'highlights': (ProposalHighlight, ('order', 'title_ru', 'title_en', 'title_cs', 'title')),
    'arch_nodes': (ProposalArchNode, ('order', 'is_accent') + tuple(
        f'{b}{l}' for b in ('title', 'caption') for l in LANGS)),
    'modules': (ProposalModule, ('number', 'order') + tuple(
        f'{b}{l}' for b in ('title', 'description') for l in LANGS)),
    'packages': (ProposalPackage, ('order', 'price', 'price_high', 'currency', 'is_recommended') + tuple(
        f'{b}{l}' for b in ('name', 'scope', 'duration') for l in LANGS)),
    'specs': (ProposalSpec, ('kind', 'order') + tuple(f'{b}{l}' for b in ('title', 'body') for l in LANGS)),
}


class ImportError_(Exception):
    """Помилка валідації пакета (повідомлення українською)."""


@dataclass
class ParsedPackage:
    manifest: dict
    data: dict
    sha256: str
    hero: tuple[str, bytes] | None = None
    log: list = field(default_factory=list)


def clean_html(value: str) -> str:
    return nh3.clean(value or '', tags=NH3_TAGS, attributes=NH3_ATTRS, link_rel='noopener nofollow',
                     url_schemes={'http', 'https', 'mailto', 'tel'})


def clean_text(value) -> str:
    return nh3.clean(str(value or ''), tags=set())


def validate_slug(slug: str) -> str:
    slug = (slug or '').strip()
    if not SLUG_RE.match(slug) or slug in RESERVED_SLUGS:
        raise ImportError_(f'Некоректний або зарезервований slug: «{slug}»')
    return slug


def validate_image(name: str, blob: bytes) -> None:
    from PIL import Image

    ext = PurePosixPath(name).suffix.lower()
    if ext not in IMAGE_EXT:
        raise ImportError_('Фото: дозволені лише webp/jpg/png')
    if len(blob) > MAX_IMAGE_BYTES:
        raise ImportError_('Фото більше 3 МБ')
    try:
        with Image.open(io.BytesIO(blob)) as im:
            fmt, (w, h) = im.format, im.size
            im.verify()
    except Exception as exc:  # noqa: BLE001
        raise ImportError_('Фото пошкоджене або не є зображенням') from exc
    if fmt != IMAGE_EXT[ext]:
        raise ImportError_('Розширення фото не відповідає вмісту')
    if w > MAX_IMAGE_SIDE or h > MAX_IMAGE_SIDE:
        raise ImportError_('Фото більше 2560×2560')


def parse_package(blob: bytes) -> ParsedPackage:
    """Dry-run: повна перевірка без запису в БД/диск."""
    if len(blob) > MAX_ZIP_BYTES:
        raise ImportError_('Zip більше 20 МБ')
    try:
        zf = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile as exc:
        raise ImportError_('Файл не є zip-архівом') from exc
    infos = zf.infolist()
    if len(infos) > MAX_ENTRIES:
        raise ImportError_('У zip більше 50 файлів')
    total = 0
    names = {}
    for info in infos:
        name = info.filename
        p = PurePosixPath(name)
        if name.startswith('/') or '..' in p.parts or '\\' in name or (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise ImportError_(f'Недопустимий шлях у zip: {name}')
        if info.flag_bits & 0x1:
            raise ImportError_('Зашифровані zip не підтримуються')
        total += info.file_size
        if info.compress_size and info.file_size / info.compress_size > MAX_RATIO:
            raise ImportError_('Підозріле стиснення (zip-бомба)')
        if not info.is_dir():
            names[name] = info
    if total > MAX_UNPACKED:
        raise ImportError_('Розпакований вміст більше 200 МБ')
    for required in ('manifest.json', 'proposal.json'):
        if required not in names:
            raise ImportError_(f'Немає {required}')
    try:
        manifest = json.loads(zf.read('manifest.json').decode('utf-8'))
        data = json.loads(zf.read('proposal.json').decode('utf-8'))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ImportError_('Некоректний JSON у пакеті') from exc
    if not isinstance(manifest, dict) or not isinstance(data, dict):
        raise ImportError_('manifest.json / proposal.json мають бути обʼєктами')
    if manifest.get('version') != 1 or manifest.get('type') not in PACKAGE_TYPES:
        raise ImportError_('manifest: потрібні version=1 і type ∈ landing/shop/corporate/corporate_catalog')
    kind, catalog = PACKAGE_TYPES[manifest['type']]
    if data.get('kind') and data['kind'] != kind:
        raise ImportError_('kind у proposal.json не відповідає type у manifest')
    data['kind'], data['corp_catalog'] = kind, catalog
    data['slug'] = validate_slug(data.get('slug'))
    if not (data.get('client_name') or '').strip() or not (data.get('title') or '').strip():
        raise ImportError_('Порожні client_name або title')
    try:
        data['issued_on'] = dt.date.fromisoformat(str(data.get('issued_on')))
    except ValueError as exc:
        raise ImportError_('issued_on має бути YYYY-MM-DD') from exc
    for key, (model, fields) in CHILD_SPECS.items():
        rows = data.get(key) or []
        if not isinstance(rows, list):
            raise ImportError_(f'{key} має бути списком')
        for row in rows:
            if not isinstance(row, dict):
                raise ImportError_(f'{key}: елемент має бути обʼєктом')
            if key == 'packages':
                for pf in ('price', 'price_high'):
                    if row.get(pf) not in (None, ''):
                        try:
                            row[pf] = Decimal(str(row[pf]))
                        except InvalidOperation as exc:
                            raise ImportError_(f'packages.{pf}: не число') from exc
                    else:
                        row[pf] = None if pf == 'price_high' else Decimal('0')
            if key == 'specs' and row.get('kind') not in ProposalSpec.Kind.values:
                raise ImportError_('specs.kind: spec/payment/recommendation')
    hero = None
    hero_ref = (data.get('hero_image') or '').strip()
    if hero_ref:
        if not hero_ref.startswith('media/') or hero_ref not in names:
            raise ImportError_(f'hero_image не знайдено в media/: {hero_ref}')
        blob_img = zf.read(hero_ref)
        validate_image(hero_ref, blob_img)
        hero = (hero_ref, blob_img)
    for name in names:
        if name.startswith('media/') and name != hero_ref:
            validate_image(name, zf.read(name))
    return ParsedPackage(manifest=manifest, data=data, sha256=hashlib.sha256(blob).hexdigest(), hero=hero)


def serialize_proposal(p: Proposal) -> dict:
    """Знімок КП у форматі proposal.json (для snapshot_before / export / rollback)."""
    out = {f: getattr(p, f) for f in (HTML_FIELDS | TEXT_FIELDS)}
    out.update(slug=p.slug, client_name=p.client_name, issued_on=p.issued_on.isoformat() if p.issued_on else None,
               kind=p.kind, corp_catalog=p.corp_catalog, is_published=p.is_published, order=p.order,
               pair_slug=p.pair_slug)
    hero = p.hero_images.filter(is_active=True).order_by('order', 'pk').first()
    out['hero_image'] = hero.image.name if hero else ''
    for key, (model, fields) in CHILD_SPECS.items():
        rel = getattr(p, key).all().order_by('order', 'pk')
        out[key] = [{f: (str(getattr(r, f)) if isinstance(getattr(r, f), Decimal) else getattr(r, f))
                     for f in fields} for r in rel]
    return out


def _apply(p: Proposal, data: dict, hero_import: tuple[str, bytes] | None, keep_hero_name: str | None = None):
    for f in HTML_FIELDS:
        if f in data:
            setattr(p, f, clean_html(data[f]))
    for f in TEXT_FIELDS:
        if f in data:
            setattr(p, f, clean_text(data[f]))
    p.client_name = clean_text(data['client_name'])
    p.issued_on = data['issued_on'] if isinstance(data['issued_on'], dt.date) else dt.date.fromisoformat(data['issued_on'])
    p.kind, p.corp_catalog = data['kind'], bool(data.get('corp_catalog'))
    p.is_published = bool(data.get('is_published'))
    p.order = int(data.get('order') or 0)
    p.source = Proposal.Source.IMPORT
    p.save()
    for key, (model, fields) in CHILD_SPECS.items():
        getattr(p, key).all().delete()
        for row in data.get(key) or []:
            kwargs = {}
            for f in fields:
                if f not in row:
                    continue
                v = row[f]
                if f in ('order', 'number'):
                    v = int(v or 0)
                elif f == 'is_accent' or f == 'is_recommended':
                    v = bool(v)
                elif f in ('price', 'price_high'):
                    v = None if v in (None, '') else Decimal(str(v))
                elif f.startswith(('body', 'description', 'scope')):
                    v = clean_html(v)
                else:
                    v = clean_text(v)
                kwargs[f] = v
            model.objects.create(proposal=p, **kwargs)
    if hero_import:
        name, blob = hero_import
        p.hero_images.update(is_active=False)
        next_order = (p.hero_images.aggregate(m=Max('order'))['m'] or 0) + 1 if p.hero_images.exists() else 0
        img = ProposalHeroImage(proposal=p, order=next_order, original_name=PurePosixPath(name).name[:255])
        img.image.save(PurePosixPath(name).name, ContentFile(blob), save=False)
        img.save()
    elif keep_hero_name is not None:
        p.hero_images.update(is_active=False)
        if keep_hero_name:
            p.hero_images.filter(image=keep_hero_name).update(is_active=True)


def _next_version(proposal: Proposal | None) -> int:
    if not proposal:
        return 1
    return (proposal.imports.aggregate(m=Max('version'))['m'] or 0) + 1


def import_proposal_package(blob: bytes, *, user=None, original_name: str = '', dry_run: bool = False) -> ProposalImport | ParsedPackage:
    parsed = parse_package(blob)
    if ProposalImport.objects.filter(sha256=parsed.sha256).exists():
        raise ImportError_('Цей пакет уже імпортовано (той самий SHA-256)')
    existing = Proposal.objects.filter(slug=parsed.data['slug']).first()
    if existing and existing.source != Proposal.Source.IMPORT:
        raise ImportError_('КП з таким slug створено не імпортом (seed/ручне) — перезапис заборонено')
    if dry_run:
        return parsed
    with transaction.atomic():
        snapshot = serialize_proposal(existing) if existing else None
        proposal = existing or Proposal(slug=parsed.data['slug'])
        _apply(proposal, parsed.data, parsed.hero)
        rec = ProposalImport(
            proposal=proposal, kind=ProposalImport.Kind.UPLOAD, version=_next_version(existing),
            original_name=original_name[:255], sha256=parsed.sha256, manifest=parsed.manifest,
            status=ProposalImport.Status.SUCCESS, snapshot_before=snapshot, user=user,
            log=[f'{"оновлено" if existing else "створено"} КП {proposal.slug}'], finished_at=timezone.now(),
        )
        rec.file.save(f'{parsed.sha256[:16]}.zip', ContentFile(blob), save=False)
        rec.save()
    return rec


def rollback_import(target: ProposalImport, *, user=None) -> ProposalImport:
    """Відкат = новий ProposalImport(kind=rollback, version+1), КП ← target.snapshot_before."""
    proposal = target.proposal
    if not proposal or not target.snapshot_before:
        raise ImportError_('Немає знімка «до» — відкат неможливий (перша версія: використайте soft-delete)')
    with transaction.atomic():
        current = serialize_proposal(proposal)
        snap = dict(target.snapshot_before)
        _apply(proposal, snap, None, keep_hero_name=snap.get('hero_image') or '')
        return ProposalImport.objects.create(
            proposal=proposal, kind=ProposalImport.Kind.ROLLBACK, version=_next_version(proposal),
            rollback_of=target, status=ProposalImport.Status.SUCCESS, snapshot_before=current, user=user,
            log=[f'відкат до стану перед v{target.version}'], finished_at=timezone.now(),
        )


def soft_delete_proposal(proposal: Proposal, *, user=None) -> None:
    with transaction.atomic():
        proposal.deleted_at = timezone.now()
        proposal.deleted_by = user
        proposal.is_published = False
        proposal.save(update_fields=['deleted_at', 'deleted_by', 'is_published', 'updated_at'])
        if proposal.source == Proposal.Source.IMPORT:  # стандартне демо (seed) не чіпаємо
            tenant = proposal.demo_tenant
            if tenant is not None and hasattr(tenant, 'is_active'):
                tenant.is_active = False
                tenant.save(update_fields=['is_active'])


def restore_proposal(proposal: Proposal) -> None:
    with transaction.atomic():
        proposal.deleted_at = None
        proposal.deleted_by = None
        proposal.save(update_fields=['deleted_at', 'deleted_by', 'updated_at'])
        if proposal.source == Proposal.Source.IMPORT:
            tenant = proposal.demo_tenant
            if tenant is not None and hasattr(tenant, 'is_active'):
                tenant.is_active = True
                tenant.save(update_fields=['is_active'])


def can_import(user) -> bool:
    return bool(user and user.is_active and (user.is_superuser or (user.is_staff and user.has_perm('core.can_import_proposal'))))
