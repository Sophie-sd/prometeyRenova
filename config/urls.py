from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.conf import settings
from django.conf.urls.static import static

# URL без префіксу мови
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/set_language/', set_language, name='set_language'),
]

# URL з префіксом мови
urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('blog/', include('apps.blog.urls')),
    path('events/', include('apps.events.urls')),
    path('payment/', include('apps.payment.urls')),
    prefix_default_language=False
)

# Статичні файли для розробки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
