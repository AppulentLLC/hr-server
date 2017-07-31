from rest_framework_json_api import serializers

from .models import *
        
class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Employee
        
        
class TerminalEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'full_name')

class WorkPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = WorkPeriod

class DayOffSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = DayOff
        read_only_fields = ('entered_at',)

class DaysOffRequestSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = DaysOffRequest

class SettingsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = UserSettings
        



