# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 19:33
from __future__ import unicode_literals

from django.db import migrations, models
import frontend.models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='desired_state',
            field=models.CharField(default=frontend.models.AppStates('enabled'), max_length=128),
        ),
    ]
