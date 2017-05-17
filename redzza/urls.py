from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from . import views
from . import settings


urlpatterns = [
    # Url - Administracion
    url(r'^admin/', admin.site.urls),
    # Url - index de la aplicacion, sin sesion
    url(r'^$', views.index, name='index'),
    # Urls - referente a usuarios y sus perfiles
    url(r'^', include('profiles.urls')),
    # Urls - referente a categorias
    url(r'^', include('categories.urls')),
    # staticfiles
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
