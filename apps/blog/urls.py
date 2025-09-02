from django.urls import path, re_path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('search/', views.blog_search, name='blog_search'),
    re_path(r'^(?P<slug>[-\w\u0400-\u04FF.]+)/$', views.BlogDetailView.as_view(), name='blog_detail'),
] 