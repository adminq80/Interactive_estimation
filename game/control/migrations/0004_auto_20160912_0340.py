# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-12 03:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0003_auto_20160911_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='control',
            name='score',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='control',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]