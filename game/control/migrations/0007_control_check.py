# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-11 03:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0006_auto_20161005_0418'),
    ]

    operations = [
        migrations.AddField(
            model_name='control',
            name='check',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
