# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-11 04:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0007_control_check'),
    ]

    operations = [
        migrations.AlterField(
            model_name='control',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, unique=True),
        ),
    ]