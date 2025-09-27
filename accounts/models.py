from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings  # ✅ for AUTH_USER_MODEL
import secrets
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


def generate_virtual_id(length=16):
    """Generates a secure random URL-safe string."""
    return secrets.token_urlsafe(length)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)  
    email = models.EmailField(unique=True)  
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)  
    virtual_id = models.CharField(max_length=32, unique=True, blank=True, null=True)

    # 📌 New counters
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.virtual_id:
            self.virtual_id = generate_virtual_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.email})" if self.email else self.username

    class Meta:
        app_label = 'accounts'

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="following",
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="followers",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower} → {self.following}"

@receiver(post_save, sender=Follow)
def update_counts_on_follow(sender, instance, created, **kwargs):
    if created:
        instance.following.follower_count = models.F("follower_count") + 1
        instance.follower.following_count = models.F("following_count") + 1
        instance.following.save(update_fields=["follower_count"])
        instance.follower.save(update_fields=["following_count"])

@receiver(post_delete, sender=Follow)
def update_counts_on_unfollow(sender, instance, **kwargs):
    instance.following.follower_count = models.F("follower_count") - 1
    instance.follower.following_count = models.F("following_count") - 1
    instance.following.save(update_fields=["follower_count"])
    instance.follower.save(update_fields=["following_count"])