"""
Тести для форм зворотного зв'язку
"""
from django.test import TestCase, Client
from django.urls import reverse
import json


class FormValidationTests(TestCase):
    """Тести валідації форм"""

    def setUp(self):
        self.client = Client()
        self.submit_url = reverse('form_submit')

    def test_footer_form_with_valid_data(self):
        """Тест футер форми з корректними даними"""
        data = {
            'form_type': 'footer-consultation',
            'name': 'Іван Петренко',
            'phone': '+380631234567'
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue(json_data['success'])

    def test_call_request_form_with_valid_data(self):
        """Тест форми замовити дзвінок з корректними даними"""
        data = {
            'form_type': 'call_request',
            'name': 'Марія Іванівна',
            'phone': '0631234567'
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue(json_data['success'])

    def test_contact_form_with_valid_data(self):
        """Тест форми контактів з корректними даними"""
        data = {
            'form_type': 'contact',
            'name': 'Петро Сидоренко',
            'phone': '+380961234567',
            'email': 'petro@example.com',
            'message': 'Мені потрібна консультація'
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue(json_data['success'])

    def test_form_with_invalid_name_short(self):
        """Тест форми з дуже коротким ім'ям"""
        data = {
            'form_type': 'footer-consultation',
            'name': 'А',
            'phone': '+380631234567'
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertFalse(json_data['success'])
        self.assertIn('ім\'я', json_data['message'].lower())

    def test_form_with_invalid_name_only_digits(self):
        """Тест форми з ім'ям тільки з цифр"""
        data = {
            'form_type': 'footer-consultation',
            'name': '12345',
            'phone': '+380631234567'
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertFalse(json_data['success'])

    def test_form_with_invalid_phone_short(self):
        """Тест форми з дуже коротким номером телефону"""
        data = {
            'form_type': 'footer-consultation',
            'name': 'Іван Петренко',
            'phone': '123456'
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertFalse(json_data['success'])
        self.assertIn('номер телефону', json_data['message'].lower())

    def test_form_missing_required_fields(self):
        """Тест форми без обов'язкових полів"""
        data = {
            'form_type': 'footer-consultation',
            'name': 'Іван Петренко'
            # Телефон відсутній
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertFalse(json_data['success'])

    def test_form_with_special_chars_in_phone(self):
        """Тест форми з спеціальними символами в телефоні"""
        data = {
            'form_type': 'footer-consultation',
            'name': 'Іван Петренко',
            'phone': '+38 (063) 123-45-67'
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue(json_data['success'])

    def test_form_with_cyrillic_name(self):
        """Тест форми з кирилицею в ім'ї"""
        data = {
            'form_type': 'footer-consultation',
            'name': 'Василь',
            'phone': '+380631234567'
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue(json_data['success'])

    def test_form_with_mixed_chars_in_name(self):
        """Тест форми з різними типами символів в ім'ї"""
        data = {
            'form_type': 'footer-consultation',
            'name': 'John Джон',
            'phone': '+380631234567'
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue(json_data['success'])
