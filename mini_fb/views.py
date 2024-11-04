# views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import get_object_or_404
from .models import Profile, StatusMessage, Image
from django.shortcuts import redirect
from django.urls import reverse
from .forms import (
    CreateProfileForm,
    CreateStatusMessageForm,
    UpdateProfileForm,
    UpdateStatusMessageForm
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

class ProfileOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        profile = self.get_object()
        return profile.user == self.request.user
    
class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'  
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_form'] = CreateStatusMessageForm()
        return context


class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

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
        return super().form_valid(form)

    def form_invalid(self, form, user_form):
        return self.render_to_response(self.get_context_data(form=form, user_form=user_form))

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})




class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def form_valid(self, form):
        profile = get_object_or_404(Profile, user=self.request.user)
        form.instance.profile = profile

        response = super().form_valid(form)
        sm = self.object

        files = self.request.FILES.getlist('files')
        for f in files:
            image = Image()
            image.image_file = f
            image.status_message = sm
            image.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, user=self.request.user)
        return context

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})



class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
class DeleteStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    def test_func(self):
        status_message = self.get_object()
        return status_message.profile.user == self.request.user

    def get_success_url(self):
        profile_pk = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_pk})
    


class UpdateStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'mini_fb/update_status_form.html'
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

        return response

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})


class CreateFriendView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        other_pk = kwargs.get('other_pk')
        profile = get_object_or_404(Profile, user=request.user)
        other_profile = get_object_or_404(Profile, pk=other_pk)

        if profile.user != request.user:
            return redirect('show_profile', pk=profile.pk)

        profile.add_friend(other_profile)

        return redirect('show_profile', pk=other_profile.pk)

    
class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggestions'] = self.object.get_friend_suggestions()
        return context

    

class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_feed'] = self.object.get_news_feed()
        return context
