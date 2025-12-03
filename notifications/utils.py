from django.apps import apps
from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from board.models import Board

def remove_from_board(obj):
    """
    Safely remove a Post or SeekerPost instance from any board it was previously added to.
    Handles both 'posts' and 'seeker_posts'.
    """
    try:
        for board in Board.objects.all():
            removed = False

            # Remove from normal posts board
            if board.posts.filter(pk=obj.pk).exists():
                board.posts.remove(obj)
                removed = True

            # Remove from seekers board
            if board.seeker_posts.filter(pk=obj.pk).exists():
                board.seeker_posts.remove(obj)
                removed = True

            if removed:
                board.save()
                print(f"[INFO] Removed {obj.__class__.__name__} {obj.pk} from board '{board.name}'")

    except Exception as e:
        print(f"[WARN] Failed to remove {obj.__class__.__name__} {getattr(obj, 'pk', '?')} from board: {e}")
