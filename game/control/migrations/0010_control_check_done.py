# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-11 04:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0009_auto_20161011_0404'),
    ]

    operations = [
        migrations.AddField(
            model_name='control',
            name='check_done',
            field=models.BooleanField(default=False),
        ),
    ]
