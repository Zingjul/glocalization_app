# board/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Board(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True, null=True)
    author_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    # Generic relation to Post or SeekerPost
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
