from django.contrib import admin

from .forms import SettingsForm
from .models import Settings, Survey, InteractiveStatic, InteractiveStaticRound


class SettingsAdmin(admin.ModelAdmin):
    form = SettingsForm


# Register your models here.
admin.site.register(Settings, SettingsAdmin)
admin.site.register(InteractiveStatic)
admin.site.register(InteractiveStaticRound)
admin.site.register(Survey)
