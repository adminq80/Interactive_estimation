# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-25 01:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interactive', '0004_auto_20160925_0129'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RoundInteractive',
            new_name='InteractiveRound',
        ),
    ]
