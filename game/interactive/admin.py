from django.contrib import admin

from .models import Settings, Interactive, InteractiveRound


# Register your models here.
admin.site.register(Settings)
admin.site.register(Interactive)
admin.site.register(InteractiveRound)
