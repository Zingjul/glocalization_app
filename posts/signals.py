# posts/signals.py

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from notifications.hooks.post_notifications import (
    notify_post_approved,
    notify_post_rejected,
)
from notifications.utils import push_to_board, remove_from_board

from .models import Post


@receiver(post_save, sender=Post)
def post_save_handler(sender, instance: Post, created, **kwargs):
    """
    Handles actions after a Post instance is saved.

    - On creation: Pushes the post to the board if it's already approved.
    - On any save: Sends approval/rejection notifications based on transient flags.
    """
    # --- Push to board on creation ---
    if created and instance.is_approved:
        push_to_board("PostBoard", instance)

    # --- Approval / Rejection Notifications ---
    if hasattr(instance, "_notify_approval"):
        if instance._notify_approval:
            notify_post_approved(instance)
        else:
            notify_post_rejected(instance)


@receiver(pre_save, sender=Post)
def update_board_on_approval_change(sender, instance: Post, **kwargs):
    """
    Updates the board when an existing Post's approval status changes.

    Compares the `is_approved` status before and after the save to determine
    whether to push to or remove from the board.
    """
    # This signal only handles updates, not new instances.
    if instance.pk is None:
        return

    try:
        # Get the state of the object from the database before the save.
        previous_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # This should not happen for an update, but handles an edge case.
        return

    was_approved = previous_instance.is_approved
    is_now_approved = instance.is_approved

    # Push if changing from not approved to approved.
    if not was_approved and is_now_approved:
        push_to_board("PostBoard", instance)
    # Remove if changing from approved to not approved.
    elif was_approved and not is_now_approved:
        remove_from_board("PostBoard", instance)


@receiver(post_delete, sender=Post)
def remove_from_board_on_delete(sender, instance: Post, **kwargs):
    """
    Ensures a Post is removed from the board when its instance is deleted.
    """
    remove_from_board("PostBoard", instance)