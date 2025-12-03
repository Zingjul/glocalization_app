# file: notifications/serializers.py
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "actor",
            "verb",
            "read",
            "created_at",
            "extra",
            "link",
        ]

    def get_actor(self, obj):
        if obj.actor:
            return obj.actor.username
        return "System"

    def get_link(self, obj):
        # Prefer the explicit link in 'extra' if provided by the hook
        if obj.extra and "link" in obj.extra:
            return obj.extra["link"]

        # Otherwise, try building it from target info
        if obj.target_content_type == "post" and obj.target_object_id:
            from django.urls import reverse
            try:
                return reverse("post_detail", args=[obj.target_object_id])
            except Exception:
                pass

        return None
