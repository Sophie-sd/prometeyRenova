from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.utils import translation

from apps.core.context_processors import global_settings
from apps.core.models import SiteContactSettings
from apps.core.utils import get_site_contact_settings


class SiteContactSettingsTests(TestCase):
    def setUp(self):
        self.settings_obj, _ = SiteContactSettings.objects.get_or_create(pk=1)

    def test_singleton_second_create_raises(self):
        duplicate = SiteContactSettings(phone_e164='380000000000')
        with self.assertRaises(ValidationError):
            duplicate.save()

    def test_whatsapp_href_default_from_phone(self):
        self.settings_obj.phone_e164 = '380639520565'
        self.settings_obj.whatsapp_url = ''
        self.settings_obj.save()
        self.assertEqual(self.settings_obj.get_whatsapp_href(), 'https://wa.me/380639520565')

    def test_viber_href_default_from_phone(self):
        self.settings_obj.phone_e164 = '380639520565'
        self.settings_obj.viber_url = ''
        self.settings_obj.save()
        self.assertEqual(self.settings_obj.get_viber_href(), 'viber://add?number=380639520565')

    def test_maps_embed_from_coordinates(self):
        self.settings_obj.google_maps_embed_url = ''
        self.settings_obj.maps_latitude = '50.450100'
        self.settings_obj.maps_longitude = '30.523400'
        self.settings_obj.maps_zoom = 14
        self.settings_obj.save()
        src = self.settings_obj.get_maps_embed_src()
        self.assertIn('50.450100', src)
        self.assertIn('30.523400', src)
        self.assertIn('output=embed', src)

    def test_maps_embed_url_priority(self):
        self.settings_obj.google_maps_embed_url = 'https://www.google.com/maps/embed?pb=example'
        self.settings_obj.maps_latitude = '50.450100'
        self.settings_obj.maps_longitude = '30.523400'
        self.settings_obj.save()
        self.assertEqual(
            self.settings_obj.get_maps_embed_src(),
            'https://www.google.com/maps/embed?pb=example',
        )

    def test_context_processor_includes_site_contact(self):
        request = RequestFactory().get('/')
        context = global_settings(request)
        self.assertIn('site_contact', context)
        self.assertIsInstance(context['site_contact'], SiteContactSettings)

    def test_get_site_contact_settings_returns_pk_one(self):
        first = get_site_contact_settings()
        second = get_site_contact_settings()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.pk, 1)

    def test_localized_address_english(self):
        self.settings_obj.address = 'Київ, бульвар Тараса Шевченка 46а'
        self.settings_obj.save()
        with translation.override('en'):
            self.assertEqual(
                self.settings_obj.get_localized_address(),
                'Kyiv, Taras Shevchenko Boulevard 46a',
            )

    def test_localized_address_ukrainian(self):
        self.settings_obj.address = 'Київ, бульвар Тараса Шевченка 46а'
        self.settings_obj.save()
        with translation.override('uk'):
            self.assertEqual(
                self.settings_obj.get_localized_address(),
                'Київ, бульвар Тараса Шевченка 46а',
            )
