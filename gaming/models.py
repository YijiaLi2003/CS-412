from django.db import models
from django.contrib.auth.models import User

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Game(models.Model):
    title = models.CharField(max_length=200)
    platform = models.CharField(max_length=100)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='games')
    release_date = models.DateField()
    developer = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Progress(models.Model):
    COMPLETION_STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
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
    completion_status = models.CharField(max_length=20, choices=COMPLETION_STATUS_CHOICES, default='Not Started')
    hours_played = models.PositiveIntegerField(default=0)
    achievements = models.PositiveIntegerField(default=0)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"
