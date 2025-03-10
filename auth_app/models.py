from django.db import models
from django.contrib.auth.models import AbstractUser


class UCLAUser(AbstractUser):

    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profile_picture = models.URLField(max_length=500, null=True, blank=True)
    is_ucla_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email
