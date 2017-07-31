import random
from django.contrib.auth.models import User, Group
from django.utils import dateparse, timezone

from rest_framework import exceptions, filters, permissions, status, response
from rest_framework import parsers, renderers, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework_json_api.parsers import JSONParser as JSONAPIParser
from rest_framework_json_api.renderers import JSONRenderer as JSONAPIRenderer
from rest_framework_json_api import pagination

from .filters import *
from .models import *
from authentication.permissions import *
from .serializers import *


class DefaultViewSet(viewsets.ModelViewSet):
    parser_classes = (JSONAPIParser, parsers.FormParser, 
                      parsers.MultiPartParser)
    renderer_classes = (JSONAPIRenderer, renderers.BrowsableAPIRenderer)
    
    def user_is_manager(self):
        user = getattr(self.request, 'user', None)
        privileges = getattr(user, 'privileges', None)
        hr_role = privileges.hr_role
        if privileges and (privileges.is_global_admin or hr_role in ['m', 'a']):
            return True
        return False
        
    def user_is_terminal(self):
        user = getattr(self.request, 'user', None)
        privileges = getattr(user, 'privileges', None)
        if privileges and privileges.hr_role == 't':
            return True
        return False
        
    def user_is_manager_or_terminal(self):
        return self.user_is_manager() or self.user_is_terminal()



class EmployeeViewSet(DefaultViewSet):
    resource_name = 'employees'
    serializer_class = EmployeeSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = EmployeeFilter
    permission_classes = (permissions.IsAuthenticated, IsManagerOrNotCreate,
                          IsNotDelete)
                          
    def get_queryset(self):
        if self.user_is_manager_or_terminal():
            return Employee.objects.all()
        return Employee.objects.filter(user__id=self.request.user.id)
        
    def get_serializer_class(self):
        if self.user_is_terminal():
            return TerminalEmployeeSerializer
        return EmployeeSerializer
        
    def create(self, request, *args, **kwargs):
        created_by = {'type': 'users', 'id': request.user.id}
        request.data['created_by'] = created_by
        updated_by = {'type': 'users', 'id': request.user.id}
        request.data['updated_by'] = updated_by
        return super().create(request, *args, **kwargs)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self.user_is_manager():
            for param in ['first_name', 'last_name', 'ssn', 
                          'currently_employed']:
                if param in request.data.keys():
                    if request.data[param] != getattr(instance, param):
                        raise exceptions.PermissionDenied
        updated_by = {'type': 'users', 'id': request.user.id}
        request.data['updated_by'] = updated_by
        print(request.data)
        return super().update(request, *args, **kwargs)

