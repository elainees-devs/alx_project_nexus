from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment

User = get_user_model()


# ---------------------------------------------------------
# PaymentSerializer
# ---------------------------------------------------------
# Serializer for the Payment model.
# - Used for listing and retrieving payment details.
# - Includes read-only fields for ID, timestamps, and user.
# - Provides the user's email via a read-only field for convenience.
class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'user_email',
            'amount',
            'currency',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'tx_ref',
            'callback_url',
            'return_url',
            'customization',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ---------------------------------------------------------
# PaymentInputSerializer
# ---------------------------------------------------------
# Serializer for initiating a new payment.
# - Validates input fields required for creating a payment transaction.
# - Includes amount, currency, user details, transaction reference, URLs, and customization.
class PaymentInputSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=10, default="ETB")
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    tx_ref = serializers.CharField(required=True)
    callback_url = serializers.URLField(required=True)
    return_url = serializers.URLField(required=True)
    customization = serializers.JSONField(required=True)


# ---------------------------------------------------------
# PaymentVerifySerializer
# ---------------------------------------------------------
# Serializer for verifying an existing payment.
# - Validates that the provided transaction reference exists.
# - Attaches the corresponding Payment instance to validated data for further processing.
class PaymentVerifySerializer(serializers.Serializer):
    tx_ref = serializers.CharField(max_length=100, required=True)

    def validate_tx_ref(self, value):
        if not Payment.objects.filter(tx_ref=value).exists():
            raise serializers.ValidationError("Payment with this tx_ref does not exist.")
        return value

    def validate(self, attrs):
        tx_ref = attrs.get("tx_ref")
        payment = Payment.objects.filter(tx_ref=tx_ref).first()
        if not payment:
            raise serializers.ValidationError("No matching payment found.")
        attrs["payment_instance"] = payment
        return attrs
