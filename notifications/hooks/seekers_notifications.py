# notifications/hooks/seeker_notifications.py
from notifications.models import Notification
from accounts.models import Follow  # ✅ Centralized Follow model
from django.contrib.auth import get_user_model

User = get_user_model()


def notify_seeker_approved(seeker_post):
    """
    Notify relevant parties when a seeker post is approved.
    """
    # --- Notify the author ---
    Notification.objects.create(
        recipient=seeker_post.author,
        verb=f"Your seeker request '{seeker_post.title}' has been approved ✅",
        target_object_id=seeker_post.pk,
        target_content_type="seekerpost"
    )

    # --- Global notifications (optional for everyone except the author) ---
    for user in User.objects.exclude(pk=seeker_post.author.pk):
        Notification.objects.create(
            recipient=user,
            verb=f"New seeker request in {seeker_post.category.name}: '{seeker_post.title}' by {seeker_post.author.username}",
            target_object_id=seeker_post.pk,
            target_content_type="seekerpost"
        )

    # --- Notify followers of the author ---
    followers = seeker_post.author.followers.all()  # from Follow model
    for follow in followers:
        Notification.objects.create(
            recipient=follow.follower,
            actor=seeker_post.author,
            verb=f"{seeker_post.author.username} created a new seeker request: '{seeker_post.title}'",
            target_object_id=seeker_post.pk,
            target_content_type="seekerpost"
        )


def notify_seeker_rejected(seeker_post):
    """
    Notify the author if their seeker post was rejected.
    """
    Notification.objects.create(
        recipient=seeker_post.author,
        verb=f"Your seeker request '{seeker_post.title}' was rejected 🚫",
        target_object_id=seeker_post.pk,
        target_content_type="seekerpost"
    )


def notify_seeker_town_approved(seeker_post, town_name):
    """
    Notify the author if their seeker town was approved.
    """
    Notification.objects.create(
        recipient=seeker_post.author,
        verb=f"Your town '{town_name}' for seeker request '{seeker_post.title}' has been approved ✅",
        target_object_id=seeker_post.pk,
        target_content_type="seekerpost"
    )


def notify_seeker_town_rejected(seeker_post, town_name):
    """
    Notify the author if their seeker town was rejected.
    """
    Notification.objects.create(
        recipient=seeker_post.author,
        verb=f"Your town '{town_name}' for seeker request '{seeker_post.title}' was rejected 🚫. Please update.",
        target_object_id=seeker_post.pk,
        target_content_type="seekerpost"
    )
