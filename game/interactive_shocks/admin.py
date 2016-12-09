from django.contrib import admin

from .forms import SettingsForm
from .models import Settings, Survey, InteractiveShocks, InteractiveShocksRound


class SettingsAdmin(admin.ModelAdmin):
    form = SettingsForm


# Register your models here.
admin.site.register(Settings, SettingsAdmin)
admin.site.register(InteractiveShocks)
admin.site.register(InteractiveShocksRound)
admin.site.register(Survey)
