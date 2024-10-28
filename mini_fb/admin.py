from django.contrib import admin
from .models import Friend, Profile, StatusMessage

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'email_address')
    search_fields = ('first_name', 'last_name', 'email_address', 'city')

@admin.register(StatusMessage)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'timestamp', 'message')
    search_fields = ('message', 'profile__first_name', 'profile__last_name')
    list_filter = ('profile', 'timestamp')


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile1', 'profile2', 'timestamp')
    search_fields = ('profile1__first_name', 'profile1__last_name', 'profile2__first_name', 'profile2__last_name')
