"""Спільний канон даних КП (усі КП): lead, highlights, 50/50, дубль гарантії."""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_canon import (
    normalize_highlight, normalize_payment_text, normalize_proposal_data, sanitize_lead,
)
from apps.core.proposal_import import import_proposal_package
from apps.core.proposal_models import Proposal, ProposalSpec
from apps.core.proposal_presenters import pay_figure
from apps.core.proposal_visual_models import ProposalHighlight
from apps.core.tests.test_proposal_import import make_zip

GUA = '<p>Гарантія: довічна гарантія на код + 1 рік підтримки.</p>'


class CanonUnitTests(TestCase):
    def test_lead_sanitize_ua_ru(self):
        self.assertEqual(sanitize_lead('Кодописний корпоративний сайт'), 'Написаний з нуля корпоративний сайт')
        self.assertEqual(sanitize_lead('Кодописна система'), 'Написана з нуля система')
        self.assertEqual(sanitize_lead('Кодописный сайт'), 'Написанный с нуля сайт')
        self.assertEqual(sanitize_lead('Сайт на чистому коді'), 'Сайт на чистому коді')

    def test_highlight_pattern(self):
        self.assertEqual(normalize_highlight('  Enterprise-безпека і масштаб. '), 'Корпоративна безпека і масштаб')
        self.assertEqual(normalize_highlight('Enterprise-безопасность и масштаб'), 'Корпоративная безопасность и масштаб')

    def test_payment_fifty_variants_feed_presenter(self):
        for raw in ('50 / 50', '50%/50%', '50 на 50', '50% + 50%'):
            norm = normalize_payment_text(f'Оплата {raw}')
            self.assertIn('50/50', norm, raw)
            self.assertEqual(pay_figure(norm, ''), '50/50')
        self.assertEqual(normalize_payment_text('Передоплата 30%'), 'Передоплата 30%')

    def test_data_drops_guarantee_dup_keeps_others(self):
        data = {'lead': 'Кодописний сайт', 'guarantee_html': GUA,
                'highlights': [{'title': 'Enterprise-безпека і масштаб'}],
                'specs': [{'kind': 'recommendation', 'title': 'Гарантія', 'body': 'довічна гарантія на код'},
                          {'kind': 'recommendation', 'title': 'Географія робіт', 'body': 'Карта об’єктів'},
                          {'kind': 'payment', 'title': 'Оплата 50 на 50', 'body': ''}]}
        log = normalize_proposal_data(data)
        self.assertEqual(data['lead'], 'Написаний з нуля сайт')
        self.assertEqual(data['highlights'][0]['title'], 'Корпоративна безпека і масштаб')
        self.assertEqual([s['title'] for s in data['specs']], ['Географія робіт', 'Оплата 50/50'])
        self.assertTrue(log)
        self.assertEqual(normalize_proposal_data(data), [])  # ідемпотентно


class CanonImportAndCommandTests(TestCase):
    def test_import_applies_shared_canon(self):
        blob = make_zip({'lead': 'Кодописний лендінг', 'guarantee_html': GUA,
                         'highlights': [{'order': 0, 'title': 'Enterprise-безпека'}],
                         'specs': [{'kind': 'recommendation', 'order': 0, 'title': 'Гарантія', 'body': 'x'},
                                   {'kind': 'payment', 'order': 1, 'title': 'Оплата 50 / 50', 'body': ''}]})
        rec = import_proposal_package(blob, create_demo=False)
        p = Proposal.objects.get(slug='test-kp-import')
        self.assertEqual(p.lead, 'Написаний з нуля лендінг')
        self.assertEqual(p.highlights.get().title, 'Корпоративна безпека')
        self.assertFalse(p.specs.filter(kind='recommendation').exists())
        self.assertEqual(p.specs.get(kind='payment').title, 'Оплата 50/50')
        self.assertIn('CANON', '\n'.join(rec.log if isinstance(rec.log, list) else [str(rec.log)]))

    def test_normalize_proposals_dry_run_then_apply_all(self):
        import_proposal_package(make_zip({'guarantee_html': GUA}), create_demo=False)
        p = Proposal.objects.get(slug='test-kp-import')
        Proposal.objects.filter(pk=p.pk).update(lead='Кодописний сайт')
        ProposalHighlight.objects.create(proposal=p, order=9, title='Enterprise-безпека і масштаб')
        ProposalSpec.objects.create(proposal=p, kind='recommendation', order=0, title='Гарантія', body='x')
        out = StringIO()
        call_command('normalize_proposals', stdout=out)
        p.refresh_from_db()
        self.assertEqual(p.lead, 'Кодописний сайт')  # dry-run нічого не пише
        call_command('normalize_proposals', '--apply', stdout=StringIO())
        p.refresh_from_db()
        self.assertEqual(p.lead, 'Написаний з нуля сайт')
        self.assertTrue(p.highlights.filter(title='Корпоративна безпека і масштаб').exists())
        self.assertFalse(p.specs.filter(kind='recommendation', title='Гарантія').exists())
        out2 = StringIO()
        call_command('normalize_proposals', '--apply', stdout=out2)
        self.assertIn('Змін: 0', out2.getvalue())
