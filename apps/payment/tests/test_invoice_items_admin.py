"""Рядки послуг у рахунку та початковий стан еквайрингу в адмінці."""
from datetime import date
from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import RequestFactory, TestCase

from apps.payment.admin import PaymentLinkAdmin, PaymentLinkAdminForm
from apps.payment.invoice_admin import InvoiceItemInline
from apps.payment.invoice_models import Invoice, InvoiceItem
from apps.payment.models import PaymentLink, RecipientProfile

User = get_user_model()


def payment_perm(codename):
    return Permission.objects.get(
        content_type__app_label='payment',
        codename=codename,
    )


def user_with(*codenames):
    user = User.objects.create_user(
        username='-'.join(codenames)[:140] or 'staff',
        password='test-pass',
        is_staff=True,
    )
    user.user_permissions.set([payment_perm(code) for code in codenames])
    return User.objects.get(pk=user.pk)


class InvoiceItemInlineTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.inline = InvoiceItemInline(Invoice, AdminSite())
        self.manager = user_with(
            'add_invoice',
            'change_invoice',
            'view_invoice',
            'add_invoiceitem',
            'change_invoiceitem',
            'view_invoiceitem',
        )
        self.recipient = RecipientProfile.objects.create(
            name='ФОП Тест',
            recipient='ФОП Тест',
            iban='UA123',
            ipn='1234567890',
        )
        self.invoice = Invoice(
            number=900001,
            invoice_date=date(2026, 11, 27),
            recipient=self.recipient,
            client_name='ТОВ Клієнт',
            client_tax_id='12345678',
            contract_number='1',
            contract_date=date(2026, 11, 1),
        )
        self.invoice.save()
        InvoiceItem.objects.create(
            invoice=self.invoice, title='Послуга А', quantity=Decimal('1'), price=Decimal('100'),
        )
        InvoiceItem.objects.create(
            invoice=self.invoice, title='Послуга Б', quantity=Decimal('2'), price=Decimal('50'),
        )

    def request_for(self, user):
        request = self.factory.get('/admin/payment/invoice/add/')
        request.user = user
        return request

    def test_create_form_shows_one_blank_row_and_allows_delete(self):
        request = self.request_for(self.manager)
        self.assertEqual(self.inline.get_extra(request, None), 0)
        self.assertEqual(self.inline.min_num, 1)
        self.assertTrue(self.inline.has_add_permission(request, None))
        self.assertFalse(self.manager.has_perm('payment.delete_invoiceitem'))
        self.assertTrue(self.inline.has_delete_permission(request, None))

        formset_class = self.inline.get_formset(request, obj=None)
        self.assertEqual(formset_class.extra, 0)
        self.assertEqual(formset_class.min_num, 1)
        self.assertTrue(formset_class.validate_min)
        self.assertTrue(formset_class.can_delete)
        formset = formset_class()
        self.assertEqual(formset.initial_form_count(), 0)
        self.assertEqual(formset.total_form_count(), 1)
        self.assertEqual(len(formset.forms), 1)

    def test_saved_invoice_keeps_lines_readonly(self):
        request = self.request_for(self.manager)
        self.assertTrue(self.inline._lines_locked(self.invoice))
        self.assertFalse(self.inline.has_add_permission(request, self.invoice))
        self.assertFalse(self.inline.has_change_permission(request, self.invoice))
        self.assertFalse(self.inline.has_delete_permission(request, self.invoice))

        formset_class = self.inline.get_formset(request, obj=self.invoice)
        self.assertFalse(formset_class.validate_min)
        self.assertFalse(formset_class.can_delete)
        formset = formset_class(instance=self.invoice)
        self.assertEqual(formset.initial_form_count(), 2)
        self.assertEqual(formset.extra, 0)
        self.assertEqual(formset.total_form_count(), 2)

    def test_delete_permission_follows_invoice_change_or_item_delete(self):
        request = self.request_for(self.manager)
        self.assertTrue(self.inline.has_delete_permission(request, None))

        viewer = user_with('view_invoice', 'view_invoiceitem')
        view_request = self.request_for(viewer)
        self.assertFalse(self.inline.has_delete_permission(view_request, None))

        deleter = user_with('delete_invoiceitem')
        delete_request = self.request_for(deleter)
        self.assertTrue(self.inline.has_delete_permission(delete_request, None))
        self.assertFalse(self.inline.has_delete_permission(delete_request, self.invoice))


class AcquiringInitialTests(TestCase):
    def test_model_default_stays_on(self):
        self.assertIs(PaymentLink._meta.get_field('use_acquiring').default, True)
        self.assertTrue(PaymentLink().use_acquiring)

    def test_new_admin_form_starts_with_acquiring_off(self):
        admin = PaymentLinkAdmin(PaymentLink, AdminSite())
        request = RequestFactory().get('/admin/payment/paymentlink/add/?use_acquiring=1')
        request.user = User.objects.create_superuser(
            username='sofia',
            email='sofia@example.com',
            password='test-pass',
        )
        initial = admin.get_changeform_initial_data(request)
        self.assertIs(initial['use_acquiring'], False)

        form = PaymentLinkAdminForm()
        self.assertFalse(form['use_acquiring'].value())
        forced = PaymentLinkAdminForm(initial={'use_acquiring': True})
        self.assertFalse(forced['use_acquiring'].value())

        checked = PaymentLinkAdminForm(data={'use_acquiring': 'on', 'client_name': 'Клієнт'})
        self.assertTrue(checked['use_acquiring'].value())
        unchecked = PaymentLinkAdminForm(data={'client_name': 'Клієнт'})
        self.assertFalse(unchecked['use_acquiring'].value())

    def test_existing_payment_link_keeps_saved_acquiring_flag(self):
        enabled = PaymentLink.objects.create(
            client_name='Увімкнений',
            amount=Decimal('100.00'),
            currency=PaymentLink.Currency.UAH,
        )
        self.assertTrue(enabled.use_acquiring)
        enabled_form = PaymentLinkAdminForm(instance=enabled)
        self.assertTrue(enabled_form['use_acquiring'].value())

        disabled = PaymentLink.objects.create(
            client_name='Вимкнений',
            amount=Decimal('50.00'),
            currency=PaymentLink.Currency.UAH,
            use_acquiring=False,
        )
        disabled_form = PaymentLinkAdminForm(instance=disabled)
        self.assertFalse(disabled_form['use_acquiring'].value())
