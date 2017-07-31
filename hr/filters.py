import django_filters

from .models import *
from django.contrib.auth.models import User

class WorkPeriodFilter(django_filters.FilterSet):
    order_by_field = 'order'
    min_start_date = django_filters.DateTimeFilter(name='start_time', 
                                                   lookup_expr=('gte',))
    max_start_date = django_filters.DateTimeFilter(name='start_time',
                                                   lookup_expr=('lt',))
    class Meta:
        model = WorkPeriod
        fields = ('employee', 'id', 'min_start_date', 'max_start_date')
        order_by = ['start_time', '-start_time', 'id', '-id']
        
class EmployeeFilter(django_filters.FilterSet):
    class Meta:
        model = Employee
        fields = ('user',)

class DayOffFilter(django_filters.FilterSet):
    order_by_field = 'order'
    min_date = django_filters.DateTimeFilter(name='date', 
                                                   lookup_expr=('gte',))
    max_date = django_filters.DateTimeFilter(name='date',
                                                   lookup_expr=('lt',))
    class Meta:
        model = DayOff
        fields = ('employee', 'id', 'min_date', 'max_date')
        order_by = ['date', '-date', 'id', '-id']
        
        
class DaysOffRequestFilter(django_filters.FilterSet):
    order_by_field = 'order'
    seen = django_filters.BooleanFilter(name='seen',lookup_expr=('exact',))
    
    class Meta:
        model = DaysOffRequest
        fields = ('seen', 'start_date', 'employee')
        order_by = ['start_date', '-start_date', 'id', '-id']

