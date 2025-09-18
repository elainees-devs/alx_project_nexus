#jobboard/payments/serializers.py
from rest_framework import serializers
from .models import Payment
from django.contrib.auth import get_user_model

User = get_user_model()


# ------------------------
# Payment Serializer
# ------------------------
class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'user_email',
            'provider',
            'amount',
            'currency',
            'status',
            'transaction_id',
            'description',
            'metadata',
            'payment_type',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


# ------------------------
# Input serializer for initiating payment
# ------------------------
class PaymentInputSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=10, default="USD", required=False)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)
    payment_type = serializers.ChoiceField(choices=Payment.PAYMENT_TYPE_CHOICES, required=True)


# ------------------------
# Serializer for verifying payment
# ------------------------
class PaymentVerifySerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=255, required=True)

    def validate_transaction_id(self, value):
        if not Payment.objects.filter(transaction_id=value).exists():
            raise serializers.ValidationError("Payment with this transaction ID does not exist.")
        return value

    def validate(self, attrs):
        transaction_id = attrs.get("transaction_id")
        payment = Payment.objects.filter(transaction_id=transaction_id, provider="chapaa").first()
        if not payment:
            raise serializers.ValidationError("No matching Chapaa payment found.")
        attrs["payment_instance"] = payment
        return attrs
