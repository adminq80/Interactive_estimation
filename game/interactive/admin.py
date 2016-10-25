from django import forms
from django.contrib import admin

from .forms import SettingsForm
from .models import Settings, Survey, Interactive, InteractiveRound


class SettingsAdmin(admin.ModelAdmin):
    form = SettingsForm


# Register your models here.
admin.site.register(Settings, SettingsAdmin)
admin.site.register(Interactive)
admin.site.register(InteractiveRound)
admin.site.register(Survey)
