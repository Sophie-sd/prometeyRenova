"""Сайдбар студійної адмінки: посилання «Підписки» і CSP-виняток."""
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from apps.core.middleware import CSPMiddleware
from config.settings import _payment_subscriptions_admin_link


class SubscriptionsSidebarLinkTests(SimpleTestCase):
    def test_link_is_request_callable(self):
        request = RequestFactory().get('/admin/')
        url = _payment_subscriptions_admin_link(request)
        self.assertTrue(callable(_payment_subscriptions_admin_link))
        self.assertTrue(url.endswith('/payment/paymentlink/?is_subscription=1'))
        self.assertNotIn('__proxy__', url)


class StudioAdminCspTests(SimpleTestCase):
    def _html(self, path):
        def get_response(request):
            return HttpResponse('<html></html>', content_type='text/html')

        request = RequestFactory().get(path)
        return CSPMiddleware(get_response)(request)

    @override_settings(ADMIN_URL='admin/')
    def test_fallback_admin_has_no_csp(self):
        response = self._html('/admin/')
        self.assertNotIn('Content-Security-Policy', response)
        self.assertNotIn('Content-Security-Policy', self._html('/admin'))

    @override_settings(ADMIN_URL='studio-secret/')
    def test_custom_prefix_skips_csp_old_admin_does_not(self):
        secret = self._html('/studio-secret/')
        self.assertNotIn('Content-Security-Policy', secret)
        public = self._html('/admin/')
        self.assertIn("'strict-dynamic'", public['Content-Security-Policy'])
