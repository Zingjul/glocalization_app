# What this file does
# Centralizes notification logic for post approval and rejection events.
# Sends notifications to:
# The post author (always).
# All users except the author (global notification).
# All followers of the author.
# Functions:
# notify_post_approved(post):

# Notifies the author that their post was approved.
# Notifies all other users about the new post (global notification).
# Notifies all followers of the author about the new post.
# notify_post_rejected(post):

# Notifies the author that their post was rejected.
from django.conf import settings
from notifications.models import Board, Notification
from accounts.models import Follow

User = settings.AUTH_USER_MODEL

def notify_post_approved(post):
    author = post.author
    # Notify the author
    Notification.objects.create(
        recipient=author,
        actor=None,
        verb=f"Your post '{post.product_name}' has been approved ✅",
        target_content_type="post",
        target_object_id=post.pk
    )

    # Notify the Board
    board = Board.objects.filter(name="PostBoard").first()
    if board:
        Notification.objects.create(
            recipient=board,
            actor=author,
            verb=f"New post: {post.product_name} by {author.username}",
            target_content_type="post",
            target_object_id=post.pk
        )

    # Notify followers of the author
    follower_ids = Follow.objects.filter(following=author).values_list("follower_id", flat=True)
    followers = author.__class__.objects.filter(id__in=follower_ids)
    Notification.objects.bulk_create([
        Notification(
            recipient=follower,
            actor=author,
            verb=f"{author.username} published a new post: {post.product_name}",
            target_object_id=post.pk,
            target_content_type="post"
        )
        for follower in followers
    ])
# 
def notify_post_rejected(post):
    """Notify the author if their post was rejected."""
    Notification.objects.create(
        recipient=post.author,
        actor=None,
        verb=f"Your post '{post.product_name}' was rejected 🚫",
        target_object_id=post.pk,
        target_content_type="post"
    )
