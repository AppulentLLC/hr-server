from django.contrib import admin
from django.contrib.auth.models import User

from .models import *

# Register your models here.
#admin.site.register(Employee)
#admin.site.register(WorkPeriod)
#admin.site.register(Message)


   
class WorkPeriodInline(admin.StackedInline):
    model = WorkPeriod
    ordering = ('-start_time',)
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'primary_phone')
    inlines = (WorkPeriodInline,)
    

@admin.register(WorkPeriod)
class WorkPeriodAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_time', 'end_time')
    ordering = ('-start_time',)

@admin.register(DayOff)
class DayOffAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'hours', 'day_off_type', 'is_paid')
    ordering = ('-date',)

@admin.register(DaysOffRequest)
class DaysOffRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'request_type',
                    'is_paid')
    ordering = ('-requested_at',)


admin.site.register(UserSettings)
