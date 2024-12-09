# gaming/admin.py
from django.contrib import admin
from .models import (
    Genre, Game, Progress,
    Profile, Friend, StatusMessage, Image
)

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

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'email_address')
    search_fields = ('first_name', 'last_name', 'email_address', 'city')

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile1', 'profile2', 'timestamp')
    search_fields = ('profile1__first_name', 'profile1__last_name', 'profile2__first_name', 'profile2__last_name')

@admin.register(StatusMessage)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'timestamp', 'message')
    search_fields = ('message', 'profile__first_name', 'profile__last_name')
    list_filter = ('profile', 'timestamp')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('status_message', 'timestamp', 'image_file')
    search_fields = ('status_message__message',)
    list_filter = ('timestamp',)
