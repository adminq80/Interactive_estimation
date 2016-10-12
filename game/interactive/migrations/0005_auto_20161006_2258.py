# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-06 22:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('interactive', '0004_interactiveround_influenced_guess'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interactiveround',
            name='influencers',
        ),
        migrations.AddField(
            model_name='interactiveround',
            name='followers',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='interactiveround',
            name='following',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL),
        ),
    ]