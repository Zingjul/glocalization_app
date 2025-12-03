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
        """Readable fallback for admin and logs."""
        actor_name = self.actor.username if self.actor else "System"
        return f"{actor_name} - {self.verb.replace('_', ' ').capitalize()}"

    def display_text(self):
        """Return a human-friendly sentence for each notification."""
        actor_name = self.actor.username if self.actor else "System"
        verb = self.verb
        extra = self.extra or {}
        post_title = extra.get("post_title") or extra.get("title")

        # --- Custom formatting rules ---
        if verb in ["post_published", "seeker_post_published"]:
            return f"Your post '{post_title or 'Untitled'}' has been approved!"
        elif verb in ["post_published_subscription", "seeker_post_published_subscription"]:
            return f"{actor_name} just published a new post '{post_title or 'Untitled'}'."
        elif verb == "commented":
            return f"{actor_name} commented on your post '{post_title or 'Untitled'}'."
        elif verb == "started_following":
            return f"{actor_name} started following you."
        elif verb == "profile_approved":
            return f"Your profile update has been approved!"
        elif verb == "account_created":
            return f"Welcome! Your account has been created successfully."
        else:
            return f"{actor_name} {verb.replace('_', ' ')}."

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

    def get_target_url(self):
        """Return a direct URL to the notification target if possible."""
        if not self.target_content_type or not self.target_object_id:
            return None

        model = self.target_content_type.split(".")[-1]
        obj_id = self.target_object_id

        # Adjust these names to match your actual URL names
        if model == "post":
            return reverse("post_detail", args=[obj_id])
        elif model == "seekerpost":
            return reverse("seekerpost_detail", args=[obj_id])
        elif model == "board":
            return reverse("board_detail", args=[obj_id])

        return None
    # def get_target_url(self):
    #     """
    #     Return a URL to the target object if supported.
    #     Extend this as your app grows (posts, seekerposts, etc.)        ✔✔👀👀
    #     """
    #     if self.target_content_type == "post":
    #         return reverse("post_detail", args=[self.target_object_id])
    #     elif self.target_content_type == "seekerpost":
    #         return reverse("seeker_detail", args=[self.target_object_id])
    #     # Add more content types as needed
    #     return None


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
