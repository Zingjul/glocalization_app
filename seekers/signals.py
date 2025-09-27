# seekers/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SeekerPost
from notifications.hooks.seeker_notifications import (
    notify_seeker_approved,
    notify_seeker_rejected,
    notify_seeker_town_approved,
    notify_seeker_town_rejected,
)

@receiver(post_save, sender=SeekerPost)
def seeker_notifications(sender, instance, created, **kwargs):
    """
    Handle notifications for SeekerPost events:
    - Approval / rejection (transient flags).
    - Town approval / rejection (transient flags).
    NOTE: follower/global notifications are already handled in hooks.
    """

    # --- Approval / Rejection ---
    if hasattr(instance, "_notify_approval"):
        if instance._notify_approval:
            notify_seeker_approved(instance)
        else:
            notify_seeker_rejected(instance)

    # --- Town Approval ---
    if hasattr(instance, "_town_approved"):
        notify_seeker_town_approved(instance, instance._town_approved)

    # --- Town Rejection ---
    if hasattr(instance, "_town_rejected"):
        notify_seeker_town_rejected(instance, instance._town_rejected)
