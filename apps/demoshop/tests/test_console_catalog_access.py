"""Кабінет КП: власник демо бачить свій каталог, чужий і чужий логін — ні.

Група DemoClient після міграцій не має model-permissions (їх ще нема в
момент RunPython). Доступ тримається на власнику активного магазину.
"""
import shutil
import tempfile
from datetime import date
from html.parser import HTMLParser
from io import BytesIO

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.core.proposal_models import Proposal
from apps.demoshop.catalog_admin import ShopCategoryAdmin, ShopProductAdmin, ShopReviewAdmin
from apps.demoshop.catalog_models import ShopCategory, ShopProduct, ShopProductImage, ShopReview
from apps.demoshop.models import DemoShop
from apps.demoshop.order_admin import ShopOrderAdmin
from apps.demoshop.order_models import ShopOrder, ShopOrderItem

INLINE_MEDIA_ROOT = tempfile.mkdtemp(prefix='renova-inline-media-')

User = get_user_model()

CATALOG_MODELS = ('shopproduct', 'shoporder', 'shopcategory', 'shopreview')


def make_proposal(slug, client_name):
    return Proposal.objects.create(
        slug=slug,
        client_name=client_name,
        title=client_name,
        issued_on=date(2026, 11, 6),
        is_published=True,
        kind=Proposal.DemoKind.SHOP,
    )


def make_owner(username):
    user = User.objects.create_user(username=username, password=None)
    user.is_staff = True
    user.is_active = True
    user.set_unusable_password()
    user.save(update_fields=['password', 'is_staff', 'is_active'])
    group, _created = Group.objects.get_or_create(name='DemoClient')
    user.groups.add(group)
    return user


def make_shop(slug, client_name, username):
    proposal = make_proposal(slug, client_name)
    owner = make_owner(username)
    shop = DemoShop.objects.create(
        proposal=proposal,
        name=client_name,
        slug=slug,
        owner_user=owner,
        demo_login=username,
    )
    category = ShopCategory.objects.create(shop=shop, name=f'Категорія {client_name}')
    product = ShopProduct.objects.create(
        shop=shop, category=category, name=f'Товар {client_name}', price='10.00',
    )
    ShopReview.objects.create(
        shop=shop, product=product, author_name=f'Відгук {client_name}', text='ok',
    )
    ShopOrder.objects.create(shop=shop, customer_name=f'Замовлення {client_name}', total='10.00')
    return shop


def model_path(shop, model_name):
    return f'{shop.get_console_path()}demoshop/{model_name}/'


def tearDownModule():
    shutil.rmtree(INLINE_MEDIA_ROOT, ignore_errors=True)


def tiny_png(name):
    buffer = BytesIO()
    Image.new('RGB', (2, 2), (120, 80, 40)).save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


class _AdminInputs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.fields = {}
        self._select = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        name = attrs.get('name')
        if tag == 'input' and name and attrs.get('type') not in ('submit', 'button', 'image'):
            if attrs.get('type') == 'checkbox':
                if 'checked' in attrs:
                    self.fields[name] = attrs.get('value', 'on')
            else:
                self.fields[name] = attrs.get('value', '')
        elif tag == 'select' and name:
            self._select = name
        elif tag == 'option' and self._select and 'selected' in attrs:
            self.fields[self._select] = attrs.get('value', '')

    def handle_endtag(self, tag):
        if tag == 'select':
            self._select = None


def admin_post_data(response):
    parser = _AdminInputs()
    parser.feed(response.content.decode())
    return parser.fields


