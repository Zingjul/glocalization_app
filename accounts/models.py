from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
import secrets

def generate_visual_id(length=16):
    """Generates a secure random URL-safe string."""
    return secrets.token_urlsafe(length)

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    home_town = models.CharField(max_length=20, blank=True, null=True)
    visual_id = models.CharField(max_length=32, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.visual_id:
            self.visual_id = generate_visual_id()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.visual_id:
            return f"{self.username} (Visual ID: {self.visual_id})"
        else:
            return self.username