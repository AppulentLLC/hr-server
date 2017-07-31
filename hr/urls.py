#server URL Configuration

from django.conf.urls import url, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'employees', EmployeeViewSet,base_name='Employees')
router.register(r'work-periods', WorkPeriodViewSet,base_name='Work Periods')
router.register(r'days-off', DayOffViewSet, base_name= 'Day Off')
router.register(r'days-off-requests', DaysOffRequestViewSet, 
                base_name= 'Days Off Request')
router.register(r'user-settings', SettingsViewSet, base_name= 'Settings')


urlpatterns = (
    url(r'^', include(router.urls)),
)

