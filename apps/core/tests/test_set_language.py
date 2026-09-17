"""ERR-141: custom set_language with prefix_default_language=False."""
from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from apps.core.i18n_views import strip_lang_prefix, translate_path


class TranslatePathTests(SimpleTestCase):
    def test_strip_en_prefix(self):
        self.assertEqual(strip_lang_prefix('/en/'), '/')
        self.assertEqual(strip_lang_prefix('/en'), '/')
        self.assertEqual(strip_lang_prefix('/en/demo/x/'), '/demo/x/')

    def test_strip_leaves_default_path(self):
        self.assertEqual(strip_lang_prefix('/demo/x/'), '/demo/x/')
        self.assertEqual(strip_lang_prefix('/contacts/'), '/contacts/')

    def test_uk_from_en_root(self):
        self.assertEqual(translate_path('/en/', 'uk'), '/')

    def test_en_demo_from_unprefixed(self):
        self.assertEqual(translate_path('/demo/x/', 'en'), '/en/demo/x/')

    def test_uk_demo_from_en(self):
        self.assertEqual(translate_path('/en/demo/x/', 'uk'), '/demo/x/')

    def test_keeps_query_string(self):
        self.assertEqual(
            translate_path('/en/demo/x/?q=1', 'uk'),
            '/demo/x/?q=1',
        )


@override_settings(ROOT_URLCONF='config.urls')
class SetLanguageViewTests(SimpleTestCase):
    def test_uk_from_en_root_location(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'uk', 'next': '/en/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
        self.assertEqual(
            response.cookies[settings.LANGUAGE_COOKIE_NAME].value,
            'uk',
        )

    def test_en_demo_location(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'en', 'next': '/demo/x/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/en/demo/x/')

    def test_uk_from_en_demo_location(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'uk', 'next': '/en/demo/x/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/demo/x/')

    def test_rejects_offsite_next(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'uk', 'next': 'https://evil.example/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
