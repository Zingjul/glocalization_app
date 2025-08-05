from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.conf import settings
from django.urls import reverse

class Comment(models.Model):
    # 🔗 Generic relation to any model (e.g. Post, SeekerPost, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')  # Renamed from 'post' to reflect generality

    # 👤 Comment metadata
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 🧵 For threaded discussions
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    # 📌 Additional flags
    is_edited = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk and self.text != Comment.objects.get(pk=self.pk).text:
            self.is_edited = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.content_type.app_label}.{self.content_type.model} #{self.object_id}"

    def get_absolute_url(self):
        return reverse('comment_detail', kwargs={'pk': self.pk})

    @property
    def is_root(self):
        return self.parent is None

    class Meta:
        ordering = ['-created_at']
