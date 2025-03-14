from django.db import models
from auth_app.models import UCLAUser


class Profile(models.Model):
    user = models.OneToOneField(UCLAUser, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    major = models.CharField(max_length=100, blank=True)
    year = models.CharField(max_length=20, blank=True)
    age = models.PositiveSmallIntegerField()
    interests = models.JSONField(default=list, blank=True)
    photos = models.JSONField(default=list, blank=True)
    location = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    gender_preference = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"


class Settings(models.Model):
    user = models.OneToOneField(UCLAUser, on_delete=models.CASCADE, related_name="settings", null=True, blank=True)
    email_notifications = models.BooleanField(default=True)
    match_notifications = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ("public", "Public"),
            ("matches_only", "Matches Only"),
            ("private", "Private"),
        ],
        default="public",
    )
    show_online_status = models.BooleanField(default=True)
    max_distance = models.IntegerField(default=50)  # in miles
    age_min = models.IntegerField(default=18)
    age_max = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.email}'s Settings"
        return "Public Settings"
