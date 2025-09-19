# jobsboard/request_logs/models.py
from django.db import models
from django.conf import settings


class RequestLog(models.Model):
    HTTP_METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='request_logs'
    )
    ip_address = models.CharField(max_length=45)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=HTTP_METHOD_CHOICES)
    status_code = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'request_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"