class WorkPeriodViewSet(DefaultViewSet):
    resource_name = 'work-periods'
    serializer_class = WorkPeriodSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = WorkPeriodFilter
    pagination_class = pagination.PageNumberPagination
    permission_classes = (permissions.IsAuthenticated, IsManagerOrReadOnly,
                          IsNotDelete)
                              
    def get_queryset(self):
        if self.user_is_manager_or_terminal():
            return WorkPeriod.objects.all()
        user_id = self.request.user.id
        return WorkPeriod.objects.filter(employee__user__id=user_id)

    def create(self, request, *args, **kwargs):
        # should this be moved to a separate method?
        start_time = request.data.get('start_time', None)
        start_time = dateparse.parse_datetime(start_time)
        
        try:
            previous_work_period = WorkPeriod.objects.filter(
                start_time__lt=start_time,
                employee__id=request.data['employee']['id']
            ).order_by('-start_time')[0]
            if previous_work_period.end_time:
                if previous_work_period.end_time > start_time:
                    msg = 'This work period overlaps with the previous one.'
                    return response.Response({'status': msg},
                                             status=status.HTTP_400_BAD_REQUEST)
        except IndexError:
            pass
        
        end_time = request.data.get('end_time', None)
        if end_time is not None:
            end_time = dateparse.parse_datetime(end_time)
            if end_time > start_time:
                try:
                    next_work_period = WorkPeriod.objects.filter(
                        start_time__gt=end_time,
                        employee__id=request.data['employee']['id']
                    ).order_by('start_time')[0]
                    
                    if next_work_period.start_time < end_time:
                        msg = 'This work period overlaps with the next one.'
                        return response.Response({'status': msg},
                                                 status=status.HTTP_400_BAD_REQUEST)  
                except IndexError:
                    pass
            else:
                msg = 'End Time can not be before Start Time'
                return response.Response({'status': msg},
                                         status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        start_time = request.data.get('start_time', None)
        end_time = request.data.get('end_time', None)        
        start_time_obj = dateparse.parse_datetime(start_time)
        msg = ''
        if start_time_obj != instance.start_time:
            msg = "Cannot change 'start-time' for this work period."
        if end_time is not None:
            end_time_obj = dateparse.parse_datetime(end_time)
            print(end_time_obj)
            if instance.end_time and (end_time_obj != instance.end_time):
                msg = 'Employee is already clocked out for this work period.'
            elif not (instance.start_time < end_time_obj <= timezone.now()):
                msg = 'Clock out can not be out of range'
        if len(msg) > 0:
            return response.Response({'status': msg},
                                     status=status.HTTP_400_BAD_REQUEST)  
                              
        return super().update(request, *args, **kwargs)
    
    
    @list_route(methods=('post',), 
                permission_classes=(permissions.IsAuthenticated, IsTerminal))
    def clock_in(self, request):
        now = timezone.now()
        start_time = now.replace(second=0, microsecond=0)
        request.data.update(start_time=start_time, end_time=None)
        return self.create(request)
        
    @detail_route(methods=('post',),
                  permission_classes=(permissions.IsAuthenticated, IsTerminal))
    def clock_out(self, request, pk):
        now = timezone.now()
        end_time = now.replace(second=0, microsecond=0)
        instance = self.get_object()
        employee = instance.employee
        # Prevent duplicate clock-outs.
        work_periods = self.get_queryset().filter(employee=employee)
        latest_work_period = work_periods.order_by('-start_time')[0]
        if latest_work_period.end_time:
            return response.Response({'status': 'Employee already clocked out'},
                                     status=status.HTTP_400_BAD_REQUEST)

        request.data['end_time'] = str(timezone.localtime(end_time))
        return self.partial_update(request)
    
    @list_route()
    def mine(self, request):
        work_periods = WorkPeriod.objects.filter(employee_id=request.user.id)
        serializer = self.get_serializer(work_periods, many=True)
        return response.Response(serializer.data)
              
    @list_route(methods=('get',))
    def latest(self, request):
        employee_id = request.query_params.get('employee', None)
        if employee_id is not None:
            try:
                employee = Employee.objects.get(pk=employee_id)
            except Employee.DoesNotExist:
                message = "No employee with id '" + str(employee_id) + "'"
                return response.Response({'status': message},
                                         status=status.HTTP_400_BAD_REQUEST)
            work_periods = self.get_queryset().filter(employee=employee)
            try:
                latest_work_period = work_periods.order_by('-start_time')[0]
                serializer = self.get_serializer(latest_work_period)
                return response.Response(serializer.data)
            except IndexError:
                message = 'No work periods found for employee ' + str(employee)
                return response.Response({'status': message},
                                         status=status.HTTP_404_NOT_FOUND)
        else:
            employees = Employee.objects.all()
            work_periods = []
            for employee in employees:
                queryset = self.get_queryset().filter(employee=employee)
                try:
                    latest_work_period = queryset.order_by('-start_time')[0]
                    work_periods.append(latest_work_period)
                except IndexError:
                    pass
            serializer = self.get_serializer(work_periods, many=True)
            return response.Response(serializer.data)


class DayOffViewSet(DefaultViewSet):
    resource_name = 'days-off'
    serializer_class = DayOffSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = DayOffFilter
    pagination_class = pagination.PageNumberPagination
    permission_classes = (permissions.IsAuthenticated, IsManagerOrReadOnly,
                          IsNotDelete)
                              
    def get_queryset(self):
        if self.user_is_manager():
            return DayOff.objects.all()
        user_id = self.request.user.id
        return DayOff.objects.filter(employee__user__id=user_id)
    
    def create(self, request, *args, **kwargs):
        entered_by = {'type': 'users', 'id': request.user.id}
        request.data['entered_by'] = entered_by
        updated_by = {'type': 'users', 'id': request.user.id}
        request.data['updated_by'] = updated_by
        return super().create(request, *args, **kwargs)
        
    def update(self, request, *args, **kwargs):
        updated_by = {'type': 'users', 'id': request.user.id}
        request.data['updated_by'] = updated_by
        return super().update(request, *args, **kwargs)                          

    @list_route(methods=('post',),)
    def add_day_off(self, request):
        data = request.data
        days_off = []
        print(data)
        for dt in request.data['dates']:
            new_time_off = {
                'date': dateparse.parse_datetime(dt).date(),
                'day_off_type': data['day_off_type'],
                'is_paid': data['is_paid'],
                'employee': {'type': 'employees', 'id': data['employee']['id']},
                'hours': data['hours'],
                'entered_by': {'type': 'users', 'id': request.user.id},
                'updated_by': {'type': 'users', 'id': request.user.id},
            }
            
            if data['days_off_request'].get('id', None):
                new_time_off['days_off_request'] = {
                    'type': 'days-off-requests',
                    'id': data['days_off_request']['id']
                }
            days_off.append(new_time_off)
        print(days_off)
        serializer = self.get_serializer(data=days_off, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED,
                                 headers=headers
        )
        
    @list_route(methods=('post',),)
    def delete_day_off(self, request):
        data = request.data
        request_id = data['days_off_request']['id']
        DayOff.objects.filter(days_off_request=request_id).delete()

        return response.Response(status=status.HTTP_204_NO_CONTENT)
        

class DaysOffRequestViewSet(DefaultViewSet):
    resource_name = 'days-off-requests'
    serializer_class = DaysOffRequestSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = DaysOffRequestFilter
    pagination_class = pagination.PageNumberPagination
    permission_classes = (permissions.IsAuthenticated, IsNotDelete, IsOwnerOrIsManager)
    
    def get_queryset(self):
        if self.user_is_manager():
            return DaysOffRequest.objects.all()
        user_id = self.request.user.id
        return DaysOffRequest.objects.filter(employee__user__id=user_id)
        
    def create(self, request, *args, **kwargs):
        updated_by = {'type': 'users', 'id': request.user.id}
        request.data['updated_by'] = updated_by
        return super().create(request, *args, **kwargs)
        
    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        updated_by = {'type': 'users', 'id': request.user.id}
        request.data['updated_by'] = updated_by
        if not self.user_is_manager() and request.data['status'] != obj.status:
            raise exceptions.PermissionDenied 
            
        return super().update(request, *args, **kwargs)                           
    
        
class SettingsViewSet(DefaultViewSet):
    resource_name = 'user-settings'
    serializer_class = SettingsSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrReadOnly,
                          IsNotDelete)
    queryset = UserSettings.objects.all()
       

