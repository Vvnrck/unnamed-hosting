# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-17 20:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0004_auto_20170217_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logrequest',
            name='app',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='frontend.App'),
        ),
    ]
