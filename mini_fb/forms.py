# forms.py

from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Profile, StatusMessage, Image

class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'profile_image_url']

class CreateStatusMessageForm(forms.ModelForm):
    class Meta:
        model = StatusMessage
        fields = ['message']

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['city', 'email_address', 'profile_image_url'] 

class UpdateStatusMessageForm(forms.ModelForm):
    delete_images = forms.ModelMultipleChoiceField(
        queryset=Image.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Select images to delete"
    )

    class Meta:
        model = StatusMessage
        fields = ['message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delete_images'].queryset = self.instance.images.all()