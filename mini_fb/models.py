# models.py

from django.db import models
from django.urls import reverse
from django.db.models import Q

class Profile(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    email_address = models.EmailField(unique=True)
    profile_image_url = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
    
    def get_friends(self):
        friends = Friend.objects.filter(Q(profile1=self) | Q(profile2=self))
        friends_profiles = [friend.profile2 if friend.profile1 == self else friend.profile1 for friend in friends]
        return friends_profiles
    
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
        friends = self.get_friends()
        friends_pks = [friend.pk for friend in friends]
        friends_pks.append(self.pk)  # Exclude self

        suggestions = Profile.objects.exclude(pk__in=friends_pks)
        return suggestions

    def get_news_feed(self):
        # Get the profile and friends' PKs
        profiles = [self] + self.get_friends()
        profiles_pks = [profile.pk for profile in profiles]

        # Get StatusMessages for self and friends
        news_feed = StatusMessage.objects.filter(profile__pk__in=profiles_pks).order_by('-timestamp')
        return news_feed

class StatusMessage(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f"StatusMessage(pk={self.pk}, profile={self.profile}, timestamp={self.timestamp})"

    class Meta:
        ordering = ['-timestamp']

    def get_images(self):
        return self.images.all()

class Image(models.Model):
    image_file = models.ImageField(upload_to='images/')
    timestamp = models.DateTimeField(auto_now_add=True)
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f"Image(pk={self.pk}, status_message={self.status_message.pk})"

class Friend(models.Model):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_profile1_set')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_profile2_set')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile1} & {self.profile2}"
    