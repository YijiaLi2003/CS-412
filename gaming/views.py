# gaming/views.py

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import (
    Genre, Game, Progress,
    Profile, Friend, StatusMessage, Image, FeedItem,Comment
)
from .forms import (
    CreateProfileForm, CreateStatusMessageForm,
    UpdateProfileForm, UpdateStatusMessageForm,
    GameSearchForm, ProgressForm,CommentForm
)
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.db.models import Sum, Max
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count
from .models import Progress,Platform
from .forms import GameForm 
from django.urls import reverse_lazy
from django.db.models import Case, When, IntegerField
from urllib.parse import urlencode
from .models import StatusMessage, Like, Profile
from django.db.models import Exists, OuterRef
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.contenttypes.models import ContentType
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
        # Define custom order for completion_status
        status_order = Case(
            When(completion_status='Not Started', then=1),
            When(completion_status='In Progress', then=2),
            When(completion_status='Completed', then=3),
            When(completion_status='Wishlist', then=4),
            default=5,
            output_field=IntegerField(),
        )
        return (
            Progress.objects
            .filter(user=self.request.user)
            .select_related('game', 'platform')
            .annotate(status_order=status_order)
            .order_by('status_order', 'game__title')
        )

class ProgressAddView(LoginRequiredMixin, ListView):
    model = Game
    template_name = 'gaming/progress_add.html'
    context_object_name = 'games'

    def get_queryset(self):
        qs = Game.objects.all()
        q = self.request.GET.get('q', '')
        platform_id = self.request.GET.get('platform', '')
        release_year = self.request.GET.get('release_year', '')

        if q:
            qs = qs.filter(title__icontains=q)
        if platform_id:
            qs = qs.filter(platforms__pk=platform_id)
        if release_year:
            qs = qs.filter(release_date__year=release_year)

        qs = qs.distinct()  # Prevent duplicate results due to many-to-many relationships
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = GameSearchForm(self.request.GET or None)
        context['form'] = form
        query = self.request.GET.get('q', '')
        platform_id = self.request.GET.get('platform', '')
        release_year = self.request.GET.get('release_year', '')

        # If no games found and a query exists, offer to create a new game
        if query and not context['games'].exists():
            context['no_results'] = True
            # Pass the query as a GET parameter to prefill the title in the create form
            context['create_url'] = reverse('gaming:game-create') + '?' + urlencode({'title': query})
        return context


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

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user doesn't already have a profile. Redirect them to their profile
        if it exists.
        """
        if request.user.is_authenticated and hasattr(request.user, 'gaming_profile'):
            messages.error(request, "You already have a profile.")
            return HttpResponseRedirect(reverse('gaming:profile-detail', kwargs={'pk': request.user.gaming_profile.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Add the UserCreationForm to the context for rendering.
        """
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request and validate both forms (UserCreationForm and ProfileForm).
        """
        self.object = None  # Clear the object before handling forms
        form = self.get_form()
        user_form = UserCreationForm(self.request.POST)

        if form.is_valid() and user_form.is_valid():
            return self.form_valid(form, user_form)
        else:
            return self.form_invalid(form, user_form)

    def form_valid(self, form, user_form):
        """
        Save the user and associate the profile with it.
        """
        # Save the user using the UserCreationForm
        user = user_form.save()
        form.instance.user = user  # Link the profile to the newly created user

        # Authenticate and log the user in
        username = user_form.cleaned_data.get('username')
        raw_password = user_form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)

        # Display a success message
        messages.success(self.request, "Profile created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form, user_form):
        """
        Handle invalid forms and re-render the template with errors.
        """
        context = self.get_context_data(form=form, user_form=user_form)
        return self.render_to_response(context)

    def get_success_url(self):
        """
        Redirect the user to their profile page after successful creation.
        """
        return reverse('gaming:profile-detail', kwargs={'pk': self.object.pk})
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
        return self.request.user.gaming_profile  

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

# gaming/views.py

class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    model = StatusMessage
    fields = ['message']
    template_name = 'gaming/create_status_message.html'

    def form_valid(self, form):
        form.instance.profile = self.request.user.gaming_profile
        response = super().form_valid(form)
        # Create a FeedItem for this StatusMessage
        FeedItem.objects.create(
            user=self.request.user,
            content_object=self.object
        )
        return response

    def get_success_url(self):
        return reverse('gaming:news-feed')

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
        # Handle image deletions
        images_to_delete = form.cleaned_data.get('delete_images')
        if images_to_delete:
            images_to_delete.delete()
        messages.success(self.request, "Status message updated successfully!")
        return response

    def get_success_url(self):
        return reverse('gaming:news-feed')

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
            (Q(profile1=profile) & Q(profile2=other_profile)) |
            (Q(profile1=other_profile) & Q(profile2=profile))
        ).exists():
            messages.info(request, "You are already friends with this user.")
            return redirect('gaming:profile-detail', pk=other_profile.pk)

        # Create a new Friend relationship
        Friend.objects.create(profile1=profile, profile2=other_profile)
        messages.success(request, f"You are now friends with {other_profile.user.username}.")
        return redirect('gaming:friends-progress-list')


class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'gaming/friend_suggestions.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.gaming_profile  # Using the related_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        suggestions = self.object.get_friend_suggestions()
        context['suggestions'] = suggestions

    # Gather user data
        user_profile = self.object
        user_progress = Progress.objects.filter(user=user_profile.user).select_related('game')
        user_games = {p.game for p in user_progress}
        user_genres = {p.game.genre for p in user_progress if p.game.genre is not None}
        user_ratings = {p.game_id: p.rating for p in user_progress if p.rating}

        match_details = {}

        for suggestion in suggestions:
            suggestion_data = {
                "genres": [],
                "ratings": []
            }

        # Find genres that both have played
            suggestion_progress = Progress.objects.filter(user=suggestion.user).select_related('game')
            suggestion_genres = {sp.game.genre for sp in suggestion_progress if sp.game.genre is not None}
            shared_genres = user_genres & suggestion_genres
            if shared_genres:
                suggestion_data["genres"] = [g.name for g in shared_genres]

        # Find games and ratings that match
            suggestion_ratings = {sp.game_id: sp.rating for sp in suggestion_progress if sp.rating}
            for g_id, u_rating in user_ratings.items():
                if g_id in suggestion_ratings and suggestion_ratings[g_id] == u_rating:
                    shared_game = next((gm for gm in user_games if gm.pk == g_id), None)
                    if shared_game is not None:
                        suggestion_data["ratings"].append({
                            "game": shared_game,
                            "rating": u_rating
                        })

        # Instead of using a dictionary in the template, just attach details to the suggestion object
            suggestion.details = suggestion_data

        return context

class CreateCommentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        feed_item_id = request.POST.get('feed_item_id')
        feed_item = get_object_or_404(FeedItem, id=feed_item_id)
        content_object = feed_item.content_object

        if form.is_valid():
            comment = form.save(commit=False)
            comment.profile = request.user.gaming_profile
            comment.content_object = content_object
            comment.save()
            messages.success(request, "Your comment has been added.")

        return redirect('gaming:news-feed')


class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        feed_item_id = request.POST.get('feed_item_id')
        feed_item = get_object_or_404(FeedItem, id=feed_item_id)
        user_profile = request.user.gaming_profile

        # Determine the content_object type
        content_object = feed_item.content_object
        content_type = ContentType.objects.get_for_model(type(content_object))
        object_id = content_object.pk

        # Check if the user has already liked this content_object
        like_exists = Like.objects.filter(
            content_type=content_type,
            object_id=object_id,
            profile=user_profile
        ).exists()

        if like_exists:
            # Unlike the content_object
            Like.objects.filter(
                content_type=content_type,
                object_id=object_id,
                profile=user_profile
            ).delete()
            messages.info(request, "You have unliked this post.")
        else:
            # Like the content_object
            Like.objects.create(
                content_type=content_type,
                object_id=object_id,
                profile=user_profile
            )
            messages.success(request, "You have liked this post.")

        return redirect('gaming:news-feed')


class ShowNewsFeedView(LoginRequiredMixin, ListView):
    model = FeedItem
    template_name = 'gaming/news_feed.html'
    context_object_name = 'news_feed'
    paginate_by = 10  # Optional

    def get_queryset(self):
        user_profile = self.request.user.gaming_profile
        friends = user_profile.get_friends()
        user_qs = Profile.objects.filter(pk=user_profile.pk)
        profiles = friends | user_qs
        user_pks = profiles.values_list('user__pk', flat=True)
    
        queryset = FeedItem.objects.filter(
            user__pk__in=user_pks
        ).select_related('user').order_by('-timestamp')
    # Remove the problematic prefetches
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['form'] = CreateStatusMessageForm()  # Add the status message form to the context
        context['progress_form'] = ProgressForm()   # Add the progress form to the context

        # Add user's own progress entries to context
        user_progress = Progress.objects.filter(user=self.request.user).select_related('game')
        context['user_progress'] = user_progress

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


class SummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'gaming/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        progress_entries = Progress.objects.filter(user=user).select_related('game', 'platform')

        # Total Hours Played
        total_hours = progress_entries.aggregate(total=Sum('hours_played'))['total'] or 0

        # Games Completed
        games_completed = progress_entries.filter(completion_status='Completed').count()

        # Top game by hours
        top_game_data = (progress_entries
                         .values('game__title')
                         .annotate(total=Sum('hours_played'))
                         .order_by('-total')
                         .first())
        top_game_title = top_game_data['game__title'] if top_game_data else "No games played"
        top_game_hours = top_game_data['total'] if top_game_data else 0

        # Top 5 games by hours
        top_5 = (progress_entries
                 .values('game__title')
                 .annotate(total=Sum('hours_played'))
                 .order_by('-total')[:5])
        chart_labels = [entry['game__title'] for entry in top_5]
        chart_data = [entry['total'] for entry in top_5]

        # Genre Distribution (Pie)
        genre_counts = (progress_entries
                        .values('game__genre__name')
                        .annotate(count=Count('id'))
                        .filter(game__genre__name__isnull=False))
        total_entries = sum(g['count'] for g in genre_counts)
        genre_labels = [g['game__genre__name'] for g in genre_counts]
        genre_data = [(g['count'] / total_entries)*100 if total_entries > 0 else 0 for g in genre_counts]
        genre_data = [round(val, 2) for val in genre_data]

        # Platform Popularity (Bar)
        # Now we can directly count from progress_entries by platform name
        platform_counts = (progress_entries
                           .values('platform__name')
                           .annotate(count=Count('id'))
                           .order_by())
        platform_labels = [p['platform__name'] for p in platform_counts]
        platform_data = [p['count'] for p in platform_counts]

        # Completion Status Breakdown (Stacked Bar)
        completed_count = progress_entries.filter(completion_status='Completed').count()
        in_progress_count = progress_entries.filter(completion_status='In Progress').count()
        not_started_count = progress_entries.filter(completion_status='Not Started').count()
        wishlist_count = progress_entries.filter(completion_status='Wishlist').count()

        status_labels = ["Status"]
        completed_data = [completed_count]
        in_progress_data = [in_progress_count]
        wishlist_data = [wishlist_count]

        # Hours Played by Genre (Horizontal Bar)
        hours_by_genre = (progress_entries
                          .values('game__genre__name')
                          .annotate(total=Sum('hours_played'))
                          .filter(game__genre__name__isnull=False)
                          .order_by('-total'))
        hours_genre_labels = [h['game__genre__name'] for h in hours_by_genre]
        hours_genre_data = [h['total'] for h in hours_by_genre]

        # Add to context
        context['total_hours'] = total_hours
        context['games_completed'] = games_completed
        context['top_game_title'] = top_game_title
        context['top_game_hours'] = top_game_hours
        context['chart_labels'] = chart_labels
        context['chart_data'] = chart_data

        context['genre_labels'] = genre_labels
        context['genre_data'] = genre_data

        context['platform_labels'] = platform_labels
        context['platform_data'] = platform_data

        context['status_labels'] = status_labels
        context['completed_data'] = completed_data
        context['in_progress_data'] = in_progress_data
        context['wishlist_data'] = wishlist_data

        context['hours_genre_labels'] = hours_genre_labels
        context['hours_genre_data'] = hours_genre_data

        return context
    
class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = 'gaming/game_create.html'
    success_url = reverse_lazy('gaming:progress-add')  # Temporary redirect

    def get_initial(self):
        initial = super().get_initial()
        title = self.request.GET.get('title', '')
        if title:
            initial['title'] = title
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        # After creating the game, redirect to ProgressCreateView with the new game
        return redirect(reverse('gaming:progress-create') + f'?game={self.object.pk}')

class ProgressCreateView(LoginRequiredMixin, CreateView):
    model = Progress
    form_class = ProgressForm
    template_name = 'gaming/progress_create.html'

    def get_initial(self):
        initial = super().get_initial()
        game_id = self.request.GET.get('game', '')
        if game_id:
            try:
                game = Game.objects.get(pk=game_id)
                initial['game'] = game
            except Game.DoesNotExist:
                pass
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        game_id = self.request.GET.get('game', '')
        if game_id:
            try:
                game = Game.objects.get(pk=game_id)
                kwargs['game'] = game
            except Game.DoesNotExist:
                game = None
        else:
            game = None
        kwargs['game'] = game
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        # Create a FeedItem for this Progress entry
        FeedItem.objects.create(
            user=self.request.user,
            content_object=self.object
        )
        return response

    def get_success_url(self):
        return reverse('gaming:news-feed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.request.GET.get('game', '')
        if game_id:
            try:
                game = Game.objects.get(pk=game_id)
                context['game'] = game
            except Game.DoesNotExist:
                context['game'] = None
        else:
            context['game'] = None
        return context

class ProgressUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Progress
    form_class = ProgressForm  # Reuse the same form as ProgressCreateView
    template_name = 'gaming/progress_update.html'
    success_url = reverse_lazy('gaming:news-feed')

    def test_func(self):
        # Ensure that the user owns the progress entry
        progress = self.get_object()
        return progress.user == self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Check if the update is intended for sharing to the feed
        share_to_feed = self.request.POST.get('share_to_feed', False)
        if share_to_feed:
            # Check if a FeedItem already exists for this progress
            content_type = ContentType.objects.get_for_model(Progress)
            feed_item_exists = FeedItem.objects.filter(
                user=self.request.user,
                content_type=content_type,
                object_id=self.object.id
            ).exists()

            if not feed_item_exists:
                # Create a new FeedItem for this progress
                FeedItem.objects.create(
                    user=self.request.user,
                    content_object=self.object
                )
                messages.success(self.request, "Progress updated and shared to your news feed!")
            else:
                messages.info(self.request, "Progress updated. It is already shared in your news feed.")
        else:
            messages.success(self.request, "Progress updated successfully!")
        
        return response
    

class UpdateFeedItemView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = FeedItem
    fields = ['content_object']  # Adjust fields based on content type
    template_name = 'gaming/update_feed_item.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        feed_item = self.get_object()
        return feed_item.user == self.request.user

    def get_success_url(self):
        return reverse('gaming:news-feed')
    

class DeleteFeedItemView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = FeedItem
    template_name = 'gaming/delete_feed_item.html'
    success_url = '/gaming/news-feed/'

    def test_func(self):
        feed_item = self.get_object()
        return feed_item.user == self.request.user
    
class ProgressEditFormView(LoginRequiredMixin, DetailView):
    model = Progress
    template_name = 'gaming/edit_progress_form.html'
    context_object_name = 'progress_entry'

    def get_queryset(self):
        # Ensure that the user can only edit their own progress entries
        return Progress.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ProgressForm(instance=self.object)
        context = {
            'form': form,
            'progress_entry': self.object,
        }
        html = render_to_string(self.template_name, context, request=request)
        return HttpResponse(html)
    
# In views.py
class UpdateFeedItemView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = FeedItem
    template_name = 'gaming/update_feed_item.html'
    # No fields here since we are not editing the FeedItem fields directly.

    def test_func(self):
        feed_item = self.get_object()
        return feed_item.user == self.request.user

    def get_content_object_form_class(self):
        """Return the appropriate form class based on the content_object type."""
        feed_item = self.get_object()
        obj = feed_item.content_object

        if isinstance(obj, StatusMessage):
            return UpdateStatusMessageForm
        elif isinstance(obj, Progress):
            return ProgressForm
        elif isinstance(obj, Comment):
            return CommentForm
        else:
            return None

    def get_content_object(self):
        """Return the underlying content object."""
        feed_item = self.get_object()
        return feed_item.content_object

    def get_form_kwargs(self):
        """Customize form kwargs to edit the underlying content object instead of the FeedItem."""
        kwargs = super().get_form_kwargs()
        # Remove the 'instance' key that points to FeedItem
        if 'instance' in kwargs:
            del kwargs['instance']

        obj = self.get_content_object()
        # Set the instance to the content object
        kwargs['instance'] = obj

        # If editing Progress, and we want to limit platforms to the related game
        if isinstance(obj, Progress):
            # This ensures that the ProgressForm can limit platform choices based on the game
            kwargs['game'] = obj.game

        return kwargs

    def get_form_class(self):
        return self.get_content_object_form_class()

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Item updated successfully!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('gaming:news-feed')



class DeleteFeedItemView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = FeedItem
    template_name = 'gaming/delete_feed_item.html'

    def test_func(self):
        feed_item = self.get_object()
        return feed_item.user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Feed item deleted successfully!")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('gaming:news-feed')