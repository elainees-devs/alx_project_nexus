#jobsboard/notifications/models.py
from django.db import models
from django.conf import settings

# ---------------------------------------------------------
# Notification Model
# ---------------------------------------------------------
# Represents a notification sent to a user.
# - Stores title, message, optional link, type, and read status.
# - Supports filtering by user and read/unread status via database indexes.
# - Provides a string representation showing user, title, and read status.

class Notification(models.Model):
    NOTIFICATION_TYPE=[
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error')
    ]
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title=models.CharField(max_length=255)
    message=models.TextField()
    link=models.CharField(max_length=255, blank=True, null=True)
    is_read=models.BooleanField(default=False)
    type=models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE,
        default='info'
    )
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='idx_notifications_user'),
            models.Index(fields=['is_read'], name='idx_notifications_is_read'),
        ]

    def __str__(self):
        return f"{self.user} - {self.title} ({'Read' if self.is_read else 'Unread'})"