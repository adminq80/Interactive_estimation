# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-08 01:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('round', '0015_auto_20161105_2340'),
    ]

    operations = [
        migrations.AddField(
            model_name='plot',
            name='non_stationary_seq',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='plot',
            name='seq',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='plot',
            name='stationary_seq',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='plot',
            name='plot',
            field=models.URLField(unique=True),
        ),
    ]