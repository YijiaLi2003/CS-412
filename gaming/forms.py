# gaming/forms.py

from django import forms
from django.forms.widgets import ClearableFileInput, CheckboxSelectMultiple
from django.core.exceptions import ValidationError
from django.forms.widgets import FileInput, CheckboxSelectMultiple
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
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'profile_image']
        exclude = ['user']

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['city', 'email_address', 'profile_image']


class CreateStatusMessageForm(forms.ModelForm):
    class Meta:
        model = StatusMessage
        fields = ['message']  # Only the message field
    class Meta:
        model = StatusMessage
        fields = ['message']  # Ensure 'images' is NOT here

    def clean_images(self):
        images = self.files.getlist('images')
        for image in images:
            if not image.content_type.startswith('image/'):
                raise ValidationError(f"{image.name} is not a valid image file.")
            if image.size > 5 * 1024 * 1024:  # Limit to 5MB
                raise ValidationError(f"{image.name} exceeds the 5MB size limit.")
        return images

class UpdateStatusMessageForm(forms.ModelForm):
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
        super(UpdateStatusMessageForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['delete_images'].queryset = self.instance.images.all()

class GameSearchForm(forms.Form):
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
            'placeholder': 'Release Year'
        })
    )

class GameForm(forms.ModelForm):
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
    class Meta:
        model = Progress
        fields = ['game', 'platform', 'completion_status', 'hours_played', 'achievements', 'rating', 'notes']
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
        game = kwargs.pop('game', None)
        super().__init__(*args, **kwargs)
        if game:
            self.fields['game'].initial = game
            # Limit platform choices to the game's available platforms
            self.fields['platform'].queryset = game.platforms.all()

class CommentForm(forms.ModelForm):
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
