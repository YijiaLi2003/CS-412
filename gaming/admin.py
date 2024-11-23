from django.contrib import admin
from .models import Genre, Game, Progress

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'genre', 'release_date', 'developer', 'publisher')
    list_filter = ('genre', 'platform')
    search_fields = ('title', 'developer', 'publisher')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'completion_status', 'hours_played', 'achievements', 'rating')
    list_filter = ('completion_status', 'game', 'user')
    search_fields = ('user__username', 'game__title')
