from django.contrib import admin
from .models import Control, Survey, Setting


@admin.register(Control)
class AdminSite(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('user', 'id')
    search_fields = ['id']


@admin.register(Survey)
class SurveyAdminSite(admin.ModelAdmin):
    readonly_fields = ('id', 'user', 'game', 'age', 'gender', 'feedback', 'bugs', 'pay', 'education')
    list_display = ('user', 'game', 'gender')
    search_fields = ['id', 'user']


@admin.register(Setting)
class SettingsAdminSite(admin.ModelAdmin):
    readonly_fields = ('id',)
    search_fields = ['id']
    list_display = ('max_rounds', 'types')
