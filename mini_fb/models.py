from django.db import models

class Profile(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    email_address = models.EmailField(unique=True)
    profile_image_url = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
