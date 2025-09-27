from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Person
from notifications.hooks.person_notifications import (
    notify_profile_approval,
    notify_profile_rejection,
    notify_pending_town,
    notify_town_approval,
    notify_town_rejection,
    notify_business_name_toggle
)

# --- Profile creation for new users ---
"""Automatically create a Person profile when a new user signs up."""
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "profile"):
        Person.objects.create(user=instance, approval_status="pending")
# --- Ensure profile updates when user is saved ---
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    """Ensure the Person profile updates when the User model is saved."""
    if hasattr(instance, "profile"):
        instance.profile.save()

# --- Notification triggers for Person updates ---
@receiver(post_save, sender=Person)
def person_notifications(sender, instance, **kwargs):
    """
    Trigger notifications for profile updates, town approvals/rejections,
    and business name toggle changes. Use transient attributes in the view/admin
    to control which notifications fire.
    """
    # Profile approval/rejection
    if hasattr(instance, "_notify_approval"):
        if instance._notify_approval:
            notify_profile_approval(instance)
        else:
            notify_profile_rejection(instance)

    # Town pending
    if hasattr(instance, "_pending_town"):
        notify_pending_town(instance, instance._pending_town)

    # Town approved/rejected
    if hasattr(instance, "_town_approved"):
        notify_town_approval(instance, instance._town_approved)
    if hasattr(instance, "_town_rejected"):
        notify_town_rejected(instance, instance._town_rejected)

    # Business name toggle
    if hasattr(instance, "_business_toggle"):
        notify_business_name_toggle(instance)
