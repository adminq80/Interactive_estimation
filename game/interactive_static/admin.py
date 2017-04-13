from django.contrib import admin

from .forms import SettingsForm
from .models import Settings, Survey, InteractiveStatic, InteractiveStaticRound


class SettingsAdmin(admin.ModelAdmin):
    form = SettingsForm


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    form = SettingsForm
    readonly_fields = ('id',)
    search_fields = ['id', ]
    list_display = ('max_rounds', 'max_users', 'max_following')


@admin.register(InteractiveStaticRound)
class AdminSite(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('user', 'id', 'guess', 'influenced_guess', 'outcome')
    search_fields = ['id', ]


@admin.register(Survey)
class SurveyAdminSite(admin.ModelAdmin):
    readonly_fields = ('id', 'username', 'game', 'age', 'gender', 'feedback', 'bugs', 'pay', 'education')
    list_display = ('username', 'game', 'gender')
    search_fields = ['id', 'user']


@admin.register(InteractiveStatic)
class GameAdminSite(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('id', 'start_time', 'started', 'end_time', )
    search_fields = ['id', ]

