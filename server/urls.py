#server URL Configuration

from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = (
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', 
                               namespace='rest_framework')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^$', RedirectView.as_view(url='/hr/', permanent=False), 
        name='home'),
    url(r'^hr/', include('hr.urls', namespace='hr')),
    url(r'^authentication/', include('authentication.urls',
                                     namespace='authentication')) 
)


