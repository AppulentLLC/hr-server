# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-22 11:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dayoff',
            name='days_off_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hr.DaysOffRequest'),
        ),
    ]
