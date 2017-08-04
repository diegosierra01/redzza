from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from django.views.static import serve
from . import settings

from profiles.urls import router as profiles_router
from categories.urls import router as categories_router
from things.urls import router as things_router
from tags.urls import router as tags_router

router = routers.DefaultRouter()
router.registry.extend(profiles_router.registry)
router.registry.extend(categories_router.registry)
router.registry.extend(things_router.registry)
router.registry.extend(tags_router.registry)

urlpatterns = [
    url(r'^admin/', admin.site.urls,),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
