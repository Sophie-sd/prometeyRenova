"""Генерація PDF «Рахунок на оплату» через xhtml2pdf."""
from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from .amount_ua import amount_in_words_ua, format_money_ua


def _static_path(relative: str) -> Optional[Path]:
    found = find(relative)
    if found:
        return Path(found).resolve()
    fallback = Path(settings.BASE_DIR) / 'static' / relative
    if fallback.exists():
        return fallback.resolve()
    return None


def _logo_file_uri() -> str:
    path = _static_path('images/favicon-48x48.png')
    return path.as_uri() if path else ''


def _font_paths() -> Dict[str, str]:
    regular = _static_path('fonts/NotoSans-Regular.ttf')
    bold = _static_path('fonts/NotoSans-Bold.ttf')
    return {
        'regular': str(regular) if regular else '',
        'bold': str(bold) if bold else '',
    }


def _short_recipient_name(full_name: str) -> str:
    """ФОП Дмитренко Сергій Дмитрович → ФОП Дмитренко С.Д."""
    name = (full_name or '').strip()
    if not name:
        return ''
    parts = name.split()
    prefix = ''
    if parts and parts[0].upper() in {'ФОП', 'ТОВ', 'ПП', 'АТ', 'ПРАТ', 'ТДВ'}:
        prefix = parts[0]
        parts = parts[1:]
    if len(parts) >= 3:
        short = f'{parts[0]} {parts[1][0]}.{parts[2][0]}.'
    elif len(parts) == 2:
        short = f'{parts[0]} {parts[1][0]}.'
    elif parts:
        short = parts[0]
    else:
        short = name
    return f'{prefix} {short}'.strip() if prefix else short


def _client_slug_for_filename(client_name: str) -> str:
    name = (client_name or '').strip()
    tokens = re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ'’-]+", name)
    skip = {'ФОП', 'ТОВ', 'ПП', 'АТ', 'ПРАТ', 'ТДВ', 'ФІЗИЧНА', 'ОСОБА'}
    meaningful = [t for t in tokens if t.upper() not in skip]
    if not meaningful:
        return 'клієнт'
    return meaningful[0]


def build_pdf_filename(invoice) -> str:
    date_s = invoice.invoice_date.strftime('%d.%m.%Y')
    slug = _client_slug_for_filename(invoice.client_name)
    return f'Рахунок_{invoice.number}_{slug}_{date_s}.pdf'


def invoice_context(invoice) -> dict:
    items = []
    for item in invoice.items.all():
        items.append({
            'position': item.position,
            'title': item.title,
            'unit': item.unit,
            'quantity': item.quantity,
            'price_formatted': format_money_ua(item.price),
            'amount_formatted': format_money_ua(item.amount),
        })
    fonts = _font_paths()
    return {
        'invoice': invoice,
        'items': items,
        'logo_uri': _logo_file_uri(),
        'font_regular': fonts['regular'],
        'font_bold': fonts['bold'],
        'invoice_date': invoice.invoice_date.strftime('%d.%m.%Y'),
        'valid_until': invoice.valid_until.strftime('%d.%m.%Y'),
        'contract_date': invoice.contract_date.strftime('%d.%m.%Y'),
        'total_formatted': format_money_ua(invoice.total_amount),
        'total_words': amount_in_words_ua(invoice.total_amount),
        'recipient_name': invoice.recipient_name_snapshot,
        'recipient_ipn': invoice.recipient_ipn_snapshot,
        'recipient_iban': invoice.recipient_iban_snapshot,
        'recipient_bank': invoice.recipient_bank_snapshot,
        'recipient_mfo': invoice.recipient_mfo_snapshot,
        'recipient_bank_edrpou': invoice.recipient_bank_edrpou_snapshot,
        'sign_name': _short_recipient_name(invoice.recipient_name_snapshot),
    }


def render_invoice_html(invoice) -> str:
    return render_to_string('payment/invoice_pdf.html', invoice_context(invoice))


def _link_callback(uri, rel):
    """Дозволяє xhtml2pdf читати локальні file:// та static paths."""
    if uri.startswith('file://'):
        return uri.replace('file://', '')
    if uri.startswith('/'):
        return uri
    static_candidate = Path(settings.BASE_DIR) / 'static' / uri
    if static_candidate.exists():
        return str(static_candidate)
    found = find(uri)
    if found:
        return found
    return uri


def generate_invoice_pdf_bytes(invoice) -> bytes:
    from xhtml2pdf import pisa

    html = render_invoice_html(invoice)
    result = io.BytesIO()
    pdf = pisa.CreatePDF(
        src=io.BytesIO(html.encode('utf-8')),
        dest=result,
        encoding='utf-8',
        link_callback=_link_callback,
    )
    if pdf.err:
        raise RuntimeError(f'PDF generation failed with {pdf.err} error(s)')
    return result.getvalue()


def get_or_create_invoice_pdf(invoice) -> Tuple[bytes, str]:
    filename = build_pdf_filename(invoice)
    if invoice.pdf_file:
        invoice.pdf_file.open('rb')
        try:
            data = invoice.pdf_file.read()
        finally:
            invoice.pdf_file.close()
        if data:
            return data, filename

    data = generate_invoice_pdf_bytes(invoice)
    invoice.pdf_file.save(filename, ContentFile(data), save=True)
    return data, filename
