# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-06 19:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20170302_0133'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='score',
            field=models.SmallIntegerField(default=0),
        ),
    ]
