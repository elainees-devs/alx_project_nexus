# payments/models.py
from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL

# ---------------------------------------------------------
# Payment Model
# ---------------------------------------------------------
# Represents a payment transaction made by a user.
# - Stores payment details such as amount, currency, user info, and transaction reference.
# - Supports callback and return URLs for payment gateway integration.
# - Includes a JSON field for customization (title & description).
# - Orders records by creation date descending for easy access to recent payments.
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    
    # Payload fields
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="ETB")
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    tx_ref = models.CharField(max_length=255, unique=True, default=uuid.uuid4)  # generate unique default
    callback_url = models.URLField(blank=True, null=True, default="https://example.com/callback")
    return_url = models.URLField()
    customization = models.JSONField(default=dict)  # stores title & description

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.tx_ref}"
