"""URL демо-магазину: /demo/<shop_slug>/...

`str`, не `slug` path-конвертер: наші slug-поля мають `allow_unicode=True`
(українські назви категорій/товарів), а вбудований `slug` converter матчить
лише `[-a-zA-Z0-9_]+` і давав 404 на кириличні slugs.
"""
from django.urls import path

from . import views

app_name = 'demoshop'

urlpatterns = [
    path('<str:shop_slug>/', views.home, name='home'),
    path('<str:shop_slug>/hits/', views.hits, name='hits'),
    path('<str:shop_slug>/catalog/', views.catalog, name='catalog'),
    path('<str:shop_slug>/promotions/', views.promotions, name='promotions'),
    path('<str:shop_slug>/product/<str:product_slug>/', views.product_detail, name='product_detail'),
    path('<str:shop_slug>/wishlist/', views.wishlist, name='wishlist'),
    path('<str:shop_slug>/cart/', views.cart_view, name='cart'),
    path('<str:shop_slug>/cart/add/', views.cart_add, name='cart_add'),
    path('<str:shop_slug>/cart/remove/', views.cart_remove, name='cart_remove'),
    path('<str:shop_slug>/cart/set-qty/', views.cart_set_qty, name='cart_set_qty'),
    path('<str:shop_slug>/checkout/', views.checkout, name='checkout'),
    path('<str:shop_slug>/order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('<str:shop_slug>/api/np/cities/', views.np_cities, name='np_cities'),
    path('<str:shop_slug>/api/np/warehouses/', views.np_warehouses, name='np_warehouses'),
    path('<str:shop_slug>/admin-access/', views.admin_access, name='admin_access'),
    path('<str:shop_slug>/admin-login/', views.admin_login, name='admin_login'),
    path('<str:shop_slug>/theme.css', views.theme_css, name='theme_css'),
]
