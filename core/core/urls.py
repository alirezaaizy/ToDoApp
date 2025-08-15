from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("todos.urls_site", namespace="site")),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('todos/', include('todos.urls', namespace='todos')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
