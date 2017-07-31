from datetime import datetime

from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from localflavor.us.models import USZipCodeField, USStateField

# Create your models here.
SSNValidator = RegexValidator(
    regex=r'^\d{3}-\d{2}-\d{4}$',
    message='Please enter an SSN in the format `999-99-9999`')
                   
PhoneValidator = RegexValidator(
    regex=r'^\(\d{3}\)\d{3}-\d{4}$',
    message='Please enter a phone in the format `(999)999-9999`')

DAY_OFF_TYPES = (
    ('hy', 'Holiday'),
    ('vn', 'Vacation'),
    ('pl', 'Personal'),
)

class Employee(models.Model):
    user = models.OneToOneField(User)
    payroll_id = models.CharField(max_length=25, null=True, blank=True)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    ssn = models.CharField(max_length=11, null=True, blank=True, unique=True,
                           validators=[SSNValidator])
    primary_phone = models.CharField(max_length=13, validators=[PhoneValidator])
    secondary_phone = models.CharField(max_length=13, null=True, blank=True,
                                       validators=[PhoneValidator])
    address_street = models.CharField('Street address', max_length=40)
    address_secondary = models.CharField('Secondary address', max_length=25,
                                         null=True, blank=True)
    city = models.CharField(max_length=25)
    state = USStateField()
    postal_code = USZipCodeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, related_name='employee_creates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, related_name='employee_updates')
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)
        
    def full_name(self):
        return str(self)
        
    def owner(self):
        return self.user
        
class WorkPeriod(models.Model):
    employee = models.ForeignKey(Employee, related_name='work_periods')
    start_time = models.DateTimeField(blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    adjustment = models.IntegerField(null=True, blank=True)
    note = models.CharField(max_length=60, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)

    def owner(self):
        return self.employee.user
      
class DayOff(models.Model):
    employee = models.ForeignKey(Employee, related_name='days_off')
    days_off_request = models.ForeignKey('DaysOffRequest', null=True, 
                                         blank=True)
    date = models.DateField()
    hours = models.IntegerField()
    day_off_type = models.CharField(max_length=2, choices=DAY_OFF_TYPES)
    is_paid = models.BooleanField(default=True)
    note = models.CharField(max_length=120, null=True, blank=True)
    entered_by = models.ForeignKey(User, related_name='day_off_creates')
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, related_name='day_off_updates')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Days off'
    
    def owner(self):
        return self.employee.user
        
class DaysOffRequest(models.Model):
    employee = models.ForeignKey(Employee)
    start_date = models.DateField()
    end_date = models.DateField()
    request_type = models.CharField(max_length=2, choices=DAY_OFF_TYPES)
    is_paid = models.BooleanField(default=True)
    status = models.CharField(max_length=10, default='Pending')
    note = models.CharField(max_length=250, null=True, blank=True)
    seen = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Days off requests'
    
    def owner(self):
        return self.employee.user
      
class UserSettings(models.Model):
    user = models.OneToOneField(User, null=True, blank=True)
    summary_text = models.CharField(max_length=250,null=True, blank=True)
    summary_weeks = models.IntegerField(null=True, blank=True)
    summary_view = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'User settings'
    
