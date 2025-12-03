# posts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from board.models import Board
from .models import Post


@receiver(post_save, sender=Post)
def sync_post_board(sender, instance, created, **kwargs):
    """
    Automatically add/remove Post from PostBoard when approval status changes.
    Keeps the board in sync with the `is_approved` field.
    """
    try:
        board, _ = Board.objects.get_or_create(
            name="PostBoard",
            defaults={"description": "Board for all approved posts."}
        )

        if getattr(instance, "is_approved", False):
            # ✅ Add approved posts to board
            if instance not in board.posts.all():
                board.add_item(instance)
                print(f"[INFO] Added approved Post {instance.pk} to PostBoard.")
        else:
            # 🧹 Remove unapproved posts
            if instance in board.posts.all():
                board.posts.remove(instance)
                print(f"[INFO] Removed unapproved Post {instance.pk} from PostBoard.")

    except Exception as e:
        print(f"[WARN] Failed to sync Post {instance.pk}: {e}")
