# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-25 01:15
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactive', '0029_auto_20161024_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='max_rounds',
            field=models.PositiveSmallIntegerField(default=30, validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=False,
        ),
    ]
