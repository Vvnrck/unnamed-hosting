# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-08 15:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_auto_20170206_1933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='app',
            name='container_id',
        ),
        migrations.RemoveField(
            model_name='app',
            name='db_pass',
        ),
        migrations.RemoveField(
            model_name='app',
            name='db_user',
        ),
        migrations.RemoveField(
            model_name='app',
            name='image_id',
        ),
    ]
