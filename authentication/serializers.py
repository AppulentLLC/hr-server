from rest_framework_json_api import serializers
from oauth2_provider.models import Application

from .models import *

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        resource_name = 'users'
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user
        
    def update(self, instance, validated_data):
        # raise_errors_on_nested_writes('update', self, validated_data)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class PrivilegesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Privileges
        fields = '__all__'
        
class ApplicationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Application
        fields = ('id', 'name', 'client_id', 'client_secret')
