"""Спільний код для пари КП «Квіти» (kp-kvity/2026-10-29-001): лендинг і інтернет-магазин окремо."""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import transaction

from apps.core.i18n_content import translate_ua_to_ru
from apps.core.legacy_schema import create_with_leftovers, ensure_leftover_not_null_defaults
from apps.core.proposal_models import Proposal, ProposalModule, ProposalPackage, ProposalSpec
from apps.core.proposal_visual_models import ProposalArchNode, ProposalHighlight

# Канон гарантії: пожиттєва гарантія на код + 1 рік безкоштовної підтримки.
GUARANTEE_HTML = """
<p>Ми впевнені в якості нашого коду. Сайт пишеться з нуля без сторонніх модулів і вразливих CMS-шаблонів, тому не потребує щомісячних оновлень, які часто ламають звичайні сайти.</p>
<p>Ми надаємо <strong>пожиттєву гарантію на код</strong>: технічні баги з нашої вини виправляємо безкоштовно без обмеження строку. Плюс <strong>1 рік безкоштовної підтримки</strong>: якщо щось зламалося, дрібні правки, консультації.</p>
""".strip()


def with_ru(payload: dict, text_keys: tuple) -> dict:
    out = dict(payload)
    for key in text_keys:
        out.setdefault(f'{key}_ru', translate_ua_to_ru(out.get(key, '')))
        for lang in ('en', 'cs'):
            out.setdefault(f'{key}_{lang}', '')
    return out


def attach_hero(proposal: Proposal) -> None:
    src = Path(settings.BASE_DIR) / 'static' / 'proposal' / 'img' / 'seal-on-dark.webp'
    if not src.is_file():
        return
    if proposal.hero_image:
        proposal.hero_image.delete(save=False)
    with src.open('rb') as handle:
        proposal.hero_image.save(src.name, File(handle), save=True)


def seed_rows(cfg) -> tuple:
    """cfg — модуль seed-команди з константами SLUG, TITLE, … (ідемпотентно, лише ця КП)."""
    for model in (Proposal, ProposalModule, ProposalPackage, ProposalSpec,
                  ProposalHighlight, ProposalArchNode):
        ensure_leftover_not_null_defaults(model)
    with transaction.atomic():
        proposal, created = Proposal.objects.update_or_create(
            slug=cfg.SLUG,
            defaults={
                'client_name': cfg.CLIENT,
                'title': cfg.TITLE, 'title_ru': translate_ua_to_ru(cfg.TITLE),
                'title_en': '', 'title_cs': '',
                'lead': cfg.LEAD, 'lead_ru': translate_ua_to_ru(cfg.LEAD),
                'lead_en': '', 'lead_cs': '',
                'recommendations_lead': cfg.RECS_LEAD,
                'recommendations_lead_ru': translate_ua_to_ru(cfg.RECS_LEAD),
                'recommendations_lead_en': '', 'recommendations_lead_cs': '',
                'issued_on': cfg.ISSUED_ON,
                'intro_html': cfg.INTRO_HTML, 'intro_html_ru': translate_ua_to_ru(cfg.INTRO_HTML),
                'intro_html_en': '', 'intro_html_cs': '',
                'guarantee_html': GUARANTEE_HTML,
                'guarantee_html_ru': translate_ua_to_ru(GUARANTEE_HTML),
                'guarantee_html_en': '', 'guarantee_html_cs': '',
                'cta_label': 'Обговорити проєкт', 'cta_label_ru': 'Обсудить проект',
                'cta_label_en': '', 'cta_label_cs': '',
                'kind': cfg.KIND,
                'corp_catalog': False,
                'is_published': True,
                'order': cfg.ORDER,
            },
        )
        proposal.modules.all().delete()
        for data in cfg.MODULES:
            create_with_leftovers(ProposalModule, proposal=proposal,
                                  **with_ru(data, ('title', 'description')))
        proposal.packages.all().delete()
        for data in cfg.PACKAGES:
            create_with_leftovers(ProposalPackage, proposal=proposal,
                                  **with_ru(data, ('name', 'scope', 'duration')))
        proposal.specs.all().delete()
        for data in cfg.SPECS:
            create_with_leftovers(ProposalSpec, proposal=proposal, **with_ru(data, ('title', 'body')))
        proposal.highlights.all().delete()
        for data in cfg.HIGHLIGHTS:
            create_with_leftovers(ProposalHighlight, proposal=proposal, **with_ru(data, ('title',)))
        proposal.arch_nodes.all().delete()
        for data in cfg.ARCH_NODES:
            create_with_leftovers(ProposalArchNode, proposal=proposal,
                                  **with_ru(data, ('title', 'caption')))
        attach_hero(proposal)
    return proposal, created
