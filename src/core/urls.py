from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),
    path('account/', include('accounts.urls')),
    path('', include('notes.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
