# media_app/models.py
import os
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = settings.AUTH_USER_MODEL


def media_upload_path(instance, filename):
    """
    Save files under:
        <app_label>/<images|videos>/user_<owner_id>/<filename>
    Example:
        seekers/images/user_5/pic.png
        posts/videos/user_7/clip.mp4
        person/images/user_3/avatar.jpg
    Ensures per-app, per-user organization with safe fallback.
    """
    folder = "videos" if instance.file_type == "video" else "images"

    # detect related object's app label safely
    related_obj = instance.content_object
    app_label = related_obj._meta.app_label if related_obj else "media"

    # user folder (fallback if no owner yet)
    owner_id = instance.owner_id or getattr(instance.owner, "id", None) or "anonymous"

    return os.path.join(app_label, folder, f"user_{owner_id}", filename)


class MediaFile(models.Model):
    # Who uploaded the file (optional, for better organization)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_media"
    )

    # Generic relation to any model (Post, Seeker, Profile, Comment, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # File fields
    file = models.FileField(upload_to=media_upload_path)
    FILE_CHOICES = (("image", "Image"), ("video", "Video"))
    file_type = models.CharField(max_length=10, choices=FILE_CHOICES)
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_public = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        owner = getattr(self.owner, "username", "anonymous")
        return f"{self.file.name} ({self.file_type}) by {owner}"
