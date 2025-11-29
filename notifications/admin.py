from django.contrib import admin
from .models import Notification, NotificationPreference, Board

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipient_display",
        "actor_display",
        "verb",
        "read",
        "created_at",
        "target_content_type",
        "target_object_id",
    )
    list_filter = ("verb", "read", "recipient")
    search_fields = ("recipient__username", "actor__username", "verb", "target_content_type")
    readonly_fields = ("created_at",)

    def recipient_display(self, obj):
        # Show Board name if recipient is a Board, else username
        if hasattr(obj.recipient, "name"):
            return f"Board: {obj.recipient.name}"
        return getattr(obj.recipient, "username", str(obj.recipient))
    recipient_display.short_description = "Recipient"

    def actor_display(self, obj):
        return getattr(obj.actor, "username", str(obj.actor)) if obj.actor else "-"
    actor_display.short_description = "Actor"

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "allow_global_posts", "allow_comments", "mode")
    search_fields = ("user__username", "user__email")

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)