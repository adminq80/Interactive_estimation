# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-25 02:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interactive', '0008_auto_20160925_0207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interactive',
            name='constraints',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='interactive.Settings'),
        ),
    ]