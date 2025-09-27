from django.conf import settings
from notifications.models import Notification
from accounts.models import Follow

User = settings.AUTH_USER_MODEL

def notify_post_approved(post):
    """Notify relevant parties when a post is approved."""
    author = post.author

    # --- Notify the author ---
    Notification.objects.create(
        recipient=author,
        actor=None,
        verb=f"Your post '{post.product_name}' has been approved ✅",
        target_object_id=post.pk,
        target_content_type="post"
    )

    # --- Global notifications (optional, see scalability note) ---
    global_users = author.__class__.objects.exclude(pk=author.pk)
    Notification.objects.bulk_create([
        Notification(
            recipient=user,
            actor=author,
            verb=f"New post in {post.category.name}: {post.product_name} by {author.username}",
            target_object_id=post.pk,
            target_content_type="post"
        )
        for user in global_users
    ])

    # --- Notify followers of the author ---
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


def notify_post_rejected(post):
    """Notify the author if their post was rejected."""
    Notification.objects.create(
        recipient=post.author,
        actor=None,
        verb=f"Your post '{post.product_name}' was rejected 🚫",
        target_object_id=post.pk,
        target_content_type="post"
    )
