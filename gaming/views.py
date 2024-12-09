# gaming/views.py

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import (
    Genre, Game, Progress,
    Profile, Friend, StatusMessage, Image
)
from .forms import (
    CreateProfileForm, CreateStatusMessageForm,
    UpdateProfileForm, UpdateStatusMessageForm
)

class GenreListView(ListView):
    model = Genre
    template_name = 'gaming/genre_list.html'
    context_object_name = 'genres'

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'gaming/genre_detail.html'
    context_object_name = 'genre'

class GameListView(ListView):
    model = Game
    template_name = 'gaming/game_list.html'
    context_object_name = 'games'

class GameDetailView(DetailView):
    model = Game
    template_name = 'gaming/game_detail.html'
    context_object_name = 'game'

class ProgressListView(LoginRequiredMixin, ListView):
    model = Progress
    template_name = 'gaming/progress_list.html'
    context_object_name = 'progress_entries'
    paginate_by = 10  # Optional

    def get_queryset(self):
        return Progress.objects.filter(user=self.request.user).select_related('game')

class ProgressDetailView(LoginRequiredMixin, DetailView):
    model = Progress
    template_name = 'gaming/progress_detail.html'
    context_object_name = 'progress_entry'

# Social Feature Views

class ProfileOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        profile = self.get_object()
        return profile.user == self.request.user

class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'gaming/show_all_profiles.html'  
    context_object_name = 'profiles'

class ShowProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'gaming/profile_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_form'] = CreateStatusMessageForm()
        context['friends'] = self.object.get_friends()
        return context

class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'gaming/create_profile_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None 
        form = self.get_form()
        user_form = UserCreationForm(self.request.POST)

        if form.is_valid() and user_form.is_valid():
            return self.form_valid(form, user_form)
        else:
            return self.form_invalid(form, user_form)

    def form_valid(self, form, user_form):
        user = user_form.save()
        form.instance.user = user
        username = user_form.cleaned_data.get('username')
        raw_password = user_form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        messages.success(self.request, "Profile created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form, user_form):
        return self.render_to_response(self.get_context_data(form=form, user_form=user_form))

    def get_success_url(self):
        return reverse('gaming:profile-detail', kwargs={'pk': self.object.pk})

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'gaming/update_profile_form.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.gaming_profile  # Updated to use related_name

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('gaming:profile-detail', kwargs={'pk': self.object.pk})

class DeleteStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = StatusMessage
    template_name = 'gaming/delete_status_form.html'
    context_object_name = 'status_message'

    def test_func(self):
        status_message = self.get_object()
        return status_message.profile.user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Status message deleted successfully!")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        profile_pk = self.object.profile.pk
        return reverse('gaming:profile-detail', kwargs={'pk': profile_pk})

class UpdateStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'gaming/update_status_form.html'
    context_object_name = 'status_message'

    def test_func(self):
        status_message = self.get_object()
        return status_message.profile.user == self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        sm = self.object 

        images_to_delete = form.cleaned_data.get('delete_images')
        if images_to_delete:
            images_to_delete.delete()

        messages.success(self.request, "Status message updated successfully!")
        return response

    def get_success_url(self):
        return reverse('gaming:profile-detail', kwargs={'pk': self.object.profile.pk})

class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'gaming/create_status_form.html'

    def form_valid(self, form):
        profile = self.request.user.gaming_profile  # Updated to use related_name
        form.instance.profile = profile

        response = super().form_valid(form)
        sm = self.object

        files = self.request.FILES.getlist('images')
        for f in files:
            Image.objects.create(image_file=f, status_message=sm)

        messages.success(self.request, "Status message posted successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.gaming_profile  # Updated to use related_name
        return context

    def get_success_url(self):
        return reverse('gaming:profile-detail', kwargs={'pk': self.object.profile.pk})

class CreateFriendView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        other_pk = kwargs.get('other_pk')
        profile = request.user.gaming_profile  # Updated to use related_name
        other_profile = get_object_or_404(Profile, pk=other_pk)

        # Prevent adding self as a friend
        if profile == other_profile:
            messages.error(request, "You cannot add yourself as a friend.")
            return redirect('gaming:show-all-profiles')

        # Check if already friends
        if Friend.objects.filter(
            (models.Q(from_profile=profile) & models.Q(to_profile=other_profile)) |
            (models.Q(from_profile=other_profile) & models.Q(to_profile=profile))
        ).exists():
            messages.info(request, "You are already friends with this user.")
            return redirect('gaming:profile-detail', pk=other_profile.pk)

        # Create a new Friend relationship
        Friend.objects.create(from_profile=profile, to_profile=other_profile)
        messages.success(request, f"You are now friends with {other_profile.first_name} {other_profile.last_name}.")
        return redirect('gaming:profile-detail', pk=other_profile.pk)

class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'gaming/friend_suggestions.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.gaming_profile  # Updated to use related_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggestions'] = self.object.get_friend_suggestions()
        return context

class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'gaming/news_feed.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.gaming_profile  # Updated to use related_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_feed'] = self.object.get_news_feed()  # Implement get_news_feed in Profile model
        return context

class FriendsProgressListView(LoginRequiredMixin, ListView):
    """
    Displays a list of Progress entries from the authenticated user's friends.
    """
    model = Progress
    template_name = 'gaming/friends_progress_list.html'
    context_object_name = 'progress_entries'
    paginate_by = 10  

    def get_queryset(self):
        """
        Returns Progress entries from the user's friends.
        """
        user_profile = self.request.user.gaming_profile
        friends = user_profile.get_friends()  # Assumes get_friends() method returns a queryset of Profile instances
        return Progress.objects.filter(user__gaming_profile__in=friends).select_related('user', 'game')
