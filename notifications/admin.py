# -------------------------
# file: notifications/admin.py
# -------------------------
from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "actor", "verb", "read", "created_at")
    list_filter = ("verb", "read")
    search_fields = ("recipient__username", "actor__username", "verb")

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "allow_global_posts", "allow_comments", "mode")

