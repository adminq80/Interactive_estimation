# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-07 18:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactive_static', '0002_auto_20170307_0112'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='bugs',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='education',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='pay',
            field=models.TextField(null=True),
        ),
    ]