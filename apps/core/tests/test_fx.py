"""Курс валют: конвертація з євро, cookie, право в адмінці."""
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.template import RequestContext, Template
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.core.admin_permissions import (
    STAFF_ADMIN_USERNAME,
    apply_fx_grant,
    get_staff_admin_permissions,
)
from apps.core.fx import format_package_price, format_range
from apps.core.fx_models import ExchangeRateSettings


class DummyPackage:
    def __init__(self, price, currency):
        self.price = Decimal(price)
        self.currency = currency

    def format_price(self):
        return f'{self.price} {self.currency}'


class FxConvertTests(TestCase):
    def setUp(self):
        self.rates = ExchangeRateSettings.objects.create(
            uah_per_eur=Decimal('40'),
            usd_per_eur=Decimal('1.085'),
            czk_per_eur=Decimal('25'),
        )
        self.factory = RequestFactory()

    def _render(self, source, cookie=None):
        request = self.factory.get('/contacts/')
        if cookie:
            request.COOKIES['pl_currency'] = cookie
        return Template(source).render(RequestContext(request))

    def test_eur_range_and_package_stay(self):
        html = self._render('{% load fx_tags %}{% fx_range 250 400 %}')
        self.assertEqual(html, '250–400 €')
        package = DummyPackage('1000.00', '€')
        self.assertEqual(format_package_price(package, 'EUR', self.rates), package.format_price())

    def test_uah_converts_commercial_amounts(self):
        html = self._render('{% load fx_tags %}{% fx_from 800 %}{% fx_range 250 400 %}', 'UAH')
        self.assertIn('від 32\u00a0000 ₴', html)
        self.assertIn('10\u00a0000–16\u00a0000 ₴', html)
        self.assertEqual(
            format_range(1500, 5000, 'USD', self.rates),
            '1\u00a0628–5\u00a0425 $',
        )

    def test_non_eur_package_is_not_converted(self):
        package = DummyPackage('900.00', 'грн')
        self.assertEqual(
            format_package_price(package, 'UAH', self.rates),
            '900.00 грн',
        )

    def test_zero_rate_hides_button(self):
        self.rates.usd_per_eur = Decimal('0')
        self.rates.save()
        html = self._render('{% load fx_tags %}{% currency_switcher "light" %}')
        self.assertIn('value="UAH"', html)
        self.assertNotIn('value="USD"', html)
        self.assertIn('value="CZK"', html)

    def test_open_redirect_is_rejected(self):
        response = self.client.post('/i18n/set_currency/', {
            'currency': 'UAH',
            'next': 'https://evil.example/phish',
        })
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.example', response['Location'])
        self.assertEqual(response.cookies['pl_currency'].value, 'UAH')

    def test_same_host_next_is_kept(self):
        response = self.client.post('/i18n/set_currency/', {
            'currency': 'EUR',
            'next': '/contacts/',
        })
        self.assertTrue(response['Location'].endswith('/contacts/'))

    def test_unknown_currency_falls_back_to_eur(self):
        response = self.client.post('/i18n/set_currency/', {
            'currency': 'BTC',
            'next': '/',
        })
        self.assertEqual(response.cookies['pl_currency'].value, 'EUR')


class FxAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username='fx-root',
            email='root@prometeylabs.com',
            password='test-pass-123',
        )
        self.staff = User.objects.create_user(
            username='fx-staff',
            email='staff@prometeylabs.com',
            password='test-pass-123',
            is_staff=True,
        )

    def test_staff_without_grant_cannot_open_rates(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:core_exchangeratesettings_changelist'))
        self.assertEqual(response.status_code, 403)

    def test_superuser_opens_singleton(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('admin:core_exchangeratesettings_changelist'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/change/', response['Location'])
        self.assertTrue(ExchangeRateSettings.objects.filter(pk=1).exists())

    def test_checkbox_only_for_superuser_and_grant_works(self):
        request = RequestFactory().get('/admin/auth/user/')
        request.user = self.superuser
        user_admin = admin.site._registry[get_user_model()]
        fields = []
        for _title, opts in user_admin.get_fieldsets(request, self.staff):
            for field in opts['fields']:
                fields.extend(field if isinstance(field, (list, tuple)) else [field])
        self.assertIn('can_set_fx', fields)
        self.client.force_login(self.superuser)
        page = self.client.get(reverse('admin:auth_user_change', args=[self.staff.pk]))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Може встановлювати курс валют')

        request.user = self.staff
        fields = []
        for _title, opts in user_admin.get_fieldsets(request, self.staff):
            for field in opts['fields']:
                fields.extend(field if isinstance(field, (list, tuple)) else [field])
        self.assertNotIn('can_set_fx', fields)

        apply_fx_grant(self.staff, True)
        staff = get_user_model().objects.get(pk=self.staff.pk)
        self.assertTrue(staff.has_perm('core.change_exchangeratesettings'))
        self.client.force_login(staff)
        response = self.client.get(reverse('admin:core_exchangeratesettings_changelist'))
        self.assertEqual(response.status_code, 302)

        apply_fx_grant(staff, False)
        staff = get_user_model().objects.get(pk=self.staff.pk)
        self.assertFalse(staff.has_perm('core.change_exchangeratesettings'))

    def test_blanket_grant_excludes_fx_permission(self):
        self.assertTrue(
            Permission.objects.filter(codename='change_exchangeratesettings').exists()
        )
        codenames = set(get_staff_admin_permissions().values_list('codename', flat=True))
        self.assertNotIn('change_exchangeratesettings', codenames)
        self.assertNotIn('view_exchangeratesettings', codenames)

    def test_render_build_keeps_explicit_fx_grant(self):
        User = get_user_model()
        user = User.objects.create_user(
            username=STAFF_ADMIN_USERNAME,
            password='test-pass-123',
            is_staff=True,
        )
        apply_fx_grant(user, True)
        call_command('grant_staff_admin_access', username=STAFF_ADMIN_USERNAME)
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.has_perm('core.change_exchangeratesettings'))
        self.assertTrue(user.has_perm('core.view_formsubmission'))
