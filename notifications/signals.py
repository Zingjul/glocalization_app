# -------------------------
# file: notifications/signals.py
# -------------------------
"""
Signals to create notifications for these triggers:
1) When a Post or SeekerPost transitions from 'pending' -> 'approved'
2) When a Post or SeekerPost receives a comment (only if approved)
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Notification
from posts.models import Post
from seekers.models import SeekerPost
from comment.models import Comment
# board
from board.models import Board
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

print("✅ Notifications signals loaded!")
# -------------------------
# HELPERS
def add_to_board(instance, title_field):  # 🔧 simplified (no summary)
    """Creates a Board entry for approved Post or SeekerPost."""
    content_type = ContentType.objects.get_for_model(instance.__class__)
    print(f"📋 add_to_board CALLED for {instance}")
    
    if Board.objects.filter(content_type=content_type, object_id=instance.id).exists():
        return  # Already exists

    title = getattr(instance, title_field, "Untitled")
    author_name = getattr(instance.author, "username", str(instance.author))
    print(f"✅ Creating board item for title={title} by {author_name}")

    Board.objects.create(
        title=title,
        author_name=author_name,
        content_object=instance,
    )

def remove_from_board(instance):  # 🔧 new helper
    """Removes an item from the board when unapproved or deleted."""
    content_type = ContentType.objects.get_for_model(instance.__class__)
    Board.objects.filter(content_type=content_type, object_id=instance.id).delete()

def create_notification_instance(recipient, actor, verb, target=None, extra=None):
    """Helper to safely create notifications, respecting prefs."""
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
        "verb": verb,
        "extra": extra or {},
    }

    if target is not None:
        payload.update({
            "target_content_type": f"{target._meta.app_label}.{target._meta.model_name}",
            "target_object_id": getattr(target, "id", None),
        })

    return Notification.objects.create(**payload)


# -------------------------
# PRE-SAVE HOOKS (track old status)
# -------------------------
@receiver(pre_save, sender=Post)
def attach_prev_status_post(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = sender.objects.get(pk=instance.pk)
            instance._prev_status = prev.status
        except sender.DoesNotExist:
            instance._prev_status = "pending"
    else:
        instance._prev_status = "pending"


@receiver(pre_save, sender=SeekerPost)
def attach_prev_status_seeker(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = sender.objects.get(pk=instance.pk)
            instance._prev_status = prev.status
        except sender.DoesNotExist:
            instance._prev_status = "pending"
    else:
        instance._prev_status = "pending"


# -------------------------
# POST APPROVAL NOTIFICATIONS
# -------------------------
@receiver(post_save, sender=Post)
def notify_on_post_approval(sender, instance, created, **kwargs):
    prev = getattr(instance, "_prev_status", "pending")
    print(f"🔥 Signal triggered for {instance} | prev={prev}, new={instance.status}")

    # --- APPROVED ---
    if not created and prev != "approved" and instance.status == "approved":
        add_to_board(instance, title_field="product_name")  # 🔧 fixed
        extra = {
            "post_title": getattr(instance, "product_name", "Untitled"),
            "post_summary": (instance.description[:120] if instance.description else ""),
            "author_id": instance.author_id,
        }

        recipients = User.objects.exclude(id=instance.author_id)
        for user in recipients.iterator():
            create_notification_instance(
                recipient=user,
                actor=instance.author,
                verb="post_published",
                target=instance,
                extra=extra,
            )

        # Notify followers too
        if hasattr(instance.author, "followers"):
            for sub in instance.author.followers.all().iterator():
                create_notification_instance(
                    recipient=sub.follower,
                    actor=instance.author,
                    verb="post_published_subscription",
                    target=instance,
                    extra=extra,
                )

    # --- REVERTED / UNAPPROVED ---
    elif not created and prev == "approved" and instance.status != "approved":
        remove_from_board(instance)  # 🔧 new behavior
              


@receiver(post_save, sender=SeekerPost)
def notify_on_seeker_post_approval(sender, instance, created, **kwargs):
    prev = getattr(instance, "_prev_status", "pending")

    # --- APPROVED ---
    if not created and prev != "approved" and instance.status == "approved":
        add_to_board(instance, title_field="title")  # 🔧 fixed
        extra = {
            "post_title": getattr(instance, "title", "Untitled"),
            "post_summary": (instance.description[:120] if instance.description else ""),
            "author_id": instance.author_id,
        }

        recipients = User.objects.exclude(id=instance.author_id)
        for user in recipients.iterator():
            create_notification_instance(
                recipient=user,
                actor=instance.author,
                verb="seeker_post_published",
                target=instance,
                extra=extra,
            )

        # Notify followers too
        if hasattr(instance.author, "followers"):
            for sub in instance.author.followers.all().iterator():
                create_notification_instance(
                    recipient=sub.follower,
                    actor=instance.author,
                    verb="seeker_post_published_subscription",
                    target=instance,
                    extra=extra,
                )

    # --- REVERTED / UNAPPROVED ---
    elif not created and prev == "approved" and instance.status != "approved":
        remove_from_board(instance)  # 🔧 new behavior


# -------------------------
# DELETE CLEANUP (auto remove from board)
# -------------------------
@receiver(post_delete, sender=Post)
def remove_post_from_board_on_delete(sender, instance, **kwargs):
    remove_from_board(instance)  # 🔧 new behavior


@receiver(post_delete, sender=SeekerPost)
def remove_seeker_from_board_on_delete(sender, instance, **kwargs):
    remove_from_board(instance)  # 🔧 new behavior

# -------------------------
# COMMENT NOTIFICATIONS
# -------------------------
@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if not created:
        return

    content_obj = instance.content_object

    # Case 1: Comment on Post
    if isinstance(content_obj, Post):
        if content_obj.status != "approved":
            return
        if content_obj.author_id == instance.author_id:
            return

        extra = {
            "comment_excerpt": (instance.text[:120] if instance.text else ""),
            "post_title": getattr(content_obj, "product_name", "Untitled"),
        }

        create_notification_instance(
            recipient=content_obj.author,
            actor=instance.author,
            verb="commented",
            target=content_obj,
            extra=extra,
        )

    # Case 2: Comment on SeekerPost
    elif isinstance(content_obj, SeekerPost):
        if content_obj.status != "approved":
            return
        if content_obj.author_id == instance.author_id:
            return

        extra = {
            "comment_excerpt": (instance.text[:120] if instance.text else ""),
            "post_title": getattr(content_obj, "title", "Untitled"),
        }

        create_notification_instance(
            recipient=content_obj.author,
            actor=instance.author,
            verb="commented",
            target=content_obj,
            extra=extra,
        )
