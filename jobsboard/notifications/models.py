#jobsboard/notifications/models.py
from django.db import models
from django.conf import settings

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
    messages=models.TextField()
    link=models.CharField(max_length=255, blank=True, null=True)
    is_read=models.BooleanField(default=False)
    type=models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE,
        default='info'
    )
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.title} ({'Read' if self.is_read else 'Unread'})"

