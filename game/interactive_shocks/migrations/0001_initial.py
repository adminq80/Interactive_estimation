# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-09 01:25
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('round', '0016_auto_20161208_0154'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InteractiveShocks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_time', models.DateTimeField(null=True)),
                ('started', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='InteractiveShocksRound',
            fields=[
                ('round_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='round.Round')),
                ('influenced_guess', models.DecimalField(decimal_places=2, max_digits=3, null=True)),
                ('outcome', models.BooleanField(default=False)),
                ('following', models.ManyToManyField(related_name='shock_following', to=settings.AUTH_USER_MODEL)),
                ('game', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='interactive_shocks.InteractiveShocks')),
            ],
            bases=('round.round',),
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_users', models.PositiveSmallIntegerField()),
                ('min_users', models.PositiveSmallIntegerField()),
                ('max_following', models.PositiveSmallIntegerField()),
                ('min_following', models.PositiveSmallIntegerField()),
                ('score_lambda', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('max_rounds', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'verbose_name_plural': 'Settings',
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('game', models.CharField(blank=True, max_length=20, null=True)),
                ('age', models.PositiveSmallIntegerField(null=True)),
                ('gender', models.CharField(blank=True, max_length=30, null=True)),
                ('feedback', models.TextField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='interactiveshocks',
            name='constraints',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interactive_shocks.Settings'),
        ),
        migrations.AddField(
            model_name='interactiveshocks',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
