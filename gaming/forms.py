# gaming/forms.py

"""
Django Forms for the Gaming Application.

This module defines various forms used in the application for creating and updating models,
performing searches, and handling user interactions.

Forms Included:
- CreateProfileForm
- UpdateProfileForm
- CreateStatusMessageForm
- UpdateStatusMessageForm
- GameSearchForm
- GameForm
- ProgressForm
- CommentForm
- FriendsProgressFilterForm
"""

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import (
    ClearableFileInput,
    CheckboxSelectMultiple,
    FileInput
)
from .models import (
    Profile, 
    StatusMessage, 
    Image, 
    Platform, 
    Game, 
    Genre, 
    Progress, 
    Comment
)


class CreateProfileForm(forms.ModelForm):
    """
    Form for creating a new user profile.
    
    Excludes the user field as it will be associated with the logged-in user upon creation.
    """
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'profile_image']
        exclude = ['user']


class UpdateProfileForm(forms.ModelForm):
    """
    Form for updating an existing user profile.
    
    Allows updating of city, email address, and profile image.
    """
    class Meta:
        model = Profile
        fields = ['city', 'email_address', 'profile_image']


class CreateStatusMessageForm(forms.ModelForm):
    """
    Form for creating a new status message with optional image uploads.
    
    Validates that uploaded files are images and do not exceed the size limit.
    """
    class Meta:
        model = StatusMessage
        fields = ['message']  

    def clean_images(self):
        """
        Validates uploaded images to ensure they are of correct type and size.
        
        Raises:
            ValidationError: If any uploaded file is not an image or exceeds 5MB.
        
        Returns:
            list: A list of validated image files.
        """
        images = self.files.getlist('images')
        for image in images:
            if not image.content_type.startswith('image/'):
                raise ValidationError(f"{image.name} is not a valid image file.")
            if image.size > 5 * 1024 * 1024: 
                raise ValidationError(f"{image.name} exceeds the 5MB size limit.")
        return images


class UpdateStatusMessageForm(forms.ModelForm):
    """
    Form for updating an existing status message.
    
    Allows updating of the message content and deletion of associated images.
    """
    delete_images = forms.ModelMultipleChoiceField(
        queryset=Image.objects.none(),
        required=False,
        widget=CheckboxSelectMultiple,
        label='Delete Images'
    )

    class Meta:
        model = StatusMessage
        fields = ['message', 'delete_images']

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and sets the queryset for delete_images based on the instance.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(UpdateStatusMessageForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['delete_images'].queryset = self.instance.images.all()


class GameSearchForm(forms.Form):
    """
    Form for searching games based on name, platform, and release year.
    
    All fields are optional to allow flexible search queries.
    """
    q = forms.CharField(
        required=False, 
        label='Game Name', 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Search by name'
        })
    )
    platform = forms.ModelChoiceField(
        required=False, 
        queryset=Platform.objects.all(), 
        label='Platform', 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    release_year = forms.IntegerField(
        required=False, 
        label='Release Year', 
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Year'
        })
    )


class GameForm(forms.ModelForm):
    """
    Form for creating or updating a Game instance.
    
    Utilizes customized widgets for better UI/UX, including checkbox selection for platforms
    and date input for release date.
    """
    class Meta:
        model = Game
        fields = ['title', 'platforms', 'genre', 'release_date', 'developer', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'platforms': forms.CheckboxSelectMultiple(),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'developer': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProgressForm(forms.ModelForm):
    """
    Form for creating or updating a Progress instance.
    
    Dynamically filters platform choices based on the selected game to ensure consistency.
    """
    class Meta:
        model = Progress
        fields = [
            'game', 'platform', 'completion_status', 
            'hours_played', 'achievements', 'rating', 'notes'
        ]
        widgets = {
            'completion_status': forms.Select(attrs={'class': 'form-control'}),
            'game': forms.Select(attrs={'class': 'form-control'}),
            'platform': forms.Select(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hours_played': forms.NumberInput(attrs={'class': 'form-control'}),
            'achievements': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and filters platform choices based on the provided game.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. Expects 'game' to filter platforms.
        """
        game = kwargs.pop('game', None)
        super().__init__(*args, **kwargs)
        if game:
            self.fields['game'].initial = game
            self.fields['platform'].queryset = game.platforms.all()


class CommentForm(forms.ModelForm):
    """
    Form for creating a new Comment.
    
    Utilizes a textarea widget with placeholder text for better user experience.
    """
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write a comment...',
            'rows': 2,
            'required': True
        })
    )

    class Meta:
        model = Comment
        fields = ['content']


class FriendsProgressFilterForm(forms.Form):
    """
    Form for filtering friends' progress entries based on completion status, platform, and specific friend.
    
    Dynamically populates the friend choices based on the logged-in user's friends.
    """
    completion_status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All'),
            ('Not Started', 'Not Started'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed'),
            ('Wishlist', 'Wishlist'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    platform = forms.ModelChoiceField(
        required=False,
        queryset=Platform.objects.all(),
        empty_label="All Platforms",
        label='Platform',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    friend = forms.ModelChoiceField(
        required=False,
        queryset=Profile.objects.none(),  
        empty_label="All Friends",
        label='Friend',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and sets the queryset for the friend field based on the user's profile.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. Expects 'user_profile' to populate friends.
        """
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        if user_profile:
            self.fields['friend'].queryset = user_profile.get_friends()
