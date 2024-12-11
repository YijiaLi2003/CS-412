# gaming/views.py

"""
Django Views for the Gaming Application.

This module defines all the views used in the gaming application, handling functionalities such as
listing and managing progress entries, user profiles, friendships, status messages, comments, likes,
and the news feed.

Class-Based Views:
- ProgressListView
- ProgressAddView
- ProgressDetailView
- ShowAllProfilesView
- ShowProfileDetailView
- CreateProfileView
- UpdateProfileView
- DeleteStatusMessageView
- CreateStatusMessageView
- UpdateStatusMessageView
- CreateFriendView
- ShowFriendSuggestionsView
- CreateCommentView
- ToggleLikeView
- ShowNewsFeedView
- FriendsProgressListView
- SummaryView
- GameCreateView
- ProgressCreateView
- ProgressUpdateView
- UpdateFeedItemView
- DeleteFeedItemView
- ProgressEditFormView

Mixins:
- ProfileOwnerMixin

"""

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    Case,
    Count,
    Exists,
    IntegerField,
    Max,
    OuterRef,
    Q,
    Sum,
    When,
)
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .forms import (
    CommentForm,
    CreateProfileForm,
    CreateStatusMessageForm,
    FriendsProgressFilterForm,
    GameForm,
    GameSearchForm,
    ProgressForm,
    UpdateProfileForm,
    UpdateStatusMessageForm,
)
from .models import (
    Comment,
    FeedItem,
    Friend,
    Game,
    Like,
    Platform,
    Profile,
    Progress,
    StatusMessage,
)


class ProgressListView(LoginRequiredMixin, ListView):
    """
    Displays a paginated list of the logged-in user's progress entries.

    The entries are ordered based on a custom completion status order and game title.
    """
    model = Progress
    template_name = 'gaming/progress_list.html'
    context_object_name = 'progress_entries'
    paginate_by = 10  # Number of entries per page

    def get_queryset(self):
        """
        Customize the queryset to order progress entries by completion status and game title.

        Returns:
            QuerySet: Ordered queryset of Progress instances for the logged-in user.
        """
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
    """
    Displays a list of games to add progress entries, with search and filtering capabilities.

    If no games match the search query, offers an option to create a new game.
    """
    model = Game
    template_name = 'gaming/progress_add.html'
    context_object_name = 'games'

    def get_queryset(self):
        """
        Customize the queryset based on search parameters.

        Filters by game title, platform, and release year.

        Returns:
            QuerySet: Filtered and distinct queryset of Game instances.
        """
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
        """
        Add additional context data to the template.

        Includes the search form and logic to display a creation option if no games are found.

        Returns:
            dict: Context data for the template.
        """
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
    """
    Displays detailed information about a specific progress entry.
    """
    model = Progress
    template_name = 'gaming/progress_detail.html'
    context_object_name = 'progress_entry'


# Social Feature Views


class ProfileOwnerMixin(UserPassesTestMixin):
    """
    Mixin to ensure that the user accessing the view is the owner of the profile.
    """

    def test_func(self):
        """
        Test whether the logged-in user is the owner of the profile.

        Returns:
            bool: True if the user owns the profile, False otherwise.
        """
        profile = self.get_object()
        return profile.user == self.request.user


class ShowAllProfilesView(LoginRequiredMixin, ListView):
    """
    Displays a list of all user profiles in the application.
    """
    model = Profile
    template_name = 'gaming/show_all_profiles.html'
    context_object_name = 'profiles'


class ShowProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Displays detailed information about a specific user profile.

    Also includes a form to create a new status message and a list of the user's friends.
    """
    model = Profile
    template_name = 'gaming/profile_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        """
        Add additional context data to the template.

        Includes the status message form and the list of friends.

        Returns:
            dict: Context data for the template.
        """
        context = super().get_context_data(**kwargs)
        context['status_form'] = CreateStatusMessageForm()
        context['friends'] = self.object.get_friends()
        return context


class CreateProfileView(CreateView):
    """
    Handles the creation of a new user profile.

    Ensures that a user cannot create multiple profiles and handles user authentication upon creation.
    """
    model = Profile
    form_class = CreateProfileForm
    template_name = 'gaming/create_profile_form.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user doesn't already have a profile. Redirect them to their profile
        if it exists.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The appropriate HTTP response.
        """
        if request.user.is_authenticated and hasattr(request.user, 'gaming_profile'):
            messages.error(request, "You already have a profile.")
            return HttpResponseRedirect(reverse('gaming:profile-detail', kwargs={'pk': request.user.gaming_profile.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Add the UserCreationForm to the context for rendering alongside the profile form.

        Returns:
            dict: Context data for the template.
        """
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request and validate both forms (UserCreationForm and ProfileForm).

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The appropriate HTTP response.
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

        Authenticates and logs the user in upon successful creation.

        Args:
            form (Form): The Profile form.
            user_form (Form): The UserCreationForm.

        Returns:
            HttpResponse: The appropriate HTTP response.
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

        Args:
            form (Form): The Profile form.
            user_form (Form): The UserCreationForm.

        Returns:
            HttpResponse: The re-rendered template with error messages.
        """
        context = self.get_context_data(form=form, user_form=user_form)
        return self.render_to_response(context)

    def get_success_url(self):
        """
        Redirect the user to their profile page after successful creation.

        Returns:
            str: The URL to the profile detail page.
        """
        return reverse('gaming:profile-detail', kwargs={'pk': self.object.pk})


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """
    Handles updating an existing user profile.

    Only allows the owner of the profile to perform updates.
    """
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'gaming/update_profile_form.html'
    context_object_name = 'profile'

    def get_object(self):
        """
        Retrieve the profile object associated with the logged-in user.

        Returns:
            Profile: The profile instance.
        """
        return self.request.user.gaming_profile

    def form_valid(self, form):
        """
        Handle valid form submissions by saving the form and displaying a success message.

        Args:
            form (Form): The UpdateProfileForm.

        Returns:
            HttpResponse: The appropriate HTTP response.
        """
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirect the user to their profile page after successful update.

        Returns:
            str: The URL to the profile detail page.
        """
        return reverse('gaming:profile-detail', kwargs={'pk': self.object.pk})


class DeleteStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Handles the deletion of a status message.

    Only allows the owner of the status message to perform deletion.
    """
    model = StatusMessage
    template_name = 'gaming/delete_status_form.html'
    context_object_name = 'status_message'

    def test_func(self):
        """
        Verify that the logged-in user is the owner of the status message.

        Returns:
            bool: True if the user owns the status message, False otherwise.
        """
        status_message = self.get_object()
        return status_message.profile.user == self.request.user

    def delete(self, request, *args, **kwargs):
        """
        Handle the deletion of the status message and display a success message.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The appropriate HTTP response.
        """
        messages.success(self.request, "Status message deleted successfully!")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        """
        Redirect the user to their profile detail page after deletion.

        Returns:
            str: The URL to the profile detail page.
        """
        profile_pk = self.object.profile.pk
        return reverse('gaming:profile-detail', kwargs={'pk': profile_pk})


class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    """
    Handles the creation of a new status message.

    Upon successful creation, a FeedItem is also created to include the status message in the user's feed.
    """
    model = StatusMessage
    fields = ['message']
    template_name = 'gaming/create_status_message.html'

    def form_valid(self, form):
        """
        Handle valid form submissions by associating the status message with the user's profile
        and creating a corresponding FeedItem.

        Args:
            form (Form): The CreateStatusMessageForm.

        Returns:
            HttpResponse: The appropriate HTTP response.
        """
        form.instance.profile = self.request.user.gaming_profile
        response = super().form_valid(form)
        # Create a FeedItem for this StatusMessage
        FeedItem.objects.create(
            user=self.request.user,
            content_object=self.object
        )
        return response

    def get_success_url(self):
        """
        Redirect the user to the news feed after successful creation.

        Returns:
            str: The URL to the news feed.
        """
        return reverse('gaming:news-feed')


class UpdateStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Handles updating an existing status message.

    Allows the owner to update the message content and delete associated images.
    """
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'gaming/update_status_form.html'
    context_object_name = 'status_message'

    def test_func(self):
        """
        Verify that the logged-in user is the owner of the status message.

        Returns:
            bool: True if the user owns the status message, False otherwise.
        """
        status_message = self.get_object()
        return status_message.profile.user == self.request.user

    def form_valid(self, form):
        """
        Handle valid form submissions by saving updates and deleting selected images.

        Args:
            form (Form): The UpdateStatusMessageForm.

        Returns:
            HttpResponse: The appropriate HTTP response.
        """
        response = super().form_valid(form)
        # Handle image deletions
        images_to_delete = form.cleaned_data.get('delete_images')
        if images_to_delete:
            images_to_delete.delete()
        messages.success(self.request, "Status message updated successfully!")
        return response

    def get_success_url(self):
        """
        Redirect the user to the news feed after successful update.

        Returns:
            str: The URL to the news feed.
        """
        return reverse('gaming:news-feed')


class CreateFriendView(LoginRequiredMixin, View):
    """
    Handles the creation of a friendship between the logged-in user and another user.
    """

    def post(self, request, *args, **kwargs):
        """
        Process POST requests to add a friend.

        Validates that the user is not adding themselves and that the friendship doesn't already exist.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments (expects 'other_pk').

        Returns:
            HttpResponse: Redirects to the appropriate page with a success or error message.
        """
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
    """
    Displays a list of suggested friends based on shared game genres and similar game ratings.
    """
    model = Profile
    template_name = 'gaming/friend_suggestions.html'
    context_object_name = 'profile'

    def get_object(self):
        """
        Retrieve the profile of the logged-in user.

        Returns:
            Profile: The profile instance of the logged-in user.
        """
        return self.request.user.gaming_profile  # Using the related_name

    def get_context_data(self, **kwargs):
        """
        Add friend suggestions and detailed match information to the context.

        Returns:
            dict: Context data for the template.
        """
        context = super().get_context_data(**kwargs)
        suggestions = self.object.get_friend_suggestions()
        context['suggestions'] = suggestions

        # Gather user data
        user_profile = self.object
        user_progress = Progress.objects.filter(user=user_profile.user).select_related('game')
        user_games = {p.game for p in user_progress}
        user_genres = {p.game.genre for p in user_progress if p.game.genre is not None}
        user_ratings = {p.game_id: p.rating for p in user_progress if p.rating}

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

            # Attach details to the suggestion object
            suggestion.details = suggestion_data

        return context


class CreateCommentView(LoginRequiredMixin, View):
    """
    Handles the creation of a new comment on a feed item.
    """

    def post(self, request, *args, **kwargs):
        """
        Process POST requests to add a comment.

        Validates the comment form and associates it with the relevant content object.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: Redirects to the news feed with a success message.
        """
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
    """
    Handles the toggling of likes on feed items.
    """

    def post(self, request, *args, **kwargs):
        """
        Process POST requests to like or unlike a feed item.

        Checks if the user has already liked the content object and toggles the like accordingly.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: Redirects to the news feed with an appropriate message.
        """
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
    """
    Displays the news feed consisting of feed items from the user and their friends.

    The feed is ordered by the most recent items first and includes pagination.
    """
    model = FeedItem
    template_name = 'gaming/news_feed.html'
    context_object_name = 'news_feed'
    paginate_by = 10  # Number of feed items per page

    def get_queryset(self):
        """
        Customize the queryset to include feed items from the user and their friends.

        Returns:
            QuerySet: Ordered queryset of FeedItem instances.
        """
        user_profile = self.request.user.gaming_profile
        friends = user_profile.get_friends()
        user_qs = Profile.objects.filter(pk=user_profile.pk)
        profiles = friends | user_qs
        user_pks = profiles.values_list('user__pk', flat=True)

        queryset = FeedItem.objects.filter(
            user__pk__in=user_pks
        ).select_related('user').order_by('-timestamp')

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add additional context data to the template.

        Includes forms for comments, status messages, and progress entries, as well as the user's own progress.

        Returns:
            dict: Context data for the template.
        """
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['form'] = CreateStatusMessageForm()  # Status message form
        context['progress_form'] = ProgressForm()      # Progress entry form

        # Add user's own progress entries to context
        user_progress = Progress.objects.filter(user=self.request.user).select_related('game')
        context['user_progress'] = user_progress

        return context


class FriendsProgressListView(LoginRequiredMixin, ListView):
    """
    Displays a list of progress entries from the user's friends, with filtering options.
    """
    model = Progress
    template_name = 'gaming/friends_progress_list.html'
    context_object_name = 'progress_entries'
    paginate_by = 10  # Number of entries per page

    def get_queryset(self):
        """
        Customize the queryset to include progress entries from friends and apply filters.

        Filters based on completion status, platform, and specific friend.

        Returns:
            QuerySet: Filtered queryset of Progress instances from friends.
        """
        user_profile = self.request.user.gaming_profile
        friends = user_profile.get_friends()
        queryset = Progress.objects.filter(user__gaming_profile__in=friends).select_related('user', 'game', 'platform')

        # Get filters from GET parameters
        completion_status = self.request.GET.get('completion_status', '')
        platform_id = self.request.GET.get('platform', '')
        friend_id = self.request.GET.get('friend', '')

        if completion_status:
            queryset = queryset.filter(completion_status=completion_status)
        if platform_id:
            queryset = queryset.filter(platform_id=platform_id)
        if friend_id:
            queryset = queryset.filter(user__gaming_profile=friend_id)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add the filtering form to the context.

        Returns:
            dict: Context data for the template.
        """
        context = super().get_context_data(**kwargs)
        # Initialize form with current filters
        user_profile = self.request.user.gaming_profile
        form = FriendsProgressFilterForm(self.request.GET or None, user_profile=user_profile)
        context['filter_form'] = form
        return context


class SummaryView(LoginRequiredMixin, TemplateView):
    """
    Displays a summary dashboard of the user's gaming statistics.
    """
    template_name = 'gaming/summary.html'

    def get_context_data(self, **kwargs):
        """
        Add summary statistics to the context.

        Includes total hours played, games completed, top games, genre distribution, platform popularity,
        completion status breakdown, and hours played by genre.

        Returns:
            dict: Context data for the template.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        progress_entries = Progress.objects.filter(user=user).select_related('game', 'platform')

        # Total Hours Played
        total_hours = progress_entries.aggregate(total=Sum('hours_played'))['total'] or 0

        # Games Completed
        games_completed = progress_entries.filter(completion_status='Completed').count()

        # Top game by hours
        top_game_data = (
            progress_entries
            .values('game__title')
            .annotate(total=Sum('hours_played'))
            .order_by('-total')
            .first()
        )
        top_game_title = top_game_data['game__title'] if top_game_data else "No games played"
        top_game_hours = top_game_data['total'] if top_game_data else 0

        # Top 5 games by hours
        top_5 = (
            progress_entries
            .values('game__title')
            .annotate(total=Sum('hours_played'))
            .order_by('-total')[:5]
        )
        chart_labels = [entry['game__title'] for entry in top_5]
        chart_data = [entry['total'] for entry in top_5]

        # Genre Distribution (Pie)
        genre_counts = (
            progress_entries
            .values('game__genre__name')
            .annotate(count=Count('id'))
            .filter(game__genre__name__isnull=False)
        )
        total_entries = sum(g['count'] for g in genre_counts)
        genre_labels = [g['game__genre__name'] for g in genre_counts]
        genre_data = [
            (g['count'] / total_entries) * 100 if total_entries > 0 else 0
            for g in genre_counts
        ]
        genre_data = [round(val, 2) for val in genre_data]

        # Platform Popularity (Bar)
        platform_counts = (
            progress_entries
            .values('platform__name')
            .annotate(count=Count('id'))
            .order_by()
        )
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
        hours_by_genre = (
            progress_entries
            .values('game__genre__name')
            .annotate(total=Sum('hours_played'))
            .filter(game__genre__name__isnull=False)
            .order_by('-total')
        )
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
    """
    Handles the creation of a new game entry.

    After creating the game, redirects the user to create a progress entry for the newly created game.
    """
    model = Game
    form_class = GameForm
    template_name = 'gaming/game_create.html'
    success_url = reverse_lazy('gaming:progress-add')  # Temporary redirect

    def get_initial(self):
        """
        Prepopulate the form with the game title if provided via GET parameters.

        Returns:
            dict: Initial data for the form.
        """
        initial = super().get_initial()
        title = self.request.GET.get('title', '')
        if title:
            initial['title'] = title
        return initial

    def form_valid(self, form):
        """
        Handle valid form submissions by saving the game and redirecting to create a progress entry.

        Args:
            form (Form): The GameForm.

        Returns:
            HttpResponse: Redirects to the ProgressCreateView with the new game's ID.
        """
        response = super().form_valid(form)
        # After creating the game, redirect to ProgressCreateView with the new game
        return redirect(reverse('gaming:progress-create') + f'?game={self.object.pk}')


class ProgressCreateView(LoginRequiredMixin, CreateView):
    """
    Handles the creation of a new progress entry for a specific game.
    """
    model = Progress
    form_class = ProgressForm
    template_name = 'gaming/progress_create.html'

    def get_initial(self):
        """
        Prepopulate the form with the game if provided via GET parameters.

        Returns:
            dict: Initial data for the form.
        """
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
        """
        Customize form kwargs to pass the game instance for dynamic platform filtering.

        Returns:
            dict: Keyword arguments for the form.
        """
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
        """
        Handle valid form submissions by associating the progress entry with the user
        and creating a corresponding FeedItem.

        Args:
            form (Form): The ProgressForm.

        Returns:
            HttpResponse: The appropriate HTTP response.
        """
        form.instance.user = self.request.user
        response = super().form_valid(form)
        # Create a FeedItem for this Progress entry
        FeedItem.objects.create(
            user=self.request.user,
            content_object=self.object
        )
        return response

    def get_success_url(self):
        """
        Redirect the user to the news feed after successful creation.

        Returns:
            str: The URL to the news feed.
        """
        return reverse('gaming:news-feed')

    def get_context_data(self, **kwargs):
        """
        Add additional context data to the template.

        Includes the game instance if provided.

        Returns:
            dict: Context data for the template.
        """
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
    """
    Handles updating an existing progress entry.

    Allows users to update their progress and optionally share the update to their news feed.
    """
    model = Progress
    form_class = ProgressForm  # Reuse the same form as ProgressCreateView
    template_name = 'gaming/progress_update.html'
    success_url = reverse_lazy('gaming:news-feed')

    def test_func(self):
        """
        Verify that the logged-in user is the owner of the progress entry.

        Returns:
            bool: True if the user owns the progress entry, False otherwise.
        """
        progress = self.get_object()
        return progress.user == self.request.user

    def form_valid(self, form):
        """
        Handle valid form submissions by updating the progress entry and managing feed sharing.

        Args:
            form (Form): The ProgressForm.

        Returns:
            HttpResponse: The appropriate HTTP response.
        """
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
    """
    Handles updating a FeedItem's associated content.

    Determines the type of content and utilizes the appropriate form for editing.
    """
    model = FeedItem
    template_name = 'gaming/update_feed_item.html'
    # No fields here since we are not editing the FeedItem fields directly.

    def test_func(self):
        """
        Verify that the logged-in user is the owner of the feed item.

        Returns:
            bool: True if the user owns the feed item, False otherwise.
        """
        feed_item = self.get_object()
        return feed_item.user == self.request.user

    def get_content_object_form_class(self):
        """
        Determine the appropriate form class based on the type of the content object.

        Returns:
            Form: The form class corresponding to the content object type.
        """
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
        """
        Retrieve the underlying content object associated with the feed item.

        Returns:
            Model instance: The content object instance.
        """
        feed_item = self.get_object()
        return feed_item.content_object

    def get_form_kwargs(self):
        """
        Customize form kwargs to edit the underlying content object instead of the FeedItem.

        Also handles dynamic platform filtering for Progress entries.

        Returns:
            dict: Keyword arguments for the form.
        """
        kwargs = super().get_form_kwargs()
        # Remove the 'instance' key that points to FeedItem
        if 'instance' in kwargs:
            del kwargs['instance']

        obj = self.get_content_object()
        # Set the instance to the content object
        kwargs['instance'] = obj

        # If editing Progress, limit platform choices based on the related game
        if isinstance(obj, Progress):
            kwargs['game'] = obj.game

        return kwargs

    def get_form_class(self):
        """
        Return the appropriate form class based on the content object type.

        Returns:
            Form: The form class to be used.
        """
        return self.get_content_object_form_class()

    def form_valid(self, form):
        """
        Save the form and display a success message.

        Args:
            form (Form): The form instance.

        Returns:
            HttpResponse: Redirects to the news feed.
        """
        form.save()
        messages.success(self.request, "Item updated successfully!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        """
        Redirect the user to the news feed after successful update.

        Returns:
            str: The URL to the news feed.
        """
        return reverse('gaming:news-feed')


class DeleteFeedItemView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Handles the deletion of a FeedItem.

    Only allows the owner of the feed item to perform deletion.
    """
    model = FeedItem
    template_name = 'gaming/delete_feed_item.html'
    success_url = reverse_lazy('gaming:news-feed')

    def test_func(self):
        """
        Verify that the logged-in user is the owner of the feed item.

        Returns:
            bool: True if the user owns the feed item, False otherwise.
        """
        feed_item = self.get_object()
        return feed_item.user == self.request.user

    def delete(self, request, *args, **kwargs):
        """
        Handle the deletion of the feed item and display a success message.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The appropriate HTTP response.
        """
        messages.success(self.request, "Feed item deleted successfully!")
        return super().delete(request, *args, **kwargs)


class ProgressEditFormView(LoginRequiredMixin, DetailView):
    """
    Provides an editable form for a specific progress entry via AJAX or partial rendering.
    """
    model = Progress
    template_name = 'gaming/edit_progress_form.html'
    context_object_name = 'progress_entry'

    def get_queryset(self):
        """
        Ensure that the user can only edit their own progress entries.

        Returns:
            QuerySet: Filtered queryset containing only the user's progress entries.
        """
        return Progress.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests by rendering the form as HTML.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The rendered HTML form.
        """
        self.object = self.get_object()
        form = ProgressForm(instance=self.object)
        context = {
            'form': form,
            'progress_entry': self.object,
        }
        html = render_to_string(self.template_name, context, request=request)
        return HttpResponse(html)
