from django.contrib import admin
from .models import Control, Survey, Setting


admin.site.register(Setting)
admin.site.register(Control)
admin.site.register(Survey)
