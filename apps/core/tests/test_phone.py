from django.test import TestCase

from apps.core.phone import normalize_phone, parse_phone
from apps.core.phone_forms import clean_phone_value
from django import forms


class NormalizePhoneTests(TestCase):
    def test_valid_ukrainian_variants(self):
        for raw in (
            '+380671234567', '380671234567', '0671234567', '671234567',
            '+38 (067) 123-45-67', '+380 (67) 123-45-67', '067-123-45-67',
            '067 123 45 67', '80671234567', '00380671234567', ' +38(067)1234567 ',
        ):
            with self.subTest(raw=raw):
                self.assertEqual(normalize_phone(raw), '+380671234567')

    def test_invalid_ukrainian(self):
        cases = {
            '': 'empty', '   ': 'empty', '067123': 'short', '+380 67 123 45': 'short',
            '+38067123456789': 'long', '06712345678': 'long', 'abc': 'chars',
            '067abc1234567': 'chars', '555-1234': 'short', '+380': 'short',
        }
        for raw, err in cases.items():
            with self.subTest(raw=raw):
                e164, code = parse_phone(raw)
                self.assertIsNone(e164)
                self.assertEqual(code, err)

    def test_other_countries_by_length(self):
        self.assertEqual(normalize_phone('+44 20 7946 0958'), '+442079460958')
        self.assertEqual(normalize_phone('+48 123 456 789'), '+48123456789')
        self.assertEqual(normalize_phone('0048123456789'), '+48123456789')
        self.assertEqual(normalize_phone('+1 (212) 555-0100'), '+12125550100')
        self.assertIsNone(normalize_phone('+48 123 456'))         # PL short
        self.assertIsNone(normalize_phone('+48 123 456 7890'))    # PL long
        self.assertIsNone(normalize_phone('+999 1234'))           # unknown, too short

    def test_form_clean_helper(self):
        self.assertEqual(clean_phone_value('067 123 45 67'), '+380671234567')
        self.assertEqual(clean_phone_value('', required=False), '')
        with self.assertRaises(forms.ValidationError):
            clean_phone_value('067 123', required=False)
        with self.assertRaises(forms.ValidationError):
            clean_phone_value('', required=True)


class FormSubmitPhoneTests(TestCase):
    def test_submit_normalizes_and_rejects(self):
        url = '/forms/submit/'
        bad = self.client.post(url, {'form_type': 'call_request', 'name': 'Іван', 'phone': '067 123'})
        self.assertFalse(bad.json()['success'])
        self.assertIn('номер', bad.json()['message'].lower())
        long_ = self.client.post(url, {'form_type': 'call_request', 'name': 'Іван', 'phone': '+380 67 123 45 678'})
        self.assertFalse(long_.json()['success'])
        letters = self.client.post(url, {'form_type': 'call_request', 'name': 'Іван', 'phone': 'abcdefghij'})
        self.assertFalse(letters.json()['success'])
