from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets

def generate_virtual_id(length=16):
    """Generates a secure random URL-safe string."""
    return secrets.token_urlsafe(length)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)  # Ensuring unique usernames
    email = models.EmailField(unique=True)  # Email required and unique for authentication
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Phone should be unique
    virtual_id = models.CharField(max_length=32, unique=True, blank=True, null=True)  # Auto-generated on save

    def save(self, *args, **kwargs):
        if not self.virtual_id:
            self.virtual_id = generate_virtual_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.email})" if self.email else self.username

    class Meta:
        app_label = 'accounts'  # Ensures Django recognizes this model under the 'accounts' app