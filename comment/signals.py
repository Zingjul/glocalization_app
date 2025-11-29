# comment/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from notifications.hooks.comment_notifications import notify_comment_created

@receiver(post_save, sender=Comment)
def comment_notification_signal(sender, instance, created, **kwargs):
    if created:
        notify_comment_created(instance)