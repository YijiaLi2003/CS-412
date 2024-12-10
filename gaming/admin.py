# gaming/admin.py

from django.contrib import admin
from django.shortcuts import render
from .models import (
    Genre, Game, Platform, Progress,
    Profile, Friend, StatusMessage, Image, FeedItem, Comment, Like
)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_platforms', 'genre', 'release_date', 'developer', 'publisher')
    list_filter = ('genre', 'platforms')
    search_fields = ('title', 'developer', 'publisher')
    filter_horizontal = ('platforms',)  

    def get_platforms(self, obj):
        """Retrieve and join all platform names for display."""
        return ", ".join([platform.name for platform in obj.platforms.all()])
    get_platforms.short_description = 'Platforms'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'email_address')
    search_fields = ('first_name', 'last_name', 'email_address', 'city')

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile1', 'profile2', 'timestamp')
    search_fields = ('profile1__first_name', 'profile1__last_name', 'profile2__first_name', 'profile2__last_name')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('status_message', 'timestamp', 'image_file')
    search_fields = ('status_message__message',)
    list_filter = ('timestamp',)

@admin.register(FeedItem)
class FeedItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'object_id', 'timestamp']
    list_filter = ['content_type', 'timestamp']
    search_fields = ['user__username', 'content_object__message', 'content_object__game__title']

@admin.register(StatusMessage)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ['profile', 'message', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['profile__first_name', 'profile__last_name', 'message']

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'platform', 'completion_status', 'hours_played', 'achievements', 'rating', 'timestamp']
    list_filter = ['game', 'platform', 'completion_status', 'rating', 'timestamp']
    search_fields = ['user__username', 'game__title', 'platform__name', 'notes']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'content_object', 'short_content', 'timestamp')
    list_filter = ('timestamp', 'profile')
    search_fields = ('profile__user__username', 'content', 'profile__first_name', 'profile__last_name')
    
    actions = ['delete_selected', 'delete_all_comments']
    
    readonly_fields = ('timestamp',)
    
    def get_username(self, obj):
        """Display the username from the related Profile."""
        return obj.profile.user.username
    get_username.short_description = 'User'
    get_username.admin_order_field = 'profile__user__username'
    
    def short_content(self, obj):
        """Display a truncated version of the comment content."""
        return (obj.content[:75] + '...') if len(obj.content) > 75 else obj.content
    short_content.short_description = 'Content'
    
    def delete_all_comments(self, request, queryset):
        """
        Custom admin action to delete all comments.
        """
        if 'apply' in request.POST:
            # User has confirmed the deletion
            count, _ = Comment.objects.all().delete()
            self.message_user(request, f"Successfully deleted {count} comments.")
            return
        return render(request, 'admin/delete_all_comments_confirmation.html')
    
    delete_all_comments.short_description = "Delete ALL Comments"
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            # Remove the 'delete_all_comments' action for non-superusers
            if 'delete_all_comments' in actions:
                del actions['delete_all_comments']
        return actions
