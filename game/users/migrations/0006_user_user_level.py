# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-30 00:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_level',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
