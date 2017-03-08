# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-01 05:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactive_shocks', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interactiveshocks',
            options={'verbose_name_plural': 'Interactive Shocks'},
        ),
        migrations.AddField(
            model_name='settings',
            name='kickout_seconds',
            field=models.PositiveSmallIntegerField(default=60),
        ),
        migrations.AddField(
            model_name='settings',
            name='prompt_seconds',
            field=models.PositiveSmallIntegerField(default=60),
        ),
    ]
