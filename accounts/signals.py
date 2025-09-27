from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# from django.contrib.auth.signals import password_changed
from django.conf import settings
from .models import CustomUser, Follow
from notifications.models import Notification

User = settings.AUTH_USER_MODEL

# --- Notify on signup ---
@receiver(post_save, sender=CustomUser)
def notify_on_signup(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance,
            actor=None,
            verb="Welcome! Your account has been created successfully.",
            target_object_id=instance.id,
            target_content_type="user"
        )

# --- Notify on password change ---
# @receiver(password_changed)
# def notify_on_password_change(sender, request, user, **kwargs):
#     Notification.objects.create(
#         recipient=user,
#         actor=None,
#         verb="Your password was changed successfully.",
#         target_object_id=user.id,
#         target_content_type="user"
#     )

# --- Notify admins on account deletion ---
@receiver(post_delete, sender=CustomUser)
def notify_on_account_deletion(sender, instance, **kwargs):
    for admin in CustomUser.objects.filter(is_superuser=True):
        Notification.objects.create(
            recipient=admin,
            actor=instance,
            verb=f"User account deleted: {instance.username}",
            target_object_id=instance.id,
            target_content_type="user"
        )

# alert follow and unfollow
@receiver(post_save, sender=Follow)
def notify_follow(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.following,
            actor=instance.follower,
            verb=f"{instance.follower.username} is now following you 👋",
            target_object_id=instance.id,
            target_content_type="follow"
        )

# @receiver(post_delete, sender=Follow)
# def notify_unfollow(sender, instance, **kwargs):
#     Notification.objects.create(
#         recipient=instance.following,
#         actor=instance.follower,
#         verb=f"{instance.follower.username} has unfollowed you.",
#         target_object_id=instance.id,
#         target_content_type="follow"
#     )

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """
    When a user follows another, notify the 'following' user.
    """
    if created:
        Notification.objects.create(
            recipient=instance.following,   # The person being followed
            actor=instance.follower,       # The person who followed
            verb="started_following",      # Action type
            target_content_type="user",    # For frontend routing
            target_object_id=instance.follower.id,  # The follower's ID
            extra={
                "message": f"{instance.follower.username} started following you"
            }
        )