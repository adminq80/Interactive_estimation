# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-11 02:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20160825_0458'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='game_type',
            field=models.CharField(choices=[('c', 'Control'), ('i', 'Interactive')], default='c', max_length=10, verbose_name='User Type'),
            preserve_default=False,
        ),
    ]
