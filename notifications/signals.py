"""
notifications/signals.py

Handles automatic notification creation for key events:
1. When a Post or SeekerPost transitions from 'pending' → 'approved'
2. When a Post or SeekerPost receives a comment (only if approved)
3. Synchronization with the Board model on approval/reversion
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from .models import Notification
from posts.models import Post
from seekers.models import SeekerPost
from comment.models import Comment
from board.models import Board
from .utils import remove_from_board
from notifications.hooks.post_notifications import notify_post_approved, notify_post_rejected
from notifications.hooks.seekers_notifications import notify_seeker_approved, notify_seeker_rejected

User = get_user_model()

print("Notifications signals initialized.")


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------
def add_to_board(instance, title_field):
    """Adds an approved Post or SeekerPost to the Board."""
    content_type = ContentType.objects.get_for_model(instance.__class__)

    if Board.objects.filter(content_type=content_type, object_id=instance.id).exists():
        return  # Already listed

    title = getattr(instance, title_field, "Untitled")
    author_name = getattr(instance.author, "username", str(instance.author))

    Board.objects.create(
        title=title,
        author_name=author_name,
        content_object=instance,
    )


def create_notification_instance(recipient, actor, verb, target=None, extra=None):
    """Safely creates a notification with optional user preference checks."""
    if not recipient:
        return None

    prefs = getattr(recipient, "notification_preferences", None)
    if prefs:
        if verb in ["post_published", "seeker_post_published"] and not prefs.allow_global_posts:
            return None
        if verb == "commented" and not prefs.allow_comments:
            return None

    payload = {
        "recipient": recipient,
        "actor": actor,
        "verb": verb.capitalize(),
        "extra": extra or {},
    }

    if target is not None:
        payload.update({
            "target_content_type": f"{target._meta.app_label}.{target._meta.model_name}",
            "target_object_id": getattr(target, "id", None),
        })

    return Notification.objects.create(**payload)


# ----------------------------------------------------------------------
# PRE-SAVE HOOKS (Track old status)
# ----------------------------------------------------------------------
@receiver(pre_save, sender=Post)
def attach_prev_status_post(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._prev_status = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            instance._prev_status = "pending"
    else:
        instance._prev_status = "pending"


@receiver(pre_save, sender=SeekerPost)
def attach_prev_status_seeker(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._prev_status = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            instance._prev_status = "pending"
    else:
        instance._prev_status = "pending"


# ----------------------------------------------------------------------
# POST APPROVAL NOTIFICATIONS
# ----------------------------------------------------------------------
@receiver(post_save, sender=Post)
def notify_on_post_approval(sender, instance, created, **kwargs):
    prev = getattr(instance, "_prev_status", "pending")

    # ---- APPROVED ----
    if not created and prev != "approved" and instance.status == "approved":
        notify_post_approved(instance)

    # ---- REVERTED / UNAPPROVED ----
    elif not created and prev == "approved" and instance.status != "approved":
        notify_post_rejected(instance)

@receiver(post_save, sender=SeekerPost)

def notify_on_seeker_post_approval(sender, instance, created, **kwargs):
    """
    Trigger notifications when a seeker post is approved or rejected.
    """
    prev = getattr(instance, "_prev_status", "pending")

    # Approved
    if not created and prev != "approved" and instance.status == "approved":
        notify_seeker_approved(instance)

    # Rejected (reverted or rejected after approval)
    elif not created and prev == "approved" and instance.status != "approved":
        notify_seeker_rejected(instance)


# # ----------------------------------------------------------------------
# # DELETE CLEANUP
# # ----------------------------------------------------------------------
# @receiver(post_delete, sender=Post)
# def remove_post_from_board_on_delete(sender, instance, **kwargs):
#     remove_from_board(instance)


# @receiver(post_delete, sender=SeekerPost)
# def remove_seeker_from_board_on_delete(sender, instance, **kwargs):
#     remove_from_board(instance)


# ----------------------------------------------------------------------
# COMMENT NOTIFICATIONS
# ----------------------------------------------------------------------
@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if not created:
        return

    content_obj = instance.content_object
    if not content_obj:
        return

    if isinstance(content_obj, Post):
        if content_obj.status != "approved" or content_obj.author_id == instance.author_id:
            return

        extra = {
            "comment_excerpt": (instance.text[:120] if instance.text else ""),
            "post_title": getattr(content_obj, "product_name", "Untitled"),
        }

        create_notification_instance(
            recipient=content_obj.author,
            actor=instance.author,
            verb="Commented on your post",
            target=content_obj,
            extra=extra,
        )

    elif isinstance(content_obj, SeekerPost):
        if content_obj.status != "approved" or content_obj.author_id == instance.author_id:
            return

        extra = {
            "comment_excerpt": (instance.text[:120] if instance.text else ""),
            "post_title": getattr(content_obj, "title", "Untitled"),
        }

        create_notification_instance(
            recipient=content_obj.author,
            actor=instance.author,
            verb="Commented on your seeker post",
            target=content_obj,
            extra=extra,
        )
