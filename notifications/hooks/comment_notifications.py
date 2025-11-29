# notifications/hooks/comment_notifications.py
from notifications.models import Notification

def notify_comment_created(comment):
    target = comment.content_object
    author = getattr(target, "author", None)
    if author and author != comment.author:
        Notification.objects.create(
            recipient=author,
            actor=comment.author,
            verb=f"New comment on your {comment.content_type.model}: '{comment.text[:50]}...'",
            target_content_type=comment.content_type.model,
            target_object_id=comment.object_id,
            extra={"comment_id": comment.id}
        )