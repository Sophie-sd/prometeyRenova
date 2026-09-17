"""URL demo-корпоративного сайту: /demo-site/<slug>/…

Каталог (`catalog/`, `catalog/<cat>/`, `product/<p>/`) повертає 404, якщо
`CorpSite.has_catalog=False` (перевірка у `views._require_catalog`).
"""
from django.urls import path

from . import views

app_name = 'democorp'

urlpatterns = [
    path('<str:slug>/', views.home, name='home'),
    path('<str:slug>/vyrobnytstvo/', views.production, name='production'),
    path('<str:slug>/pro-nas/', views.about, name='about'),
    path('<str:slug>/kontakty/', views.contacts, name='contacts'),
    path('<str:slug>/katalog/', views.catalog, name='catalog'),
    path('<str:slug>/katalog/<str:product_slug>/', views.product_detail, name='product_detail'),
    path('<str:slug>/lead/', views.lead, name='lead'),
    path('<str:slug>/theme.css', views.theme_css, name='theme_css'),
    path('<str:slug>/admin-access/', views.admin_access, name='admin_access'),
    path('<str:slug>/admin-login/', views.admin_login, name='admin_login'),
]
