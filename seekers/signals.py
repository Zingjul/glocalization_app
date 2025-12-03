# seekers/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from board.models import Board
from .models import SeekerPost


@receiver(post_save, sender=SeekerPost)
def sync_seekerpost_board(sender, instance, created, **kwargs):
    """
    Automatically add/remove SeekerPost from SeekersBoard when approval status changes.
    Keeps the board in sync with the `is_approved` field.
    """
    try:
        board, _ = Board.objects.get_or_create(
            name="SeekersBoard",
            defaults={"description": "Board for all approved seeker requests."}
        )

        if getattr(instance, "is_approved", False):
            # ✅ Add approved seeker posts to the board
            if instance not in board.seeker_posts.all():
                board.add_item(instance)
                print(f"[INFO] Added approved SeekerPost {instance.pk} to SeekersBoard.")
        else:
            # 🧹 Remove unapproved seeker posts
            if instance in board.seeker_posts.all():
                board.seeker_posts.remove(instance)
                print(f"[INFO] Removed unapproved SeekerPost {instance.pk} from SeekersBoard.")

    except Exception as e:
        print(f"[WARN] Failed to sync SeekerPost {instance.pk}: {e}")
