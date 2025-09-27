# posts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from notifications.hooks.post_notifications import (
    notify_post_approved,
    notify_post_rejected,
)

@receiver(post_save, sender=Post)
def post_notifications(sender, instance, created, **kwargs):
    """
    Handle notifications for Post events:
    - Approval / rejection (triggered by transient flags in admin/views).
    NOTE: follower/global notifications are already handled in hooks.
    """

    # --- Approval / Rejection ---
    if hasattr(instance, "_notify_approval"):
        if instance._notify_approval:
            notify_post_approved(instance)
        else:
            notify_post_rejected(instance)