class DemoConsoleCatalogAccessTests(TestCase):
    def setUp(self):
        self.shop = make_shop('console-shop-a', 'Магазин А', 'shop-console-a')
        self.other = make_shop('console-shop-b', 'Магазин Б', 'shop-console-b')

    def test_owner_has_no_model_permission(self):
        owner = self.shop.owner_user
        for codename in (
            'view_shopproduct', 'view_shoporder', 'view_shopcategory', 'view_shopreview',
            'view_shopproductimage', 'add_shopproductimage', 'change_shopproductimage',
            'delete_shopproductimage', 'view_shoporderitem', 'add_shoporder', 'delete_shoporder',
        ):
            self.assertFalse(owner.has_perm(f'demoshop.{codename}'))

    def test_autoentry_opens_own_catalog_and_keeps_shopblock(self):
        client = Client()
        home = client.get(self.shop.get_console_path(), follow=True)
        self.assertEqual(home.status_code, 200)
        self.assertEqual(home.wsgi_request.user.pk, self.shop.owner_user_id)
        self.assertContains(home, 'demoshop/shopproduct/')
        self.assertContains(home, 'demoshop/shoporder/')
        self.assertContains(home, 'demoshop/shopcategory/')
        self.assertContains(home, 'demoshop/shopreview/')
        self.assertContains(home, 'model-shopproduct')
        self.assertContains(home, 'model-shoporder')
        self.assertContains(home, 'model-shopcategory')
        self.assertContains(home, 'model-shopreview')
        self.assertContains(home, 'model-shopblock')

        block = client.get(model_path(self.shop, 'shopblock'))
        self.assertEqual(block.status_code, 200)
        self.assertContains(block, 'Мій магазин')

        expected = {
            'shopproduct': 'Товар Магазин А',
            'shopcategory': 'Категорія Магазин А',
            'shopreview': 'Відгук Магазин А',
            'shoporder': 'Замовлення Магазин А',
        }
        hidden = {
            'shopproduct': 'Товар Магазин Б',
            'shopcategory': 'Категорія Магазин Б',
            'shopreview': 'Відгук Магазин Б',
            'shoporder': 'Замовлення Магазин Б',
        }
        for model_name in CATALOG_MODELS:
            response = client.get(model_path(self.shop, model_name))
            self.assertEqual(response.status_code, 200, model_name)
            self.assertNotEqual(len(response.content), 135, model_name)
            self.assertContains(response, expected[model_name])
            self.assertNotContains(response, hidden[model_name])

        own_product = ShopProduct.objects.get(shop=self.shop)
        own_order = ShopOrder.objects.get(shop=self.shop)
        product_form = client.get(
            f'{self.shop.get_console_path()}demoshop/shopproduct/{own_product.pk}/change/',
        )
        self.assertEqual(product_form.status_code, 200)
        self.assertContains(product_form, own_product.name)
        order_form = client.get(
            f'{self.shop.get_console_path()}demoshop/shoporder/{own_order.pk}/change/',
        )
        self.assertEqual(order_form.status_code, 200)
        self.assertContains(order_form, own_order.customer_name)

    def test_other_demo_object_is_not_opened(self):
        other_product = ShopProduct.objects.get(shop=self.other)
        client = Client()
        client.get(self.shop.get_console_path(), follow=True)
        response = client.get(
            f'{self.shop.get_console_path()}demoshop/shopproduct/{other_product.pk}/change/',
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_product.name)
        self.assertContains(response, 'не існує')
        own_list = client.get(model_path(self.shop, 'shopproduct'))
        self.assertEqual(own_list.status_code, 200)
        self.assertContains(own_list, 'Товар Магазин А')
        self.assertNotContains(own_list, other_product.name)

        request = RequestFactory().get('/')
        request.user = self.shop.owner_user
        admin = ShopProductAdmin(ShopProduct, AdminSite())
        self.assertFalse(admin.has_view_permission(request, other_product))
        self.assertTrue(admin.has_view_permission(request, ShopProduct.objects.get(shop=self.shop)))
        self.assertFalse(admin.has_delete_permission(request, ShopProduct.objects.get(shop=self.shop)))
        self.assertFalse(ShopOrderAdmin(ShopOrder, AdminSite()).has_add_permission(request))
        self.assertFalse(ShopCategoryAdmin(ShopCategory, AdminSite()).has_delete_permission(request))
        self.assertFalse(ShopReviewAdmin(ShopReview, AdminSite()).has_delete_permission(request))

    def test_invalid_token_and_inactive_shop_fail_closed(self):
        self.assertEqual(Client().get('/k/this-key-does-not-exist-xx/').status_code, 404)
        self.shop.is_active = False
        self.shop.save(update_fields=['is_active'])
        self.assertEqual(Client().get(self.shop.get_console_path()).status_code, 404)
        client = Client()
        client.force_login(self.shop.owner_user)
        denied = client.get('/admin/demoshop/shopproduct/')
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(len(denied.content), 135)

    def test_staff_without_permission_is_forbidden_and_explicit_perm_stays(self):
        staff = User.objects.create_user('plain-staff', password=None)
        staff.is_staff = True
        staff.is_active = True
        staff.set_unusable_password()
        staff.save(update_fields=['password', 'is_staff', 'is_active'])
        client = Client()
        client.force_login(staff)
        for model_name in CATALOG_MODELS:
            denied = client.get(f'/admin/demoshop/{model_name}/')
            self.assertEqual(denied.status_code, 403, model_name)
            self.assertEqual(len(denied.content), 135, model_name)

        outsider = Client()
        user = User.objects.create_user('visitor', password=None)
        user.set_unusable_password()
        user.save(update_fields=['password'])
        outsider.force_login(user)
        self.assertEqual(outsider.get('/admin/demoshop/shopproduct/').status_code, 302)

        perm = Permission.objects.get(content_type__app_label='demoshop', codename='view_shopproduct')
        staff.user_permissions.add(perm)
        allowed = Client()
        allowed.force_login(staff)
        response = allowed.get('/admin/demoshop/shopproduct/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Товар Магазин А')
        self.assertNotContains(response, 'Товар Магазин Б')

    def test_public_proposal_and_storefront_stay_open(self):
        proposal = self.shop.proposal
        page = Client().get(reverse('proposal_detail', kwargs={'slug': proposal.slug}))
        self.assertEqual(page.status_code, 200)
        store = Client().get(reverse('demoshop:home', kwargs={'shop_slug': self.shop.slug}))
        self.assertEqual(store.status_code, 200)
        self.assertContains(store, 'Товар Магазин А')
        self.assertNotContains(store, 'Товар Магазин Б')


