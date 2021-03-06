# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-20 23:13
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20161209_0125'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('types', models.CharField(max_length=1000, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z', 32), code='invalid', message='Enter only digits separated by commas.')])),
            ],
            options={
                'verbose_name_plural': 'UserTypes',
            },
        ),
    ]
