# gaming/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation

class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Game(models.Model):
    title = models.CharField(max_length=200)
    platforms = models.ManyToManyField(Platform, related_name='games')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='games')
    release_date = models.DateField()
    developer = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='gaming_profile'  
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    email_address = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to='profile_images/')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('gaming:profile-detail', kwargs={'pk': self.pk})

    def get_friends(self):
        friends = Friend.objects.filter(Q(profile1=self) | Q(profile2=self)).values_list('profile1', 'profile2')
        friend_ids = set()
        for p1, p2 in friends:
            if p1 != self.pk:
                friend_ids.add(p1)
            if p2 != self.pk:
                friend_ids.add(p2)
        return Profile.objects.filter(pk__in=friend_ids)

    def add_friend(self, other):
        if self == other:
            print("Cannot add yourself as a friend.")
            return

        friendship_exists = Friend.objects.filter(
            (Q(profile1=self) & Q(profile2=other)) | (Q(profile1=other) & Q(profile2=self))
        ).exists()

        if not friendship_exists:
            Friend.objects.create(profile1=self, profile2=other)
            print(f"Friendship created between {self} and {other}.")
        else:
            print(f"Friendship already exists between {self} and {other}.")

    def get_friend_suggestions(self):
        # Get the user's friends and their PKs
        friends = self.get_friends()
        friends_pks = list(friends.values_list('pk', flat=True))
        friends_pks.append(self.pk)  # Exclude self

        # Start with all profiles that are not the current user or a friend
        base_suggestions = Profile.objects.exclude(pk__in=friends_pks)

        # Get all games the user has played and their genres
        user_progress = Progress.objects.filter(user=self.user).select_related('game')
        user_games = {p.game for p in user_progress}
        user_genres = {p.game.genre for p in user_progress if p.game.genre}

        # Create lookup dictionaries for user ratings: {game_id: rating}
        user_ratings = {p.game_id: p.rating for p in user_progress if p.rating}

        # 1. Find profiles who played games of the same genres
        genre_matched_pks = Progress.objects.filter(
            game__genre__in=user_genres
        ).values_list('user__gaming_profile', flat=True)

        # 2. Find profiles who share same game and same rating
        rating_matched_pks = set()
        for game_id, rating in user_ratings.items():
            matched_profiles_for_game = Progress.objects.filter(
                game_id=game_id,
                rating=rating
            ).values_list('user__gaming_profile', flat=True)
            rating_matched_pks.update(matched_profiles_for_game)

        # Combine genre and rating matches
        matched_pks = set(genre_matched_pks) | rating_matched_pks

        # Filter the base suggestions to only those who matched by genre or rating
        suggestions = base_suggestions.filter(pk__in=matched_pks)

        return suggestions

class Comment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comments')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    content = models.TextField(default='')
    timestamp = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Comment by {self.profile} on {self.content_object}"

    
class Like(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='likes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('profile', 'content_type', 'object_id')  # Prevent duplicate likes

    def __str__(self):
        return f"Like by {self.profile} on {self.content_object}"


class Progress(models.Model):
    COMPLETION_STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Wishlist', 'Wishlist'),
    ]

    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='progress_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_entries')
    platform = models.ForeignKey('Platform', on_delete=models.CASCADE, related_name='progress_entries')
    completion_status = models.CharField(max_length=20, choices=COMPLETION_STATUS_CHOICES, default='Not Started')
    hours_played = models.PositiveIntegerField(default=0)
    achievements = models.PositiveIntegerField(default=0)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    # Add GenericRelations for comments and likes
    comments = GenericRelation(Comment, related_query_name='progress_comments')
    likes = GenericRelation(Like, related_query_name='progress_likes')

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"

    def get_absolute_url(self):
        return reverse('gaming:progress-detail', kwargs={'pk': self.pk})



class Friend(models.Model):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_profile1_set')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_profile2_set')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile1} & {self.profile2}"



class StatusMessage(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='status_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    # Add these lines to link likes and comments via GenericRelation
    comments = GenericRelation(Comment, related_query_name='statusmessage_comments')
    likes = GenericRelation(Like, related_query_name='statusmessage_likes')

    def __str__(self):
        return f"Status by {self.profile} at {self.timestamp}"

    def get_absolute_url(self):
        return reverse('gaming:status-detail', kwargs={'pk': self.pk})


class Image(models.Model):
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE, related_name='images')
    image_file = models.ImageField(upload_to='status_images/')
    timestamp = models.DateTimeField(auto_now_add=True)  # Added timestamp field

    def __str__(self):
        return f"Image for {self.status_message}"


class FeedItem(models.Model):
    """
    A generic feed item that can represent different types of content, such as
    status messages or game progress entries.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"FeedItem by {self.user.username} at {self.timestamp}"
