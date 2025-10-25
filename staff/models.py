from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class StaffBoardPost(models.Model):
    """For staff announcements, notes, or coordination."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="board_posts")
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "staff_board_post"
        ordering = ["-created_at"]
        verbose_name = "Staff Board Post"
        verbose_name_plural = "Staff Board Posts"

    def __str__(self):
        return f"{self.title} by {self.author}"


class AuditLog(models.Model):
    """Records moderation or staff actions."""
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    target_type = models.CharField(max_length=100, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "staff_audit_log"
        ordering = ["-created_at"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"{self.staff} — {self.action} — {self.created_at:%Y-%m-%d %H:%M}"
