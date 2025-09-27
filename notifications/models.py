# -------------------------
# file: notifications/models.py
# -------------------------
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    """
    Core Notification model.
    
    Each instance represents a notification for a specific recipient.
    Examples:
      - A user’s post gets approved → notify the author + followers.
      - A comment is made on a user’s post → notify the author.
      - An admin approves a profile → notify the user.
    """

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="User who will receive the notification"
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actor_notifications",
        help_text="User who caused the event (e.g., post author, commenter, admin)."
    )

    # Human-readable action description, e.g. 'post_approved', 'commented'
    verb = models.CharField(max_length=255)

    # Lightweight target reference (instead of full GenericForeignKey for simplicity)
    target_content_type = models.CharField(max_length=100, null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)

    # Optional payload for frontend (JSON-serializable: post title, excerpt, etc.)
    extra = models.JSONField(default=dict, blank=True)

    # Read/unread state
    read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification({self.id}) → {self.recipient} :: {self.verb}"


class NotificationPreference(models.Model):
    """
    Stores per-user notification preferences.
    
    Backend can use these flags to reduce noise; 
    frontend can use them to adjust rendering (playful vs. minimal UI).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences"
    )

    # Category-level preferences
    allow_global_posts = models.BooleanField(
        default=True,
        help_text="Receive global notifications when new posts are approved."
    )
    allow_comments = models.BooleanField(
        default=True,
        help_text="Receive notifications when someone comments on your post."
    )

    # UI preference (affects frontend display style)
    mode = models.CharField(
        max_length=20,
        default="playful",
        help_text="Frontend tone: playful, professional, or minimal."
    )

    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"NotifPrefs({self.user})"
