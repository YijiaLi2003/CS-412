# gaming/admin.py

"""
Django Admin Configuration for the Gaming Application.

This module registers models with the Django admin site and customizes their admin interfaces
to enhance usability and provide better data management capabilities.

Models Registered:
- Genre
- Platform
- Game
- Profile
- Friend
- Image
- FeedItem
- StatusMessage
- Progress
- Comment
- Like

Each admin class customizes the list display, search fields, filters, and other functionalities
specific to the model it represents.
"""

from django.contrib import admin
from django.shortcuts import render
from .models import (
    Genre, Game, Platform, Progress,
    Profile, Friend, StatusMessage, Image, FeedItem, Comment, Like
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """
    Admin interface for the Genre model.
    
    Displays the name of each genre in the list view.
    """
    list_display = ('name',)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    """
    Admin interface for the Platform model.
    
    Displays the name of each platform in the list view.
    """
    list_display = ('name',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Admin interface for the Game model.
    
    Displays key fields including title, associated platforms, genre, release date, developer, and publisher.
    Provides filtering by genre and platforms, and search functionality by title, developer, and publisher.
    """
    list_display = ('title', 'get_platforms', 'genre', 'release_date', 'developer', 'publisher')
    list_filter = ('genre', 'platforms')
    search_fields = ('title', 'developer', 'publisher')
    filter_horizontal = ('platforms',)

    def get_platforms(self, obj):
        """
        Retrieves and concatenates all platform names associated with a game.
        
        Args:
            obj (Game): The game instance.
        
        Returns:
            str: A comma-separated string of platform names.
        """
        return ", ".join([platform.name for platform in obj.platforms.all()])

    get_platforms.short_description = 'Platforms'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for the Profile model.
    
    Displays first name, last name, city, and email address in the list view.
    Provides search functionality by first name, last name, email address, and city.
    """
    list_display = ('first_name', 'last_name', 'city', 'email_address')
    search_fields = ('first_name', 'last_name', 'email_address', 'city')


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    """
    Admin interface for the Friend model.
    
    Displays both profiles involved in the friendship and the timestamp of when the friendship was established.
    Provides search functionality by first and last names of both profiles.
    """
    list_display = ('profile1', 'profile2', 'timestamp')
    search_fields = (
        'profile1__first_name', 'profile1__last_name',
        'profile2__first_name', 'profile2__last_name'
    )


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    """
    Admin interface for the Image model.
    
    Displays the associated status message, timestamp, and image file.
    Provides search functionality by the content of the status message and filtering by timestamp.
    """
    list_display = ('status_message', 'timestamp', 'image_file')
    search_fields = ('status_message__message',)
    list_filter = ('timestamp',)


@admin.register(FeedItem)
class FeedItemAdmin(admin.ModelAdmin):
    """
    Admin interface for the FeedItem model.
    
    Displays the user, content type, object ID, and timestamp.
    Provides filtering by content type and timestamp.
    Enables search by username, status message content, and game title.
    """
    list_display = ['user', 'content_type', 'object_id', 'timestamp']
    list_filter = ['content_type', 'timestamp']
    search_fields = [
        'user__username',
        'content_object__message',
        'content_object__game__title'
    ]


@admin.register(StatusMessage)
class StatusMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for the StatusMessage model.
    
    Displays the associated profile, message content, and timestamp.
    Provides filtering by timestamp and search functionality by profile names and message content.
    """
    list_display = ['profile', 'message', 'timestamp']
    list_filter = ['timestamp']
    search_fields = [
        'profile__first_name',
        'profile__last_name',
        'message'
    ]


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    """
    Admin interface for the Progress model.
    
    Displays user, game, platform, completion status, hours played, achievements, rating, and timestamp.
    Provides filtering by game, platform, completion status, rating, and timestamp.
    Enables search by username, game title, platform name, and notes.
    """
    list_display = [
        'user', 'game', 'platform', 'completion_status',
        'hours_played', 'achievements', 'rating', 'timestamp'
    ]
    list_filter = [
        'game', 'platform', 'completion_status', 'rating', 'timestamp'
    ]
    search_fields = [
        'user__username',
        'game__title',
        'platform__name',
        'notes'
    ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for the Comment model.
    
    Displays the username of the commenter, the related content object, a truncated version of the comment content, and the timestamp.
    Provides filtering by timestamp and profile, and search functionality by username, comment content, and profile names.
    Includes custom admin actions for deleting selected comments and deleting all comments (restricted to superusers).
    """
    list_display = ('get_username', 'content_object', 'short_content', 'timestamp')
    list_filter = ('timestamp', 'profile')
    search_fields = [
        'profile__user__username',
        'content',
        'profile__first_name',
        'profile__last_name'
    ]
    actions = ['delete_selected', 'delete_all_comments']
    readonly_fields = ('timestamp',)

    def get_username(self, obj):
        """
        Retrieves the username of the commenter from the related Profile.
        
        Args:
            obj (Comment): The comment instance.
        
        Returns:
            str: The username of the commenter.
        """
        return obj.profile.user.username

    get_username.short_description = 'User'
    get_username.admin_order_field = 'profile__user__username'

    def short_content(self, obj):
        """
        Returns a truncated version of the comment content for display.
        
        Args:
            obj (Comment): The comment instance.
        
        Returns:
            str: A truncated string of the comment content.
        """
        return (obj.content[:75] + '...') if len(obj.content) > 75 else obj.content

    short_content.short_description = 'Content'

    def delete_all_comments(self, request, queryset):
        """
        Custom admin action to delete all comments in the database.
        
        Args:
            request (HttpRequest): The HTTP request object.
            queryset (QuerySet): The queryset of comments to delete.
        
        Returns:
            HttpResponse: A rendered confirmation page or a redirect after deletion.
        """
        if 'apply' in request.POST:
            # User has confirmed the deletion
            count, _ = Comment.objects.all().delete()
            self.message_user(request, f"Successfully deleted {count} comments.")
            return
        return render(request, 'admin/delete_all_comments_confirmation.html')

    delete_all_comments.short_description = "Delete ALL Comments"

    def get_actions(self, request):
        """
        Overrides the default get_actions to restrict certain actions based on user permissions.
        
        Args:
            request (HttpRequest): The HTTP request object.
        
        Returns:
            dict: The available admin actions.
        """
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            # Remove the 'delete_all_comments' action for non-superusers
            if 'delete_all_comments' in actions:
                del actions['delete_all_comments']
        return actions
