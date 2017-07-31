#server URL Configuration

from django.conf.urls import url, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, base_name='Users')
router.register(r'privileges', PrivilegesViewSet, base_name='Privileges')
router.register(r'applications', ApplicationViewSet, base_name='Applications')

urlpatterns = (
    url(r'^', include(router.urls)),
)

