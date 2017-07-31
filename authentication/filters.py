from django.contrib.auth.models import User
from oauth2_provider.models import Application
import django_filters

from .models import *

class UserFilter(django_filters.FilterSet):
    username_contains = django_filters.CharFilter(name='username',
                                                  lookup_expr=('contains',))
    
    class Meta:
        model = User
        fields = ('username', 'username_contains')
        
class PrivilegesFilter(django_filters.FilterSet):

    class Meta:
        model = Privileges
        fields = ('user',)
        
class ApplicationFilter(django_filters.FilterSet):

    class Meta:
        model = Application
        fields = ('name',)
