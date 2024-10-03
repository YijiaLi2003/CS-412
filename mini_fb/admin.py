from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'email_address')
    search_fields = ('first_name', 'last_name', 'email_address', 'city')
