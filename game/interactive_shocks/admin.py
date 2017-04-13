from django.contrib import admin

from .forms import SettingsForm
from .models import Settings, Survey, InteractiveShocks, InteractiveShocksRound


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    form = SettingsForm
    readonly_fields = ('id',)
    search_fields = ['id', ]
    list_display = ('max_rounds', 'max_users', 'max_following')


@admin.register(InteractiveShocksRound)
class AdminSite(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('user', 'guess', 'influenced_guess', 'outcome')
    search_fields = ['user', 'guess', 'influenced_guess']


@admin.register(Survey)
class SurveyAdminSite(admin.ModelAdmin):
    readonly_fields = ('id', 'username', 'game', 'age', 'gender', 'feedback', 'bugs', 'pay', 'education')
    list_display = ('username', 'game', 'gender')
    search_fields = ['id', 'user']


@admin.register(InteractiveShocks)
class GameAdminSite(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('id', 'start_time', 'started', 'end_time', )
    search_fields = ['id', ]
