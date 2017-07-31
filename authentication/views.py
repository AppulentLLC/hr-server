import random

from django.shortcuts import render
from rest_framework import exceptions, filters, permissions, status, response
from rest_framework import parsers, renderers, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework_json_api.parsers import JSONParser as JSONAPIParser
from rest_framework_json_api.renderers import JSONRenderer as JSONAPIRenderer
from rest_framework_json_api import pagination

from oauth2_provider.models import Application

from .filters import *
from .models import *
from .permissions import *
from .serializers import *

# Create your views here.

class ApplicationViewSet(viewsets.ModelViewSet):
    resource_name = 'applications'
    serializer_class = ApplicationSerializer
    queryset = Application.objects.all()
    permission_classes = (ReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ApplicationFilter
    
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
        
class UserViewSet(DefaultViewSet):
    #resource_name = 'users'
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = UserFilter
    permission_classes = (permissions.IsAuthenticated, IsManagerOrNotCreate,
                          IsNotDelete)
    
    def get_queryset(self):
        if self.user_is_manager():
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
        
    def create(self, request, *args, **kwargs):
        username = request.data['username']
        request.data['password'] = str(random.randint(100000, 999999))
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        request_allowed = False
        instance = self.get_object()
        if request.user == instance:
            request_allowed = True
        else:
            if request.user.privileges.hr_role == 'm':
                if instance.privileges.hr_role == 'e':
                    request_allowed = True
            if request.user.privileges.hr_role == 'a':
                if instance.privileges.hr_role in ['e', 'm', 't']:
                    request_allowed = True
            if request.user.privileges.is_global_admin:
                request_allowed = not instance.privileges.is_global_admin
        if request_allowed:
            return super().update(request, *args, **kwargs)
        raise exceptions.PermissionDenied
    
class PrivilegesViewSet(DefaultViewSet):
    resource_name = 'privileges'
    serializer_class = PrivilegesSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = PrivilegesFilter
    permission_classes = (permissions.IsAuthenticated, IsManagerOrReadOnly,
                          IsNotDelete)
    queryset = Privileges.objects.all()

    def check_params(self, request):
        instance = None
        data = request.data
        if request.method in ('PUT', 'PATCH'):
            instance = self.get_object()
        user = getattr(self.request, 'user', None)
        privileges = getattr(user, 'privileges', None)
        
        if 'is_global_admin' in data.keys(): 
            if instance is not None:
                if data['is_global_admin'] != instance.is_global_admin:
                    return False
            else:
                if data['is_global_admin'] == True:
                    return False
                    
        if privileges.is_global_admin == True:
            if request.method == 'POST' and data['is_global_admin'] == True:
                return False
            else:
                return True

        if instance is not None:
            if instance.is_global_admin:
                return False
            if (privileges.hr_role in ['m', 'a', 'e', 't']
                        and instance.hr_role == 'a'):
                return False
            if (privileges.hr_role in ['m', 'e', 't']
                        and instance.hr_role in ['a', 'm', 't']):
                return False
        
        requested_hr_role = data.get('hr_role', None)
        if requested_hr_role == 'a':
            return False
        if privileges.hr_role is not 'a':
            if requested_hr_role  in ['a', 'm', 't']:
                return False
        if privileges.hr_role in ['e', 't']:
            if requested_hr_role  in ['a', 'm', 'e', 't']:
                return False
        
        return True

    def create(self, request, *args, **kwargs):
        if self.check_params(request):
            return super().create(request, *args, **kwargs)
        raise exceptions.PermissionDenied
        
    def update(self, request, *args, **kwargs):
        if self.check_params(request):
            return super().update(request, *args, **kwargs)
        raise exceptions.PermissionDenied
