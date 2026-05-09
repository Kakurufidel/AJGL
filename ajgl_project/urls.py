from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

urlpatterns = [
    path('admin-ajgl/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)