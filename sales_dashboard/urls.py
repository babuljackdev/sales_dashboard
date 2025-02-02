from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve 
from django.urls import re_path as url

urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('', include('sales.urls')),
] 
