# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-24 20:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactive', '0028_auto_20161021_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interactiveround',
            name='influenced_guess',
            field=models.DecimalField(decimal_places=2, max_digits=3, null=True),
        ),
    ]