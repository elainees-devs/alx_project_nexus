# jobsboard/payments/models.py
from django.db import models

from django.conf import settings
from django.utils import timezone
import uuid

User = settings.AUTH_USER_MODEL


class Payment(models.Model):
    PROVIDERS = [
        ("stripe", "Stripe"),
        ("chapaa", "Chapaa"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)  # holds provider raw response
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} [{self.provider}] ({self.status})"

