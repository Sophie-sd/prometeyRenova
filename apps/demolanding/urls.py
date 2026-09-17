"""URL demo-лендінгу: /demo-landing/<slug>/…

`str`, не `slug` path-конвертер — slug-поле `allow_unicode=True` (kirilic slugs),
вбудований `slug` converter матчить лише `[-a-zA-Z0-9_]+` (parity з demoshop).
"""
from django.urls import path

from . import views

app_name = 'demolanding'

urlpatterns = [
    path('<str:slug>/', views.home, name='home'),
    path('<str:slug>/lead/', views.lead, name='lead'),
    path('<str:slug>/theme.css', views.theme_css, name='theme_css'),
    path('<str:slug>/admin-access/', views.admin_access, name='admin_access'),
    path('<str:slug>/admin-login/', views.admin_login, name='admin_login'),
]
