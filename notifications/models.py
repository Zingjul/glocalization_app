# -------------------------
# file: notifications/models.py
# -------------------------
from django.db import models
from django.conf import settings
from django.utils import timezone

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
        on_delete=models.CASCADE,  # If user is deleted, delete notifications
        related_name="notifications",
        help_text="User who will receive the notification"
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # If actor is deleted, delete notifications
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

    def mark_as_read(self):
        """Mark this notification as read."""
        self.read = True
        self.save(update_fields=["read"])

    @staticmethod
    def notify(recipient, actor, verb, target, extra=None):
        """
        Utility to create a notification.
        Example usage:
            Notification.notify(
                recipient=recipient_user,
                actor=actor_user,
                verb="commented",
                target=post,
                extra={"post_title": post.title}
            )
        """
        Notification.objects.create(
            recipient=recipient,
            actor=actor,
            verb=verb,
            target_content_type=target.__class__.__name__.lower(),
            target_object_id=target.id,
            extra=extra or {}
        )

class NotificationPreference(models.Model):
    """
    Stores per-user notification preferences.

    Backend can use these flags to reduce noise;
    frontend can use them to adjust rendering (playful vs. minimal UI).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # If user is deleted, delete preferences
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

class Board(models.Model):
    """
    Represents a central notification board for new approved posts.
    Only one instance is typically used.
    Any interested user can view notifications sent to this board.
    """
    name = models.CharField(max_length=100, unique=True, default="PostBoard")
    description = models.TextField(blank=True, default="Board for all new approved posts.")

    def __str__(self):
        return self.name

class BoardItem(models.Model):
    """
    One row on a board. Mirrors your Notification's lightweight target reference style.
    """
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="items")

    # Target reference (string-based to match your Notification style)
    target_app_label = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100)
    target_object_id = models.PositiveBigIntegerField()

    # Denormalized for fast rendering
    title = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=512, blank=True)
    extra = models.JSONField(default=dict, blank=True)

    approved_at = models.DateTimeField(null=True, blank=True)
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['board', 'target_app_label', 'target_model', 'target_object_id'],
                name='unique_board_item_per_object'
            )
        ]
        ordering = ['-pinned', '-approved_at', '-created_at', '-id']

    def __str__(self):
        return f"{self.board.name}: {self.title or f'{self.target_model}#{self.target_object_id}'}"