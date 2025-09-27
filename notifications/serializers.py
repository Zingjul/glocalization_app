# -------------------------
# file: notifications/serializers.py
# -------------------------
from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for exposing notifications to frontend clients."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "actor",
            "verb",
            "target_content_type",
            "target_object_id",
            "extra",
            "read",
            "created_at",
        ]
        read_only_fields = ["recipient", "created_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for reading/updating notification preferences."""

    class Meta:
        model = NotificationPreference
        fields = "__all__"
        read_only_fields = ["user"]
