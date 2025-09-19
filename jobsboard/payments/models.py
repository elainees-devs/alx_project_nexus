# jobsboard/payments/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

User = settings.AUTH_USER_MODEL


class Payment(models.Model):
    PROVIDERS = [
        ("chapaa", "Chapaa"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    PAYMENT_TYPE_CHOICES = [
        ("job_posting", "Job Posting"),
        ("premium_subscription", "Premium Subscription"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES, default="job_posting")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='idx_payments_user_id'),
            models.Index(fields=['status'], name='idx_payments_status'),
            models.Index(fields=['provider'], name='idx_payments_provider'),
        ]