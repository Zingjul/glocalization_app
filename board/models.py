# board/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from posts.models import Post
from seekers.models import SeekerPost


class Board(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True, null=True)
    author_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    posts = models.ManyToManyField("posts.Post", blank=True, related_name="boards")
    seeker_posts = models.ManyToManyField(SeekerPost, related_name="boards", blank=True)

    # Generic relation to Post or SeekerPost
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}"

    # ✅ NEW HELPER METHOD
    def add_item(self, obj):
        """
        Add a Post or SeekerPost instance to the correct relation.
        """
        from posts.models import Post
        from seekers.models import SeekerPost

        if isinstance(obj, Post):
            self.posts.add(obj)
        elif isinstance(obj, SeekerPost):
            self.seeker_posts.add(obj)
        else:
            raise TypeError(f"Unsupported object type: {type(obj).__name__}")

        self.save()
        print(f"[INFO] Added {obj.__class__.__name__} {obj.pk} to board '{self.name}'")
