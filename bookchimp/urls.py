from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "BookChimp Admin"
admin.site.site_title = "BookChimp Admin Portal"
admin.site.index_title = "Welcome to the BookChimp Management Console"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("store.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
