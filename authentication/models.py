from django.db import models
from django.contrib.auth.models import User

# Create your models here.

hr_roles = (
    ('e', 'Employee'),
    ('m', 'Manager'),
    ('a', 'Admin'),
    ('t', 'Timeclock'),
)

class Privileges(models.Model):
    user = models.OneToOneField(User)
    hr_role = models.CharField('HR Role', choices=hr_roles, max_length=1, 
                               default='e')
    is_global_admin = models.BooleanField('Is Global Admin?', default=False)
    
    def __str__(self):
        return '{} ( {} )'.format(self.user, self.hr_role)
        
    class Meta:
        verbose_name_plural = 'Priveleges'

