from django.contrib import admin
from .models import Control, Survey, Setting


@admin.register(Control)
class ControlAdminSite(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Setting)
admin.site.register(Survey)
