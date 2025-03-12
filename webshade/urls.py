
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf.urls.static import static,serve
from django.conf import settings

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^assets/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    path('', include('webshadeApp.urls')),
    path('admin-panel-124432/', include('webshadeAdmin.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
