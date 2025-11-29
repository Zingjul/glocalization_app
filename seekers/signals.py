# seekers/signals.py

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from notifications.hooks.seeker_notifications import (
    notify_seeker_approved,
    notify_seeker_rejected,
    notify_seeker_town_approved,
    notify_seeker_town_rejected,
)
from notifications.utils import push_to_board, remove_from_board

from .models import SeekerPost


@receiver(post_save, sender=SeekerPost)
def seeker_post_save_notifications(sender, instance: SeekerPost, created, **kwargs):
    """
    Handles sending notifications after a SeekerPost instance is saved.

    This signal checks for transient flags set on the instance to determine
    whether to send notifications for approval, rejection, town approval,
    or town rejection events.
    """
    # --- Post Approval / Rejection Notifications ---
    if hasattr(instance, "_notify_approval"):
        if instance._notify_approval:
            notify_seeker_approved(instance)
        else:
            notify_seeker_rejected(instance)

    # --- Town Approval Notification ---
    if hasattr(instance, "_town_approved"):
        notify_seeker_town_approved(instance, instance._town_approved)

    # --- Town Rejection Notification ---
    if hasattr(instance, "_town_rejected"):
        notify_seeker_town_rejected(instance, instance._town_rejected)


@receiver(pre_save, sender=SeekerPost)
def update_board_on_approval_change(sender, instance: SeekerPost, **kwargs):
    """
    Pushes a SeekerPost to the board when it's approved or removes
    it when its approval is revoked.

    This signal compares the `is_approved` status before and after the save
    to determine the correct action.
    """
    # If the instance is new (no primary key yet), it can't have a previous state.
    if instance.pk is None:
        return

    try:
        # Get the state of the object from the database before the save.
        previous_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Should not happen for an update, but handles a rare edge case.
        return

    was_approved = previous_instance.is_approved
    is_now_approved = instance.is_approved

    # Push to board if the post's status changes from not approved to approved.
    if not was_approved and is_now_approved:
        push_to_board("SeekersBoard", instance)
    # Remove from board if the post's status changes from approved to not approved.
    elif was_approved and not is_now_approved:
        remove_from_board("SeekersBoard", instance)


@receiver(post_delete, sender=SeekerPost)
def remove_from_board_on_delete(sender, instance: SeekerPost, **kwargs):
    """
    Ensures a SeekerPost is removed from the board when the
    instance is deleted from the database.
    """
    remove_from_board("SeekersBoard", instance)