@override_settings(MEDIA_ROOT=INLINE_MEDIA_ROOT)
class DemoConsoleNestedSectionTests(TestCase):
    def setUp(self):
        self.shop = make_shop('nested-shop-a', 'Вкладений А', 'shop-nested-a')
        self.other = make_shop('nested-shop-b', 'Вкладений Б', 'shop-nested-b')
        self.own_product = ShopProduct.objects.get(shop=self.shop)
        self.other_product = ShopProduct.objects.get(shop=self.other)
        self.own_image = ShopProductImage.objects.create(
            product=self.own_product, image=tiny_png('own.png'), alt='Фото вкладене А', is_main=True,
        )
        self.other_image = ShopProductImage.objects.create(
            product=self.other_product, image=tiny_png('other.png'), alt='Фото вкладене Б', is_main=True,
        )
        self.own_order = ShopOrder.objects.get(shop=self.shop)
        self.other_order = ShopOrder.objects.get(shop=self.other)
        self.own_item = ShopOrderItem.objects.create(
            order=self.own_order, product=self.own_product, product_name='Рядок А', price='10.00', qty=1,
        )
        self.other_item = ShopOrderItem.objects.create(
            order=self.other_order, product=self.other_product, product_name='Рядок Б', price='20.00', qty=2,
        )
        self.client = Client()
        self.client.get(self.shop.get_console_path(), follow=True)

    def test_own_forms_show_photo_and_order_line_only(self):
        product_form = self.client.get(
            f'{self.shop.get_console_path()}demoshop/shopproduct/{self.own_product.pk}/change/',
        )
        self.assertEqual(product_form.status_code, 200)
        self.assertContains(product_form, 'images-TOTAL_FORMS')
        self.assertContains(product_form, 'Фото вкладене А')
        self.assertNotContains(product_form, 'Фото вкладене Б')
        self.assertNotContains(product_form, 'images-0-DELETE')

        order_form = self.client.get(
            f'{self.shop.get_console_path()}demoshop/shoporder/{self.own_order.pk}/change/',
        )
        self.assertEqual(order_form.status_code, 200)
        self.assertContains(order_form, 'items-TOTAL_FORMS')
        self.assertContains(order_form, 'Рядок А')
        self.assertNotContains(order_form, 'Рядок Б')
        self.assertNotContains(order_form, 'items-0-DELETE')

        add_order = self.client.get(f'{self.shop.get_console_path()}demoshop/shoporder/add/')
        self.assertEqual(add_order.status_code, 403)
        delete_product = self.client.get(
            f'{self.shop.get_console_path()}demoshop/shopproduct/{self.own_product.pk}/delete/',
        )
        self.assertEqual(delete_product.status_code, 403)

    def test_forged_inline_post_does_not_touch_other_tenant(self):
        product_url = f'{self.shop.get_console_path()}demoshop/shopproduct/{self.own_product.pk}/change/'
        product_form = self.client.get(product_url)
        payload = admin_post_data(product_form)
        payload['images-0-id'] = str(self.other_image.pk)
        payload['images-0-alt'] = 'чужий злам фото'
        payload['images-0-DELETE'] = 'on'
        forged = self.client.post(product_url, payload)
        self.assertIn(forged.status_code, (200, 302))
        self.other_image.refresh_from_db()
        self.own_image.refresh_from_db()
        self.assertEqual(self.other_image.alt, 'Фото вкладене Б')
        self.assertEqual(self.other_image.product_id, self.other_product.pk)
        self.assertEqual(self.own_image.alt, 'Фото вкладене А')
        self.assertEqual(self.own_image.product_id, self.own_product.pk)
        self.assertEqual(ShopProductImage.objects.count(), 2)

        order_url = f'{self.shop.get_console_path()}demoshop/shoporder/{self.own_order.pk}/change/'
        order_form = self.client.get(order_url)
        order_payload = admin_post_data(order_form)
        order_payload['items-0-id'] = str(self.other_item.pk)
        order_payload['items-0-product'] = str(self.other_product.pk)
        order_payload['items-0-product_name'] = 'чужий злам рядка'
        order_payload['items-0-DELETE'] = 'on'
        forged_order = self.client.post(order_url, order_payload)
        self.assertIn(forged_order.status_code, (200, 302))
        self.other_item.refresh_from_db()
        self.own_item.refresh_from_db()
        self.assertEqual(self.other_item.product_name, 'Рядок Б')
        self.assertEqual(self.other_item.order_id, self.other_order.pk)
        self.assertEqual(self.other_item.product_id, self.other_product.pk)
        self.assertEqual(self.own_item.product_name, 'Рядок А')
        self.assertEqual(self.own_item.order_id, self.own_order.pk)
        self.assertEqual(self.own_item.product_id, self.own_product.pk)
        self.assertEqual(ShopOrder.objects.count(), 2)

    def test_owner_can_change_own_photo_alt_only(self):
        product_url = f'{self.shop.get_console_path()}demoshop/shopproduct/{self.own_product.pk}/change/'
        payload = admin_post_data(self.client.get(product_url))
        payload['images-0-alt'] = 'Фото вкладене А змінено'
        saved = self.client.post(product_url, payload)
        self.assertEqual(saved.status_code, 302)
        self.own_image.refresh_from_db()
        self.other_image.refresh_from_db()
        self.assertEqual(self.own_image.alt, 'Фото вкладене А змінено')
        self.assertEqual(self.other_image.alt, 'Фото вкладене Б')
