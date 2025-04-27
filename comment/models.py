from django.db import models
from django.conf import settings
from posts.models import Post  # Import your Post model

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # Connects comment to post
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Links comment to user
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the comment was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the comment was last updated
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )  # Enables nested comments/replies

    is_edited = models.BooleanField(default=False)  # Tracks if comment was modified
    is_spam = models.BooleanField(default=False)  # Optional flag for moderation/spam detection

    def save(self, *args, **kwargs):
        """Automatically marks comment as edited when updating the text."""
        if self.pk and self.text != Comment.objects.get(pk=self.pk).text:
            self.is_edited = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    class Meta:
        ordering = ['-created_at']  # Display comments in reverse chronological order
