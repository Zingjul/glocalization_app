"""
Handles notification creation for post status changes.

This module sends structured, clickable notifications when a post is approved or rejected.
It automatically:
- Notifies the post author with a clickable link to their post.
- Notifies the admin board (not general users) when a post is approved.
- Notifies only followers of the author about new approved posts.
"""

from django.conf import settings
from django.urls import reverse
from notifications.models import Notification
from accounts.models import Follow
from notifications.utils import remove_from_board  # ✅ import cleanup helper
from board.models import Board
User = settings.AUTH_USER_MODEL


def get_post_url(post):
    """Return the absolute URL for a given post instance."""
    try:
        return reverse("post_detail", args=[post.pk])
    except Exception:
        return None


def make_clickable_link(text, url):
    """Return a clickable HTML link if URL exists."""
    if not url:
        return text
    return f'<a href="{url}" style="color:#007bff;text-decoration:none;">{text}</a>'


def notify_post_approved(post):
    """
    Notify only the author and followers when a post is approved.
    Also adds the post to the central 'PostBoard' for public display.
    """
    author = post.author
    post_url = get_post_url(post)
    product_name = post.product_name or "Untitled Post"
    clickable_title = make_clickable_link(product_name, post_url)

    # 1️⃣ Add the approved post to the public board
    board = Board.objects.filter(name="PostBoard").first()
    if board:
        board.add_item(post)

    # 2️⃣ Notify the author
    Notification.objects.create(
        recipient=author,
        actor=None,
        verb=f"Your post {clickable_title} has been approved",
        target_content_type="post",
        target_object_id=post.pk,
        extra={"link": post_url},
    )

    # 3️⃣ Notify followers of the author
    follower_ids = list(
        Follow.objects.filter(following=author).values_list("follower_id", flat=True)
    )

    if follower_ids:
        followers = author.__class__.objects.filter(id__in=follower_ids)
        Notification.objects.bulk_create([
            Notification(
                recipient=follower,
                actor=author,
                verb=f"{author.username} made a new post: {clickable_title}.",
                target_object_id=post.pk,
                target_content_type="post",
                extra={"link": post_url},
            )
            for follower in followers
        ])

def notify_post_rejected(post):
    """
    Notify the post author if their post was rejected or unapproved,
    and ensure it’s removed from the Board.
    """
    post_url = get_post_url(post)
    product_name = post.product_name or "Untitled Post"
    clickable_title = make_clickable_link(product_name, post_url)

    # 📨 Notify the author
    Notification.objects.create(
        recipient=post.author,
        actor=None,
        verb=f"Your post {clickable_title} was rejected or reverted.",
        target_content_type="post",
        target_object_id=post.pk,
        extra={"link": post_url},
    )
    # 🧹 Remove from board (if it exists there)
    try:
        remove_from_board(post)
    except Exception as e:
        print(f"[WARN] Failed to remove post from board: {e}")
