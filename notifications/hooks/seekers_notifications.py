"""
Handles notification creation for seeker request status changes.

This module sends notifications when a seeker request or related town
is approved or rejected. It ensures that:
- The seeker author is notified directly with a clickable link.
- The Seekers board is informed of all new approvals.
- Only followers of the author are notified about new seeker requests.
"""

from django.urls import reverse
from notifications.models import Notification
from accounts.models import Follow
from django.contrib.auth import get_user_model
from notifications.utils import remove_from_board  # ✅ import cleanup helper
from board.models import Board

User = get_user_model()


def get_seekers_board():
    """
    Retrieve or create the board that aggregates all approved seeker requests.
    """
    board, _ = Board.objects.get_or_create(
        name="SeekersBoard",
        defaults={"description": "Board for all approved seeker requests."}
    )
    return board


def get_seeker_url(seeker_post):
    """
    Return the absolute URL for a given seeker post instance.
    """
    try:
        return reverse("seeker_detail", args=[seeker_post.pk])
    except Exception:
        return None


def make_clickable_link(text, url):
    """
    Generate a clickable HTML anchor tag if a valid URL is available.
    """
    if not url:
        return text
    return f'<a href="{url}" style="color:#007bff;text-decoration:none;">{text}</a>'

def notify_seeker_approved(seeker_post):
    """
    Notify the author, add the seeker to SeekersBoard, and notify followers.
    """
    author = seeker_post.author
    seeker_url = get_seeker_url(seeker_post)
    title = seeker_post.title or "Untitled Request"
    clickable_title = make_clickable_link(title, seeker_url)

    # ✅ 1. Add seeker post to SeekersBoard (visible to everyone)
    seekers_board = get_seekers_board()
    seekers_board.add_item(seeker_post)

    Notification.objects.create(
        recipient=author,
        actor=None,
        verb=f"Your seeker request {clickable_title} has been approved.",
        target_object_id=seeker_post.pk,
        target_content_type="seekerpost",
        extra={"link": seeker_url},
    )

    # 🔔 3. Notify followers of the author
    follower_ids = list(
        Follow.objects.filter(following=author).values_list("follower_id", flat=True)
    )

    if follower_ids:
        followers = author.__class__.objects.filter(id__in=follower_ids)
        Notification.objects.bulk_create([
            Notification(
                recipient=follower,
                actor=author,
                verb=f"Someone you follow made a new seeker request, check it out: {clickable_title}.",
                target_object_id=seeker_post.pk,
                target_content_type="seekerpost",
                extra={"link": seeker_url},
            )
            for follower in followers
        ])

def notify_seeker_rejected(seeker_post):
    """
    Notify the author if their seeker request was rejected or reverted.
    """
    seeker_url = get_seeker_url(seeker_post)
    title = seeker_post.title or "Untitled Request"
    clickable_title = make_clickable_link(title, seeker_url)

    Notification.objects.create(
        recipient=seeker_post.author,
        actor=None,
        verb=f"Your seeker request {clickable_title} was rejected or reverted.",
        target_object_id=seeker_post.pk,
        target_content_type="seekerpost",
        extra={"link": seeker_url},
    )
        # 🧹 Remove from board (if it exists there)
    try:
        remove_from_board(seeker_post)
    except Exception as e:
        print(f"[WARN] Failed to remove post from board: {e}")


def notify_seeker_town_approved(seeker_post, town_name):
    """
    Notify the author when a town for their seeker request is approved.
    """
    seeker_url = get_seeker_url(seeker_post)
    title = seeker_post.title or "Untitled Request"
    clickable_title = make_clickable_link(title, seeker_url)

    Notification.objects.create(
        recipient=seeker_post.author,
        actor=None,
        verb=f"Your town '{town_name}' for seeker request {clickable_title} has been approved.",
        target_object_id=seeker_post.pk,
        target_content_type="seekerpost",
        extra={"link": seeker_url},
    )


def notify_seeker_town_rejected(seeker_post, town_name):
    """
    Notify the author when a town for their seeker request is rejected.
    """
    seeker_url = get_seeker_url(seeker_post)
    title = seeker_post.title or "Untitled Request"
    clickable_title = make_clickable_link(title, seeker_url)

    Notification.objects.create(
        recipient=seeker_post.author,
        actor=None,
        verb=f"Your town '{town_name}' for seeker request {clickable_title} was rejected. Please update.",
        target_object_id=seeker_post.pk,
        target_content_type="seekerpost",
        extra={"link": seeker_url},
    )
