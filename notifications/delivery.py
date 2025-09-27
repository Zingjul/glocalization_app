# -------------------------
# file: notifications/delivery.py
# -------------------------
"""
Simple delivery helper functions. In production, replace with Celery tasks
and bulk/batched processing to avoid N+1 operations.
"""
from django.utils import timezone
from .models import Notification


def mark_delivered(notification: Notification):
    """Mark a notification as delivered (useful if you track push delivery timestamps)."""
    notification.delivered_at = timezone.now()
    notification.save(update_fields=["delivered_at"]) if hasattr(notification, "delivered_at") else None

